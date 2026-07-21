import os
import sys
import json
import queue
import threading
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Import constants and core logic
import constants
from converter import convert_to_md

class MarkItDownApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Load user configuration
        self.load_config()
        
        # Configure window and custom base background
        self.title(f"{constants.APP_NAME} (v{constants.APP_VERSION})")
        self.geometry(f"{constants.DEFAULT_WINDOW_WIDTH}x{constants.DEFAULT_WINDOW_HEIGHT}")
        self.minsize(600, 450)
        self.configure(fg_color=constants.COLOR_MAIN_BG)
        
        # Set theme from config
        self.apply_theme(self.config.get("theme", constants.DEFAULT_THEME))
        
        # Configure layout (sidebar and main panel)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Setup queue for logs
        self.log_queue = queue.Queue()
        self.is_converting = False
        
        # Draw UI
        self.create_sidebar()
        self.create_main_panel()
        
        # Start queue polling
        self.after(100, self.poll_log_queue)
        
    def load_config(self):
        """Loads configuration from ~/.markitdown-gui/config.json"""
        self.config = {
            "theme": constants.DEFAULT_THEME,
            "export_dir": str(Path.home() / "Documents")
        }
        
        try:
            if constants.CONFIG_FILE_PATH.exists():
                with open(constants.CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        self.config.update(loaded)
        except Exception as e:
            # Fallback if config is corrupt
            print(f"[Config] Error loading config: {e}")
            
    def save_config(self):
        """Saves current configuration to ~/.markitdown-gui/config.json"""
        try:
            constants.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(constants.CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            self.write_log_direct(f"[ERROR] Failed to save config: {e}\n")
            
    def apply_theme(self, theme_name):
        """Applies customtkinter theme mode"""
        if theme_name in constants.THEMES:
            ctk.set_appearance_mode(theme_name)
            self.config["theme"] = theme_name
            
    def create_sidebar(self):
        # Sidebar Frame with border
        self.sidebar_frame = ctk.CTkFrame(
            self, 
            width=220, 
            corner_radius=0,
            fg_color=constants.COLOR_SIDEBAR_BG,
            border_width=1,
            border_color=constants.COLOR_BORDER
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        # Logo Label
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="MarkItDown", 
            font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
            text_color=constants.COLOR_TITLE
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(24, 6))
        
        self.subtitle_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Desktop Converter",
            font=ctk.CTkFont(family="Inter", size=12, slant="italic"),
            text_color=constants.COLOR_MUTED
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 24))
        
        # Theme Section
        self.theme_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Appearance Mode:", 
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color=constants.COLOR_TITLE,
            anchor="w"
        )
        self.theme_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.theme_optionmenu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=constants.THEMES,
            command=self.change_theme_event,
            fg_color=constants.COLOR_SECONDARY,
            button_color=constants.COLOR_SECONDARY,
            button_hover_color=constants.COLOR_SECONDARY_HOVER,
            dropdown_fg_color=constants.COLOR_ENTRY_BG,
            dropdown_hover_color=constants.COLOR_SECONDARY_HOVER,
            corner_radius=constants.RADIUS_BUTTON
        )
        self.theme_optionmenu.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.theme_optionmenu.set(self.config.get("theme", constants.DEFAULT_THEME))
        
        # Export Dir Frame
        self.export_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.export_frame.grid(row=5, column=0, padx=10, pady=20, sticky="ew")
        self.export_frame.grid_columnconfigure(0, weight=1)
        
        self.export_label_title = ctk.CTkLabel(
            self.export_frame, 
            text="Export Folder:", 
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color=constants.COLOR_TITLE,
            anchor="w"
        )
        self.export_label_title.grid(row=0, column=0, padx=10, pady=0, sticky="w")
        
        # Label to show selected export folder path
        self.export_path_label = ctk.CTkLabel(
            self.export_frame,
            text=self.truncate_path(self.config.get("export_dir")),
            font=ctk.CTkFont(family="Inter", size=11),
            text_color=constants.COLOR_MUTED,
            anchor="w",
            justify="left",
            wraplength=180
        )
        self.export_path_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.select_export_btn = ctk.CTkButton(
            self.export_frame,
            text="Change Folder",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            command=self.select_export_folder_event,
            fg_color=constants.COLOR_SECONDARY,
            hover_color=constants.COLOR_SECONDARY_HOVER,
            corner_radius=constants.RADIUS_BUTTON
        )
        self.select_export_btn.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
    def create_main_panel(self):
        # Main Panel Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=24, pady=24)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)
        
        # Top Heading
        self.heading_label = ctk.CTkLabel(
            self.main_frame,
            text="Convert Files to Markdown",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color=constants.COLOR_TITLE,
            anchor="w"
        )
        self.heading_label.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Select Files Button Frame
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.grid(row=1, column=0, pady=(0, 15), sticky="ew")
        self.btn_frame.grid_columnconfigure(1, weight=1)
        
        self.select_files_btn = ctk.CTkButton(
            self.btn_frame,
            text="Select Files to Convert",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            height=42,
            command=self.select_files_and_convert_event,
            fg_color=constants.COLOR_PRIMARY,
            hover_color=constants.COLOR_PRIMARY_HOVER,
            corner_radius=constants.RADIUS_BUTTON
        )
        self.select_files_btn.grid(row=0, column=0, sticky="w")
        
        self.clear_logs_btn = ctk.CTkButton(
            self.btn_frame,
            text="Clear Logs",
            width=100,
            height=32,
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color=constants.COLOR_SECONDARY,
            hover_color=constants.COLOR_SECONDARY_HOVER,
            command=self.clear_logs_event,
            corner_radius=constants.RADIUS_BUTTON
        )
        self.clear_logs_btn.grid(row=0, column=2, sticky="e")
        
        # URL Input Frame (Nested Premium Card layout)
        self.url_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color=constants.COLOR_ENTRY_BG,
            corner_radius=constants.RADIUS_PANEL,
            border_width=1,
            border_color=constants.COLOR_BORDER
        )
        self.url_frame.grid(row=2, column=0, pady=(0, 15), sticky="ew")
        self.url_frame.grid_columnconfigure(0, weight=1)
        
        self.url_inner = ctk.CTkFrame(self.url_frame, fg_color="transparent")
        self.url_inner.grid(row=0, column=0, padx=12, pady=12, sticky="ew")
        self.url_inner.grid_columnconfigure(0, weight=1)
        
        self.url_entry = ctk.CTkEntry(
            self.url_inner,
            placeholder_text="Enter YouTube URL, Wikipedia URL, or website URL here...",
            font=ctk.CTkFont(family="Inter", size=12),
            height=38,
            fg_color=constants.COLOR_ENTRY_BG,
            border_color=constants.COLOR_BORDER,
            border_width=1,
            corner_radius=constants.RADIUS_INPUT
        )
        self.url_entry.grid(row=0, column=0, padx=(0, 12), sticky="ew")
        
        self.convert_url_btn = ctk.CTkButton(
            self.url_inner,
            text="Convert URL",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            height=38,
            width=120,
            command=self.convert_url_event,
            fg_color=constants.COLOR_PRIMARY,
            hover_color=constants.COLOR_PRIMARY_HOVER,
            corner_radius=constants.RADIUS_BUTTON
        )
        self.convert_url_btn.grid(row=0, column=1, sticky="e")
        
        # Log Text Box styled like a modern terminal overlay
        self.log_textbox = ctk.CTkTextbox(
            self.main_frame, 
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=constants.COLOR_TEXTBOX_BG,
            text_color=constants.COLOR_TEXTBOX_TEXT,
            border_color=constants.COLOR_BORDER,
            border_width=1,
            corner_radius=constants.RADIUS_PANEL
        )
        self.log_textbox.grid(row=3, column=0, sticky="nsew")
        self.log_textbox.configure(state="disabled")
        
        self.write_log_direct("Ready. Select files or enter a URL to start converting...\n")
        
    def truncate_path(self, path_str):
        if not path_str:
            return "Not Selected"
        path = Path(path_str)
        parts = path.parts
        if len(parts) > 2:
            return f".../{parts[-2]}/{parts[-1]}"
        return path_str
        
    def change_theme_event(self, new_theme):
        self.apply_theme(new_theme)
        self.save_config()
        self.write_log_direct(f"Appearance theme changed to: {new_theme}\n")
        
    def select_export_folder_event(self):
        folder = filedialog.askdirectory(
            initialdir=self.config.get("export_dir"),
            title="Select Output Directory for Markdown Files"
        )
        if folder:
            self.config["export_dir"] = folder
            self.export_path_label.configure(text=self.truncate_path(folder))
            self.save_config()
            self.write_log_direct(f"Export directory updated to: {folder}\n")
            
    def clear_logs_event(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        
    def write_log_direct(self, message):
        """Helper to write logs directly when on main thread"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message)
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
        
    def queue_log(self, message):
        """Thread-safe logging by writing to the queue"""
        self.log_queue.put(message)
        
    def poll_log_queue(self):
        """Periodic check for log messages from background thread"""
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.write_log_direct(msg)
                self.log_queue.task_done()
        except queue.Empty:
            pass
            
        # Re-schedule the polling
        self.after(100, self.poll_log_queue)
        
    def select_files_and_convert_event(self):
        if self.is_converting:
            messagebox.showwarning("Busy", "A conversion task is currently running. Please wait.")
            return
            
        files = filedialog.askopenfilenames(
            title="Select Files to Convert",
            filetypes=constants.FILE_TYPES
        )
        
        if not files:
            return
            
        self.start_conversion(files)
        
    def convert_url_event(self):
        if self.is_converting:
            messagebox.showwarning("Busy", "A conversion task is currently running. Please wait.")
            return
            
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Empty URL", "Please enter a valid URL.")
            return
            
        if not url.startswith(("http://", "https://")):
            messagebox.showwarning("Invalid URL", "URL must start with http:// or https://")
            return
            
        # Start conversion and clear entry
        self.start_conversion([url])
        self.url_entry.delete(0, "end")
        
    def start_conversion(self, items):
        export_dir = self.config.get("export_dir")
        if not export_dir or not os.path.exists(export_dir):
            # Prompt user to choose export folder
            export_dir = filedialog.askdirectory(title="Please select export directory first")
            if not export_dir:
                self.write_log_direct("[WARNING] Conversion cancelled: No export folder selected.\n")
                return
            self.config["export_dir"] = export_dir
            self.export_path_label.configure(text=self.truncate_path(export_dir))
            self.save_config()
            
        # Start conversion in background thread
        self.is_converting = True
        self.select_files_btn.configure(state="disabled")
        self.convert_url_btn.configure(state="disabled")
        self.theme_optionmenu.configure(state="disabled")
        self.select_export_btn.configure(state="disabled")
        
        # Clear textbox or add separator
        self.write_log_direct("\n" + "="*50 + "\nStarting new batch conversion...\n")
        
        thread = threading.Thread(
            target=self.run_conversion_thread,
            args=(items, export_dir),
            daemon=True
        )
        thread.start()
        
    def run_conversion_thread(self, items, export_dir):
        try:
            success, total = convert_to_md(items, export_dir, log_callback=self.queue_log)
            # Log summary
            self.queue_log(f"Batch process completed. Successfully converted {success}/{total} items.\n")
        except Exception as e:
            self.queue_log(f"[FATAL ERROR] An unexpected error occurred: {e}\n")
        finally:
            self.is_converting = False
            self.after(0, self.reset_ui_state)
            
    def reset_ui_state(self):
        self.select_files_btn.configure(state="normal")
        self.convert_url_btn.configure(state="normal")
        self.theme_optionmenu.configure(state="normal")
        self.select_export_btn.configure(state="normal")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser(description="MarkItDown Desktop CLI Mode")
        parser.add_argument("files", nargs="+", help="Files to convert")
        parser.add_argument("-o", "--output", required=True, help="Output directory")
        args = parser.parse_args()
        
        print(f"Running in CLI mode. Output folder: {args.output}")
        success, total = convert_to_md(args.files, args.output, log_callback=lambda msg: print(msg, end=""))
        print(f"\nDone. Successfully converted {success}/{total} files.")
        sys.exit(0 if success == total else 1)
    else:
        app = MarkItDownApp()
        app.mainloop()

import os
from pathlib import Path

# Application Metadata
APP_NAME = "MarkItDown GUI"
APP_VERSION = "1.0.0"
DEFAULT_WINDOW_WIDTH = 850
DEFAULT_WINDOW_HEIGHT = 600

# Settings & Configuration Path
CONFIG_DIR = Path.home() / ".markitdown-gui"
CONFIG_FILE_PATH = CONFIG_DIR / "config.json"

# File extensions supported by MarkItDown
SUPPORTED_EXTENSIONS = [
    # Document formats
    ".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".csv",
    # Web / Text formats
    ".html", ".htm", ".txt", ".json", ".xml", ".md",
    # Other / Ebook / Archive
    ".epub", ".zip", ".msg",
    # Images (EXIF + OCR)
    ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif",
    # Audio (EXIF + Transcription)
    ".mp3", ".wav", ".m4a", ".flac", ".ogg"
]

# File Dialog Filetypes
FILE_TYPES = [
    ("All Supported Files", ";".join(f"*{ext}" for ext in SUPPORTED_EXTENSIONS)),
    ("PDF Documents", "*.pdf"),
    ("Word Documents", "*.docx"),
    ("PowerPoint Presentations", "*.pptx"),
    ("Excel Spreadsheets", "*.xlsx;*.xls"),
    ("CSV files", "*.csv"),
    ("HTML files", "*.html;*.htm"),
    ("Text files", "*.txt;*.json;*.xml;*.md"),
    ("Ebook files", "*.epub"),
    ("Outlook Msg files", "*.msg"),
    ("Zip archives", "*.zip"),
    ("Images", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.gif"),
    ("Audio", "*.mp3;*.wav;*.m4a;*.flac;*.ogg"),
    ("All Files", "*.*")
]

# UI Appearance Constants
THEMES = ["System", "Dark", "Light"]
DEFAULT_THEME = "System"
COLOR_THEMES = ["blue", "green", "dark-blue"]
DEFAULT_COLOR_THEME = "blue"

# Premium Design Tokens (Light, Dark Mode Tuples)
COLOR_SIDEBAR_BG = ("#f5f6fa", "#111318")
COLOR_MAIN_BG = ("#ffffff", "#16181f")

COLOR_PRIMARY = ("#6c5ce7", "#6c5ce7")  # Vibrant modern violet
COLOR_PRIMARY_HOVER = ("#81ecec", "#5849d4")  # Dynamic hover violet/teal tint

COLOR_SECONDARY = ("#747d8c", "#20242e")  # Muted slate
COLOR_SECONDARY_HOVER = ("#a4b0be", "#2f3542")

COLOR_TEXTBOX_BG = ("#f1f2f6", "#0c0d12")  # Code/terminal editor background
COLOR_TEXTBOX_TEXT = ("#2f3542", "#e1b12c")  # Warm high-contrast text

COLOR_ENTRY_BG = ("#ffffff", "#1b1e26")
COLOR_BORDER = ("#ced6e0", "#2c313f")

COLOR_TITLE = ("#2f3542", "#f5f6fa")
COLOR_MUTED = ("#747d8c", "#a4b0be")

# Corner Radii
RADIUS_BUTTON = 10
RADIUS_PANEL = 16
RADIUS_INPUT = 8


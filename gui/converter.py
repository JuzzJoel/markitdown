import os
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from markitdown import MarkItDown, MarkItDownException

def get_safe_filename(source, title=None):
    if source.startswith(("http://", "https://")):
        parsed = urlparse(source)
        # Try to get the last segment of path
        path_segment = parsed.path.strip("/").split("/")[-1]
        if not path_segment or path_segment == "watch":
            queries = parse_qs(parsed.query)
            if "v" in queries:
                filename = f"youtube_{queries['v'][0]}"
            else:
                filename = parsed.netloc.replace(".", "_")
        else:
            filename = path_segment
    else:
        filename = Path(source).stem

    # Clean characters that are invalid in Windows filenames
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    if title:
        clean_title = re.sub(r'[\\/*?:"<>|]', "_", title)
        if len(clean_title) < 50:
            filename = clean_title
            
    return filename + ".md"

def convert_to_md(file_paths, output_dir, log_callback=None):
    """
    Converts a list of files or URLs to markdown and saves them in the output directory.
    
    Parameters:
    - file_paths: List of file paths or URLs to convert.
    - output_dir: Target directory for .md files.
    - log_callback: Callable that takes a string message to log progress.
    
    Returns:
    - Tuple: (success_count, total_count)
    """
    if log_callback is None:
        log_callback = lambda msg: print(msg)
        
    log_callback("Initializing MarkItDown converter...\n")
    try:
        md = MarkItDown()
    except Exception as e:
        log_callback(f"[ERROR] Failed to initialize MarkItDown: {e}\n")
        return 0, len(file_paths)
        
    os.makedirs(output_dir, exist_ok=True)
    success_count = 0
    total_count = len(file_paths)
    
    for path_str in file_paths:
        is_url = path_str.startswith(("http://", "https://"))
        display_name = path_str if is_url else Path(path_str).name
        
        log_callback(f"\nProcessing: {display_name}\n")
        
        try:
            if not is_url:
                path = Path(path_str)
                if not path.exists():
                    log_callback(f"[ERROR] File does not exist: {path_str}\n")
                    continue
            
            # Perform conversion using markitdown
            result = md.convert(path_str)
            
            # Formulate safe output file name
            out_filename = get_safe_filename(path_str, getattr(result, 'title', None))
            out_path = Path(output_dir) / out_filename
            
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(result.markdown)
                
            log_callback(f"[SUCCESS] Converted and saved: {out_filename}\n")
            success_count += 1
            
        except MarkItDownException as e:
            log_callback(f"[ERROR] MarkItDown conversion failed for {display_name}: {e}\n")
        except Exception as e:
            log_callback(f"[ERROR] Unexpected error processing {display_name}: {e}\n")
            
    log_callback(f"\nConversion complete: {success_count}/{total_count} files/URLs succeeded.\n")
    return success_count, total_count

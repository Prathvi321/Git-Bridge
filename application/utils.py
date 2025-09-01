"""
Utility functions for Git Bridge application
"""

import subprocess
import os
import sys
import threading
from typing import Callable, Any
import tkinter as tk
from tkinter import messagebox

def check_git_installation() -> bool:
    """Check if Git is installed and accessible"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def run_in_thread(func: Callable, *args, **kwargs) -> threading.Thread:
    """Run a function in a separate thread"""
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()
    return thread

def show_error(title: str, message: str):
    """Show error message dialog"""
    messagebox.showerror(title, message)

def show_info(title: str, message: str):
    """Show info message dialog"""
    messagebox.showinfo(title, message)

def show_warning(title: str, message: str):
    """Show warning message dialog"""
    messagebox.showwarning(title, message)

def ask_yes_no(title: str, message: str) -> bool:
    """Ask yes/no question"""
    return messagebox.askyesno(title, message)

def validate_repo_name(name: str) -> bool:
    """Validate repository name"""
    if not name or not name.strip():
        return False
    
    # Check for invalid characters
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    return not any(char in name for char in invalid_chars)

def validate_email(email: str) -> bool:
    """Basic email validation"""
    return '@' in email and '.' in email.split('@')[-1]

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

class ProgressDialog:
    """Simple progress dialog"""
    def __init__(self, parent, title: str, message: str):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x100")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Create widgets
        tk.Label(self.dialog, text=message, wraplength=250).pack(pady=20)
        
        self.progress_var = tk.StringVar(value="Working...")
        self.progress_label = tk.Label(self.dialog, textvariable=self.progress_var)
        self.progress_label.pack()
        
    def update_message(self, message: str):
        """Update progress message"""
        self.progress_var.set(message)
        self.dialog.update()
        
    def close(self):
        """Close the dialog"""
        self.dialog.destroy()

def center_window(window, width: int, height: int):
    """Center a window on screen"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")

def bind_hotkeys(window, callbacks: dict):
    """Bind hotkeys to window"""
    hotkey_map = {
        '<Control-n>': callbacks.get('new_repo'),
        '<Control-o>': callbacks.get('open_repo'),
        '<Control-Shift-C>': callbacks.get('commit'),
        '<Control-p>': callbacks.get('push'),
        '<Control-l>': callbacks.get('pull'),
        '<Control-b>': callbacks.get('branch'),
        '<Control-h>': callbacks.get('history'),
        '<Control-r>': callbacks.get('refresh'),
        '<Control-slash>': callbacks.get('focus_command'),
        '<F1>': callbacks.get('help'),
        '<Control-q>': callbacks.get('quit')
    }
    
    for key, callback in hotkey_map.items():
        if callback:
            window.bind(key, lambda e, cb=callback: cb())

def get_app_data_dir() -> str:
    """Get application data directory"""
    if sys.platform == "win32":
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        return os.path.join(app_data, 'GitBridge')
    else:
        return os.path.join(os.path.expanduser('~'), '.gitbridge')

def ensure_dir_exists(path: str):
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)
#!/usr/bin/env python3
"""
Git Bridge - A complete GUI for Git operations
Entry point for the application
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import GitBridgeApp
from git_operations import GitOperations
from utils import check_git_installation

def main():
    """Main entry point for Git Bridge application"""
    try:
        # Check if Git is installed
        if not check_git_installation():
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Git Not Found", 
                "Git is not installed or not found in PATH.\n"
                "Please install Git and restart the application."
            )
            return
        
        # Create and run the application
        app = GitBridgeApp()
        app.run()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start Git Bridge: {str(e)}")

if __name__ == "__main__":
    main()
"""
Dialog windows for Git Bridge application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttk_bootstrap
from ttkbootstrap.constants import *
import os
from utils import validate_repo_name, validate_email

class BaseDialog:
    """Base class for dialogs"""
    def __init__(self, parent, title: str, width: int = 400, height: int = 300):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry(f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}")
        
        self.create_widgets()
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Override in subclasses"""
        pass
    
    def ok_clicked(self):
        """Override in subclasses"""
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Cancel dialog"""
        self.result = None
        self.dialog.destroy()

class NewRepoDialog(BaseDialog):
    """Dialog for creating new repository"""
    def __init__(self, parent):
        super().__init__(parent, "Create New Repository", 500, 200)
    
    def create_widgets(self):
        main_frame = ttk_bootstrap.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Repository name
        ttk_bootstrap.Label(main_frame, text="Repository Name:").pack(anchor=W, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk_bootstrap.Entry(main_frame, textvariable=self.name_var, width=40)
        self.name_entry.pack(fill=X, pady=5)
        self.name_entry.focus()
        
        # Location
        ttk_bootstrap.Label(main_frame, text="Location:").pack(anchor=W, pady=5)
        location_frame = ttk_bootstrap.Frame(main_frame)
        location_frame.pack(fill=X, pady=5)
        
        self.location_var = tk.StringVar(value=os.path.expanduser("~"))
        self.location_entry = ttk_bootstrap.Entry(location_frame, textvariable=self.location_var)
        self.location_entry.pack(side=LEFT, fill=X, expand=True)
        
        ttk_bootstrap.Button(location_frame, text="Browse", command=self.browse_location).pack(side=RIGHT, padx=(5, 0))
        
        # Buttons
        button_frame = ttk_bootstrap.Frame(main_frame)
        button_frame.pack(fill=X, pady=20)
        
        ttk_bootstrap.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=RIGHT, padx=5)
        ttk_bootstrap.Button(button_frame, text="Create", command=self.ok_clicked, bootstyle=PRIMARY).pack(side=RIGHT)
    
    def browse_location(self):
        """Browse for location"""
        folder = filedialog.askdirectory(title="Select Location", initialdir=self.location_var.get())
        if folder:
            self.location_var.set(folder)
    
    def ok_clicked(self):
        name = self.name_var.get().strip()
        location = self.location_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter a repository name")
            return
        
        if not validate_repo_name(name):
            messagebox.showerror("Error", "Invalid repository name")
            return
        
        if not location or not os.path.exists(location):
            messagebox.showerror("Error", "Please select a valid location")
            return
        
        repo_path = os.path.join(location, name)
        if os.path.exists(repo_path):
            messagebox.showerror("Error", "Directory already exists")
            return
        
        try:
            os.makedirs(repo_path)
            self.result = {'path': repo_path}
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create directory: {str(e)}")

class CloneRepoDialog(BaseDialog):
    """Dialog for cloning repository"""
    def __init__(self, parent):
        super().__init__(parent, "Clone Repository", 500, 250)
    
    def create_widgets(self):
        main_frame = ttk_bootstrap.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Repository URL
        ttk_bootstrap.Label(main_frame, text="Repository URL:").pack(anchor=W, pady=5)
        self.url_var = tk.StringVar()
        self.url_entry = ttk_bootstrap.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.pack(fill=X, pady=5)
        self.url_entry.focus()
        
        # Local path
        ttk_bootstrap.Label(main_frame, text="Local Path:").pack(anchor=W, pady=5)
        path_frame = ttk_bootstrap.Frame(main_frame)
        path_frame.pack(fill=X, pady=5)
        
        self.path_var = tk.StringVar(value=os.path.expanduser("~"))
        self.path_entry = ttk_bootstrap.Entry(path_frame, textvariable=self.path_var)
        self.path_entry.pack(side=LEFT, fill=X, expand=True)
        
        ttk_bootstrap.Button(path_frame, text="Browse", command=self.browse_path).pack(side=RIGHT, padx=(5, 0))
        
        # Repository name (auto-filled from URL)
        ttk_bootstrap.Label(main_frame, text="Repository Name:").pack(anchor=W, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk_bootstrap.Entry(main_frame, textvariable=self.name_var)
        self.name_entry.pack(fill=X, pady=5)
        
        # Auto-fill name when URL changes
        self.url_var.trace('w', self.update_name)
        
        # Buttons
        button_frame = ttk_bootstrap.Frame(main_frame)
        button_frame.pack(fill=X, pady=20)
        
        ttk_bootstrap.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=RIGHT, padx=5)
        ttk_bootstrap.Button(button_frame, text="Clone", command=self.ok_clicked, bootstyle=PRIMARY).pack(side=RIGHT)
    
    def browse_path(self):
        """Browse for path"""
        folder = filedialog.askdirectory(title="Select Location", initialdir=self.path_var.get())
        if folder:
            self.path_var.set(folder)
    
    def update_name(self, *args):
        """Auto-fill repository name from URL"""
        url = self.url_var.get()
        if url:
            # Extract repo name from URL
            name = url.split('/')[-1]
            if name.endswith('.git'):
                name = name[:-4]
            self.name_var.set(name)
    
    def ok_clicked(self):
        url = self.url_var.get().strip()
        path = self.path_var.get().strip()
        name = self.name_var.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter repository URL")
            return
        
        if not path or not os.path.exists(path):
            messagebox.showerror("Error", "Please select a valid path")
            return
        
        if not name:
            messagebox.showerror("Error", "Please enter repository name")
            return
        
        full_path = os.path.join(path, name)
        if os.path.exists(full_path):
            messagebox.showerror("Error", "Directory already exists")
            return
        
        self.result = {'url': url, 'path': full_path}
        self.dialog.destroy()

class CommitDialog(BaseDialog):
    """Dialog for committing changes"""
    def __init__(self, parent):
        super().__init__(parent, "Commit Changes", 500, 300)
    
    def create_widgets(self):
        main_frame = ttk_bootstrap.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Commit message
        ttk_bootstrap.Label(main_frame, text="Commit Message:").pack(anchor=W, pady=5)
        
        self.message_text = tk.Text(main_frame, height=8, wrap=tk.WORD)
        message_scroll = ttk_bootstrap.Scrollbar(main_frame, orient=VERTICAL, command=self.message_text.yview)
        self.message_text.configure(yscrollcommand=message_scroll.set)
        
        text_frame = ttk_bootstrap.Frame(main_frame)
        text_frame.pack(fill=BOTH, expand=True, pady=5)
        
        self.message_text.pack(side=LEFT, fill=BOTH, expand=True)
        message_scroll.pack(side=RIGHT, fill=Y)
        
        self.message_text.focus()
        
        # Buttons
        button_frame = ttk_bootstrap.Frame(main_frame)
        button_frame.pack(fill=X, pady=20)
        
        ttk_bootstrap.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=RIGHT, padx=5)
        ttk_bootstrap.Button(button_frame, text="Commit", command=self.ok_clicked, bootstyle=PRIMARY).pack(side=RIGHT)
    
    def ok_clicked(self):
        message = self.message_text.get(1.0, tk.END).strip()
        
        if not message:
            messagebox.showerror("Error", "Please enter a commit message")
            return
        
        self.result = {'message': message}
        self.dialog.destroy()

class BranchDialog(BaseDialog):
    """Dialog for creating branch"""
    def __init__(self, parent, title: str = "Create Branch"):
        self.dialog_title = title
        super().__init__(parent, title, 400, 150)
    
    def create_widgets(self):
        main_frame = ttk_bootstrap.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Branch name
        ttk_bootstrap.Label(main_frame, text="Branch Name:").pack(anchor=W, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk_bootstrap.Entry(main_frame, textvariable=self.name_var, width=30)
        self.name_entry.pack(fill=X, pady=5)
        self.name_entry.focus()
        
        # Buttons
        button_frame = ttk_bootstrap.Frame(main_frame)
        button_frame.pack(fill=X, pady=20)
        
        ttk_bootstrap.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=RIGHT, padx=5)
        ttk_bootstrap.Button(button_frame, text="Create", command=self.ok_clicked, bootstyle=PRIMARY).pack(side=RIGHT)
    
    def ok_clicked(self):
        name = self.name_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter a branch name")
            return
        
        # Basic validation
        if ' ' in name or any(c in name for c in ['~', '^', ':', '?', '*', '[']):
            messagebox.showerror("Error", "Invalid branch name")
            return
        
        self.result = {'name': name}
        self.dialog.destroy()

class SelectBranchDialog(BaseDialog):
    """Dialog for selecting branch"""
    def __init__(self, parent, branches: list, title: str = "Select Branch"):
        self.branches = branches
        super().__init__(parent, title, 300, 200)
    
    def create_widgets(self):
        main_frame = ttk_bootstrap.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Branch list
        ttk_bootstrap.Label(main_frame, text="Select Branch:").pack(anchor=W, pady=5)
        
        self.branch_listbox = tk.Listbox(main_frame, height=6)
        self.branch_listbox.pack(fill=BOTH, expand=True, pady=5)
        
        for branch in self.branches:
            self.branch_listbox.insert(tk.END, branch)
        
        if self.branches:
            self.branch_listbox.selection_set(0)
        
        # Buttons
        button_frame = ttk_bootstrap.Frame(main_frame)
        button_frame.pack(fill=X, pady=10)
        
        ttk_bootstrap.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=RIGHT, padx=5)
        ttk_bootstrap.Button(button_frame, text="Select", command=self.ok_clicked, bootstyle=PRIMARY).pack(side=RIGHT)
    
    def ok_clicked(self):
        selection = self.branch_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a branch")
            return
        
        branch = self.branches[selection[0]]
        self.result = {'branch': branch}
        self.dialog.destroy()

class SettingsDialog(BaseDialog):
    """Settings dialog"""
    def __init__(self, parent, auth_manager):
        self.auth_manager = auth_manager
        super().__init__(parent, "Settings", 500, 400)
    
    def create_widgets(self):
        notebook = ttk_bootstrap.Notebook(self.dialog)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Git settings tab
        git_frame = ttk_bootstrap.Frame(notebook, padding=20)
        notebook.add(git_frame, text="Git")
        
        credentials = self.auth_manager.get_git_credentials()
        
        ttk_bootstrap.Label(git_frame, text="User Name:").pack(anchor=W, pady=5)
        self.username_var = tk.StringVar(value=credentials['username'])
        ttk_bootstrap.Entry(git_frame, textvariable=self.username_var, width=40).pack(fill=X, pady=5)
        
        ttk_bootstrap.Label(git_frame, text="Email:").pack(anchor=W, pady=5)
        self.email_var = tk.StringVar(value=credentials['email'])
        ttk_bootstrap.Entry(git_frame, textvariable=self.email_var, width=40).pack(fill=X, pady=5)
        
        ttk_bootstrap.Label(git_frame, text="GitHub Token (optional):").pack(anchor=W, pady=5)
        self.token_var = tk.StringVar(value=credentials['token'])
        ttk_bootstrap.Entry(git_frame, textvariable=self.token_var, width=40, show="*").pack(fill=X, pady=5)
        
        # Application settings tab
        app_frame = ttk_bootstrap.Frame(notebook, padding=20)
        notebook.add(app_frame, text="Application")
        
        self.dark_mode_var = tk.BooleanVar(value=self.auth_manager.get_setting('dark_mode', True))
        ttk_bootstrap.Checkbutton(app_frame, text="Dark Mode", variable=self.dark_mode_var).pack(anchor=W, pady=10)
        
        # Buttons
        button_frame = ttk_bootstrap.Frame(self.dialog)
        button_frame.pack(fill=X, padx=10, pady=10)
        
        ttk_bootstrap.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=RIGHT, padx=5)
        ttk_bootstrap.Button(button_frame, text="Save", command=self.ok_clicked, bootstyle=PRIMARY).pack(side=RIGHT)
    
    def ok_clicked(self):
        username = self.username_var.get().strip()
        email = self.email_var.get().strip()
        token = self.token_var.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Please enter username")
            return
        
        if not email or not validate_email(email):
            messagebox.showerror("Error", "Please enter valid email")
            return
        
        # Save credentials
        self.auth_manager.store_git_credentials(username, email, token)
        
        # Save app settings
        self.auth_manager.set_setting('dark_mode', self.dark_mode_var.get())
        
        self.result = True
        self.dialog.destroy()

class SetupWizardDialog(BaseDialog):
    """Initial setup wizard"""
    def __init__(self, parent, auth_manager):
        self.auth_manager = auth_manager
        super().__init__(parent, "Git Bridge Setup", 600, 500)
    
    def create_widgets(self):
        main_frame = ttk_bootstrap.Frame(self.dialog, padding=30)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Welcome
        ttk_bootstrap.Label(main_frame, text="Welcome to Git Bridge!", font=('Arial', 16, 'bold')).pack(pady=20)
        ttk_bootstrap.Label(main_frame, text="Let's set up your Git configuration.", font=('Arial', 10)).pack(pady=10)
        
        # Git configuration
        config_frame = ttk_bootstrap.LabelFrame(main_frame, text="Git Configuration", padding=20)
        config_frame.pack(fill=X, pady=20)
        
        ttk_bootstrap.Label(config_frame, text="User Name:").pack(anchor=W, pady=5)
        self.username_var = tk.StringVar()
        ttk_bootstrap.Entry(config_frame, textvariable=self.username_var, width=40).pack(fill=X, pady=5)
        
        ttk_bootstrap.Label(config_frame, text="Email:").pack(anchor=W, pady=5)
        self.email_var = tk.StringVar()
        ttk_bootstrap.Entry(config_frame, textvariable=self.email_var, width=40).pack(fill=X, pady=5)
        
        ttk_bootstrap.Label(config_frame, text="GitHub Personal Access Token (optional):").pack(anchor=W, pady=5)
        self.token_var = tk.StringVar()
        ttk_bootstrap.Entry(config_frame, textvariable=self.token_var, width=40, show="*").pack(fill=X, pady=5)
        
        ttk_bootstrap.Label(config_frame, text="This token is used for private repositories and push operations.", 
                           font=('Arial', 8), foreground='gray').pack(anchor=W, pady=2)
        
        # Buttons
        button_frame = ttk_bootstrap.Frame(main_frame)
        button_frame.pack(fill=X, pady=20)
        
        ttk_bootstrap.Button(button_frame, text="Skip", command=self.cancel_clicked).pack(side=RIGHT, padx=5)
        ttk_bootstrap.Button(button_frame, text="Complete Setup", command=self.ok_clicked, bootstyle=PRIMARY).pack(side=RIGHT)
    
    def ok_clicked(self):
        username = self.username_var.get().strip()
        email = self.email_var.get().strip()
        token = self.token_var.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Please enter username")
            return
        
        if not email or not validate_email(email):
            messagebox.showerror("Error", "Please enter valid email")
            return
        
        # Save credentials
        self.auth_manager.store_git_credentials(username, email, token)
        
        messagebox.showinfo("Setup Complete", "Git Bridge has been configured successfully!")
        self.result = True
        self.dialog.destroy()

class HelpDialog:
    """Help dialog"""
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Git Bridge Help")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        
        # Create help content
        notebook = ttk_bootstrap.Notebook(self.dialog)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Shortcuts tab
        shortcuts_frame = ttk_bootstrap.Frame(notebook)
        notebook.add(shortcuts_frame, text="Shortcuts")
        
        shortcuts_text = tk.Text(shortcuts_frame, wrap=tk.WORD, padx=10, pady=10)
        shortcuts_scroll = ttk_bootstrap.Scrollbar(shortcuts_frame, orient=VERTICAL, command=shortcuts_text.yview)
        shortcuts_text.configure(yscrollcommand=shortcuts_scroll.set)
        
        shortcuts_content = """
Keyboard Shortcuts:

Ctrl + N        Create new repository
Ctrl + O        Open existing repository
Ctrl + Shift + C    Commit changes
Ctrl + P        Push to remote
Ctrl + L        Pull from remote
Ctrl + B        Create/switch branch
Ctrl + H        Show commit history
Ctrl + R        Refresh repository status
Ctrl + /        Focus on command input
F1              Show this help
Ctrl + Q        Quit application

Git Operations:

• Clone: Download a repository from remote
• Stage: Prepare files for commit
• Commit: Save changes to local repository
• Push: Upload changes to remote repository
• Pull: Download changes from remote repository
• Branch: Create parallel development lines
• Merge: Combine branches together

Tips:

• Use the command console for advanced Git operations
• Double-click recent repositories to open them quickly
• Right-click files in the status panel for more options
• The README tab shows rendered markdown files
        """
        
        shortcuts_text.insert(1.0, shortcuts_content)
        shortcuts_text.configure(state='disabled')
        
        shortcuts_text.pack(side=LEFT, fill=BOTH, expand=True)
        shortcuts_scroll.pack(side=RIGHT, fill=Y)
        
        # About tab
        about_frame = ttk_bootstrap.Frame(notebook)
        notebook.add(about_frame, text="About")
        
        about_text = tk.Text(about_frame, wrap=tk.WORD, padx=10, pady=10)
        about_content = """
Git Bridge v1.0

A modern graphical user interface for Git version control.

Features:
• Complete Git operations through GUI
• Command console for advanced users
• Branch management and visualization
• Commit history with graph view
• README preview with markdown rendering
• Dark/light theme support
• Secure credential storage
• Multi-repository support

Built with Python and Tkinter using ttkbootstrap for modern styling.

Git Bridge makes version control accessible to everyone while providing
powerful features for advanced users.
        """
        
        about_text.insert(1.0, about_content)
        about_text.configure(state='disabled')
        about_text.pack(fill=BOTH, expand=True)
        
        # Close button
        ttk_bootstrap.Button(self.dialog, text="Close", command=self.dialog.destroy).pack(pady=10)
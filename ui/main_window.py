"""
Main window for Git Bridge application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttk_bootstrap
from ttkbootstrap.constants import *
import os
import threading

from git_operations import GitOperations
from auth import AuthManager
from utils import *
from ui.dialogs import *
from ui.panels import *

class GitBridgeApp:
    def __init__(self):
        self.root = ttk_bootstrap.Window(themename="darkly")
        self.root.title("Git Bridge - Git GUI Client")
        self.root.geometry("1200x800")
        
        # Initialize managers
        self.auth_manager = AuthManager()
        self.git_ops = None
        self.current_repo = None
        
        # UI state
        self.dark_mode = self.auth_manager.get_setting('dark_mode', True)
        
        # Setup UI
        self.setup_ui()
        self.setup_hotkeys()
        
        # Check if first run
        if not self.auth_manager.is_configured():
            self.show_setup_wizard()
    
    def setup_ui(self):
        """Setup the main UI"""
        # Create main menu
        self.create_menu()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main layout
        self.create_main_layout()
        
        # Create status bar
        self.create_status_bar()
        
        # Load recent repositories
        self.load_recent_repos()
    
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Repository...", command=self.new_repository, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Repository...", command=self.open_repository, accelerator="Ctrl+O")
        file_menu.add_command(label="Clone Repository...", command=self.clone_repository)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app, accelerator="Ctrl+Q")
        
        # Git menu
        git_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Git", menu=git_menu)
        git_menu.add_command(label="Commit...", command=self.commit_changes, accelerator="Ctrl+Shift+C")
        git_menu.add_command(label="Push", command=self.push_changes, accelerator="Ctrl+P")
        git_menu.add_command(label="Pull", command=self.pull_changes, accelerator="Ctrl+L")
        git_menu.add_separator()
        git_menu.add_command(label="Create Branch...", command=self.create_branch, accelerator="Ctrl+B")
        git_menu.add_command(label="Switch Branch...", command=self.switch_branch)
        git_menu.add_separator()
        git_menu.add_command(label="View History", command=self.show_history, accelerator="Ctrl+H")
        git_menu.add_command(label="Refresh", command=self.refresh_status, accelerator="Ctrl+R")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        view_menu.add_command(label="Command Console", command=self.focus_command_input, accelerator="Ctrl+/")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help", command=self.show_help, accelerator="F1")
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_toolbar(self):
        """Create toolbar with common actions"""
        toolbar = ttk_bootstrap.Frame(self.root)
        toolbar.pack(fill=X, padx=5, pady=2)
        
        # Repository actions
        ttk_bootstrap.Button(toolbar, text="New", command=self.new_repository, width=8).pack(side=LEFT, padx=2)
        ttk_bootstrap.Button(toolbar, text="Open", command=self.open_repository, width=8).pack(side=LEFT, padx=2)
        ttk_bootstrap.Button(toolbar, text="Clone", command=self.clone_repository, width=8).pack(side=LEFT, padx=2)
        
        ttk_bootstrap.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5)
        
        # Git actions
        ttk_bootstrap.Button(toolbar, text="Commit", command=self.commit_changes, width=8).pack(side=LEFT, padx=2)
        ttk_bootstrap.Button(toolbar, text="Push", command=self.push_changes, width=8).pack(side=LEFT, padx=2)
        ttk_bootstrap.Button(toolbar, text="Pull", command=self.pull_changes, width=8).pack(side=LEFT, padx=2)
        
        ttk_bootstrap.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5)
        
        # Branch info
        self.branch_var = tk.StringVar(value="No repository")
        ttk_bootstrap.Label(toolbar, text="Branch:").pack(side=LEFT, padx=5)
        self.branch_label = ttk_bootstrap.Label(toolbar, textvariable=self.branch_var, font=('Arial', 9, 'bold'))
        self.branch_label.pack(side=LEFT)
        
        # Refresh button
        ttk_bootstrap.Button(toolbar, text="Refresh", command=self.refresh_status, width=8).pack(side=RIGHT, padx=2)
    
    def create_main_layout(self):
        """Create main application layout"""
        # Main paned window
        main_paned = ttk_bootstrap.PanedWindow(self.root, orient=HORIZONTAL)
        main_paned.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Left sidebar
        self.create_sidebar(main_paned)
        
        # Right content area
        self.create_content_area(main_paned)
        
        # Command console at bottom
        self.create_command_console()
    
    def create_sidebar(self, parent):
        """Create left sidebar with Git operations"""
        sidebar_frame = ttk_bootstrap.Frame(parent, width=250)
        parent.add(sidebar_frame, weight=0)
        
        # Repository section
        repo_frame = ttk_bootstrap.LabelFrame(sidebar_frame, text="Repository", padding=10)
        repo_frame.pack(fill=X, pady=5)
        
        ttk_bootstrap.Button(repo_frame, text="New Repository", command=self.new_repository).pack(fill=X, pady=2)
        ttk_bootstrap.Button(repo_frame, text="Open Repository", command=self.open_repository).pack(fill=X, pady=2)
        ttk_bootstrap.Button(repo_frame, text="Clone Repository", command=self.clone_repository).pack(fill=X, pady=2)
        
        # Changes section
        changes_frame = ttk_bootstrap.LabelFrame(sidebar_frame, text="Changes", padding=10)
        changes_frame.pack(fill=X, pady=5)
        
        ttk_bootstrap.Button(changes_frame, text="Stage All", command=self.stage_all_files).pack(fill=X, pady=2)
        ttk_bootstrap.Button(changes_frame, text="Commit Changes", command=self.commit_changes).pack(fill=X, pady=2)
        ttk_bootstrap.Button(changes_frame, text="Push", command=self.push_changes).pack(fill=X, pady=2)
        ttk_bootstrap.Button(changes_frame, text="Pull", command=self.pull_changes).pack(fill=X, pady=2)
        
        # Branches section
        branches_frame = ttk_bootstrap.LabelFrame(sidebar_frame, text="Branches", padding=10)
        branches_frame.pack(fill=X, pady=5)
        
        ttk_bootstrap.Button(branches_frame, text="Create Branch", command=self.create_branch).pack(fill=X, pady=2)
        ttk_bootstrap.Button(branches_frame, text="Switch Branch", command=self.switch_branch).pack(fill=X, pady=2)
        ttk_bootstrap.Button(branches_frame, text="Merge Branch", command=self.merge_branch).pack(fill=X, pady=2)
        ttk_bootstrap.Button(branches_frame, text="Delete Branch", command=self.delete_branch).pack(fill=X, pady=2)
        
        # History section
        history_frame = ttk_bootstrap.LabelFrame(sidebar_frame, text="History", padding=10)
        history_frame.pack(fill=X, pady=5)
        
        ttk_bootstrap.Button(history_frame, text="View History", command=self.show_history).pack(fill=X, pady=2)
        ttk_bootstrap.Button(history_frame, text="Export History", command=self.export_history).pack(fill=X, pady=2)
        
        # Recent repositories
        recent_frame = ttk_bootstrap.LabelFrame(sidebar_frame, text="Recent", padding=10)
        recent_frame.pack(fill=BOTH, expand=True, pady=5)
        
        self.recent_listbox = tk.Listbox(recent_frame, height=6)
        self.recent_listbox.pack(fill=BOTH, expand=True)
        self.recent_listbox.bind('<Double-Button-1>', self.open_recent_repo)
    
    def create_content_area(self, parent):
        """Create main content area"""
        content_frame = ttk_bootstrap.Frame(parent)
        parent.add(content_frame, weight=1)
        
        # Notebook for different views
        self.notebook = ttk_bootstrap.Notebook(content_frame)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Status tab
        self.status_panel = StatusPanel(self.notebook, self)
        self.notebook.add(self.status_panel.frame, text="Status")
        
        # History tab
        self.history_panel = HistoryPanel(self.notebook, self)
        self.notebook.add(self.history_panel.frame, text="History")
        
        # Files tab
        self.files_panel = FilesPanel(self.notebook, self)
        self.notebook.add(self.files_panel.frame, text="Files")
        
        # README tab
        self.readme_panel = ReadmePanel(self.notebook, self)
        self.notebook.add(self.readme_panel.frame, text="README")
    
    def create_command_console(self):
        """Create command console at bottom"""
        console_frame = ttk_bootstrap.LabelFrame(self.root, text="Git Command Console", padding=5)
        console_frame.pack(fill=X, padx=5, pady=5)
        
        # Command input
        input_frame = ttk_bootstrap.Frame(console_frame)
        input_frame.pack(fill=X, pady=2)
        
        ttk_bootstrap.Label(input_frame, text="$").pack(side=LEFT, padx=5)
        self.command_var = tk.StringVar()
        self.command_entry = ttk_bootstrap.Entry(input_frame, textvariable=self.command_var)
        self.command_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.command_entry.bind('<Return>', self.execute_command)
        
        ttk_bootstrap.Button(input_frame, text="Execute", command=self.execute_command).pack(side=RIGHT, padx=5)
        
        # Output area
        self.console_output = tk.Text(console_frame, height=6, wrap=tk.WORD)
        console_scroll = ttk_bootstrap.Scrollbar(console_frame, orient=VERTICAL, command=self.console_output.yview)
        self.console_output.configure(yscrollcommand=console_scroll.set)
        
        self.console_output.pack(side=LEFT, fill=BOTH, expand=True)
        console_scroll.pack(side=RIGHT, fill=Y)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk_bootstrap.Frame(self.root)
        self.status_bar.pack(fill=X, side=BOTTOM)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk_bootstrap.Label(self.status_bar, textvariable=self.status_var).pack(side=LEFT, padx=5)
        
        # Progress bar (hidden by default)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk_bootstrap.Progressbar(self.status_bar, variable=self.progress_var, mode='indeterminate')
    
    def setup_hotkeys(self):
        """Setup keyboard shortcuts"""
        bind_hotkeys(self.root, {
            'new_repo': self.new_repository,
            'open_repo': self.open_repository,
            'commit': self.commit_changes,
            'push': self.push_changes,
            'pull': self.pull_changes,
            'branch': self.create_branch,
            'history': self.show_history,
            'refresh': self.refresh_status,
            'focus_command': self.focus_command_input,
            'help': self.show_help,
            'quit': self.quit_app
        })
    
    def load_recent_repos(self):
        """Load recent repositories into listbox"""
        self.recent_listbox.delete(0, tk.END)
        for repo in self.auth_manager.get_recent_repos():
            if os.path.exists(repo):
                self.recent_listbox.insert(tk.END, os.path.basename(repo))
    
    def set_repository(self, repo_path: str):
        """Set current repository"""
        if not os.path.exists(repo_path):
            show_error("Error", f"Repository path does not exist: {repo_path}")
            return
        
        self.current_repo = repo_path
        self.git_ops = GitOperations(repo_path)
        
        if not self.git_ops.is_git_repo():
            show_error("Error", f"Not a Git repository: {repo_path}")
            return
        
        # Update UI
        self.root.title(f"Git Bridge - {os.path.basename(repo_path)}")
        self.auth_manager.add_recent_repo(repo_path)
        self.load_recent_repos()
        
        # Refresh all panels
        self.refresh_status()
        
        self.status_var.set(f"Repository: {repo_path}")
    
    def refresh_status(self):
        """Refresh repository status"""
        if not self.git_ops:
            return
        
        # Update branch info
        current_branch = self.git_ops.get_current_branch()
        self.branch_var.set(current_branch)
        
        # Refresh all panels
        self.status_panel.refresh()
        self.history_panel.refresh()
        self.files_panel.refresh()
        self.readme_panel.refresh()
    
    # Repository operations
    def new_repository(self):
        """Create new repository"""
        dialog = NewRepoDialog(self.root)
        if dialog.result:
            repo_path = dialog.result['path']
            success, output = self.git_ops.init_repo(repo_path) if self.git_ops else GitOperations().init_repo(repo_path)
            
            if success:
                self.set_repository(repo_path)
                show_info("Success", f"Repository created at {repo_path}")
            else:
                show_error("Error", f"Failed to create repository: {output}")
    
    def open_repository(self):
        """Open existing repository"""
        repo_path = filedialog.askdirectory(title="Select Repository Folder")
        if repo_path:
            self.set_repository(repo_path)
    
    def clone_repository(self):
        """Clone repository"""
        dialog = CloneRepoDialog(self.root)
        if dialog.result:
            url = dialog.result['url']
            path = dialog.result['path']
            
            def clone_thread():
                success, output = GitOperations().clone_repo(url, path)
                self.root.after(0, lambda: self.clone_complete(success, output, path))
            
            run_in_thread(clone_thread)
    
    def clone_complete(self, success: bool, output: str, path: str):
        """Handle clone completion"""
        if success:
            self.set_repository(path)
            show_info("Success", f"Repository cloned to {path}")
        else:
            show_error("Error", f"Failed to clone repository: {output}")
    
    def open_recent_repo(self, event):
        """Open repository from recent list"""
        selection = self.recent_listbox.curselection()
        if selection:
            index = selection[0]
            recent_repos = self.auth_manager.get_recent_repos()
            if index < len(recent_repos):
                self.set_repository(recent_repos[index])
    
    # Git operations
    def stage_all_files(self):
        """Stage all modified files"""
        if not self.git_ops:
            return
        
        success, output = self.git_ops.add_files(['.'])
        if success:
            self.refresh_status()
            show_info("Success", "All files staged")
        else:
            show_error("Error", f"Failed to stage files: {output}")
    
    def commit_changes(self):
        """Commit staged changes"""
        if not self.git_ops:
            return
        
        dialog = CommitDialog(self.root)
        if dialog.result:
            message = dialog.result['message']
            success, output = self.git_ops.commit(message)
            
            if success:
                self.refresh_status()
                show_info("Success", "Changes committed")
            else:
                show_error("Error", f"Failed to commit: {output}")
    
    def push_changes(self):
        """Push changes to remote"""
        if not self.git_ops:
            return
        
        def push_thread():
            success, output = self.git_ops.push()
            self.root.after(0, lambda: self.push_complete(success, output))
        
        run_in_thread(push_thread)
    
    def push_complete(self, success: bool, output: str):
        """Handle push completion"""
        if success:
            show_info("Success", "Changes pushed to remote")
        else:
            show_error("Error", f"Failed to push: {output}")
    
    def pull_changes(self):
        """Pull changes from remote"""
        if not self.git_ops:
            return
        
        def pull_thread():
            success, output = self.git_ops.pull()
            self.root.after(0, lambda: self.pull_complete(success, output))
        
        run_in_thread(pull_thread)
    
    def pull_complete(self, success: bool, output: str):
        """Handle pull completion"""
        if success:
            self.refresh_status()
            show_info("Success", "Changes pulled from remote")
        else:
            show_error("Error", f"Failed to pull: {output}")
    
    def create_branch(self):
        """Create new branch"""
        if not self.git_ops:
            return
        
        dialog = BranchDialog(self.root, "Create Branch")
        if dialog.result:
            branch_name = dialog.result['name']
            success, output = self.git_ops.create_branch(branch_name)
            
            if success:
                self.refresh_status()
                show_info("Success", f"Branch '{branch_name}' created and switched to")
            else:
                show_error("Error", f"Failed to create branch: {output}")
    
    def switch_branch(self):
        """Switch to different branch"""
        if not self.git_ops:
            return
        
        branches = self.git_ops.get_branches()
        if not branches:
            show_info("Info", "No branches found")
            return
        
        dialog = SelectBranchDialog(self.root, branches, "Switch Branch")
        if dialog.result:
            branch_name = dialog.result['branch']
            success, output = self.git_ops.switch_branch(branch_name)
            
            if success:
                self.refresh_status()
                show_info("Success", f"Switched to branch '{branch_name}'")
            else:
                show_error("Error", f"Failed to switch branch: {output}")
    
    def merge_branch(self):
        """Merge branch into current"""
        if not self.git_ops:
            return
        
        branches = self.git_ops.get_branches()
        current_branch = self.git_ops.get_current_branch()
        
        # Remove current branch from list
        available_branches = [b for b in branches if b != current_branch]
        
        if not available_branches:
            show_info("Info", "No other branches to merge")
            return
        
        dialog = SelectBranchDialog(self.root, available_branches, "Merge Branch")
        if dialog.result:
            branch_name = dialog.result['branch']
            
            if ask_yes_no("Confirm Merge", f"Merge '{branch_name}' into '{current_branch}'?"):
                success, output = self.git_ops.merge_branch(branch_name)
                
                if success:
                    self.refresh_status()
                    show_info("Success", f"Branch '{branch_name}' merged")
                else:
                    show_error("Error", f"Failed to merge branch: {output}")
    
    def delete_branch(self):
        """Delete a branch"""
        if not self.git_ops:
            return
        
        branches = self.git_ops.get_branches()
        current_branch = self.git_ops.get_current_branch()
        
        # Remove current branch from list
        available_branches = [b for b in branches if b != current_branch]
        
        if not available_branches:
            show_info("Info", "No other branches to delete")
            return
        
        dialog = SelectBranchDialog(self.root, available_branches, "Delete Branch")
        if dialog.result:
            branch_name = dialog.result['branch']
            
            if ask_yes_no("Confirm Delete", f"Delete branch '{branch_name}'? This cannot be undone."):
                success, output = self.git_ops.delete_branch(branch_name)
                
                if success:
                    self.refresh_status()
                    show_info("Success", f"Branch '{branch_name}' deleted")
                else:
                    show_error("Error", f"Failed to delete branch: {output}")
    
    def show_history(self):
        """Show commit history"""
        self.notebook.select(1)  # Switch to history tab
    
    def export_history(self):
        """Export commit history"""
        if not self.git_ops:
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export History",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            commits = self.git_ops.get_commit_history(100)
            try:
                with open(filename, 'w') as f:
                    f.write(f"Git History Export - {os.path.basename(self.current_repo)}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for commit in commits:
                        f.write(f"Commit: {commit['hash']}\n")
                        f.write(f"Author: {commit['author']} <{commit['email']}>\n")
                        f.write(f"Date: {commit['date']}\n")
                        f.write(f"Message: {commit['message']}\n")
                        f.write("-" * 30 + "\n\n")
                
                show_info("Success", f"History exported to {filename}")
            except Exception as e:
                show_error("Error", f"Failed to export history: {str(e)}")
    
    def execute_command(self, event=None):
        """Execute Git command from console"""
        command = self.command_var.get().strip()
        if not command:
            return
        
        self.command_var.set("")
        
        # Add to console output
        self.console_output.insert(tk.END, f"$ {command}\n")
        
        def execute_thread():
            if command.startswith('git '):
                # Execute git command
                cmd_parts = command.split()
                success, output = self.git_ops.execute_command(cmd_parts) if self.git_ops else (False, "No repository open")
            else:
                output = "Only Git commands are supported"
                success = False
            
            self.root.after(0, lambda: self.command_complete(output, success))
        
        run_in_thread(execute_thread)
    
    def command_complete(self, output: str, success: bool):
        """Handle command completion"""
        self.console_output.insert(tk.END, output + "\n\n")
        self.console_output.see(tk.END)
        
        if success:
            self.refresh_status()
    
    def focus_command_input(self):
        """Focus on command input"""
        self.command_entry.focus_set()
    
    # UI operations
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.dark_mode = not self.dark_mode
        theme = "darkly" if self.dark_mode else "flatly"
        self.root.style.theme_use(theme)
        self.auth_manager.set_setting('dark_mode', self.dark_mode)
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.root, self.auth_manager)
        if dialog.result:
            # Apply settings
            self.refresh_status()
    
    def show_setup_wizard(self):
        """Show initial setup wizard"""
        dialog = SetupWizardDialog(self.root, self.auth_manager)
    
    def show_help(self):
        """Show help dialog"""
        HelpDialog(self.root)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About Git Bridge",
            "Git Bridge v1.0\n\n"
            "A modern GUI for Git operations\n"
            "Built with Python and Tkinter\n\n"
            "© 2024 Git Bridge"
        )
    
    def quit_app(self):
        """Quit application"""
        if ask_yes_no("Quit", "Are you sure you want to quit Git Bridge?"):
            self.root.quit()
    
    def run(self):
        """Run the application"""
        center_window(self.root, 1200, 800)
        self.root.mainloop()
"""
UI panels for different views in Git Bridge
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk_bootstrap
from ttkbootstrap.constants import *
import os
import webbrowser

class BasePanel:
    """Base class for UI panels"""
    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk_bootstrap.Frame(parent)
        self.create_widgets()
    
    def create_widgets(self):
        """Override in subclasses"""
        pass
    
    def refresh(self):
        """Override in subclasses"""
        pass

class StatusPanel(BasePanel):
    """Panel showing repository status and file changes"""
    
    def create_widgets(self):
        # Main container
        main_frame = ttk_bootstrap.Frame(self.frame, padding=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Repository info
        info_frame = ttk_bootstrap.LabelFrame(main_frame, text="Repository Information", padding=10)
        info_frame.pack(fill=X, pady=5)
        
        self.repo_info_var = tk.StringVar(value="No repository selected")
        ttk_bootstrap.Label(info_frame, textvariable=self.repo_info_var, font=('Arial', 10)).pack(anchor=W)
        
        # File status sections
        paned = ttk_bootstrap.PanedWindow(main_frame, orient=VERTICAL)
        paned.pack(fill=BOTH, expand=True, pady=10)
        
        # Modified files
        modified_frame = ttk_bootstrap.LabelFrame(paned, text="Modified Files", padding=5)
        paned.add(modified_frame, weight=1)
        
        self.modified_listbox = tk.Listbox(modified_frame, height=6)
        modified_scroll = ttk_bootstrap.Scrollbar(modified_frame, orient=VERTICAL, command=self.modified_listbox.yview)
        self.modified_listbox.configure(yscrollcommand=modified_scroll.set)
        
        self.modified_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        modified_scroll.pack(side=RIGHT, fill=Y)
        
        # Context menu for modified files
        self.modified_menu = tk.Menu(self.modified_listbox, tearoff=0)
        self.modified_menu.add_command(label="Stage File", command=self.stage_selected_file)
        self.modified_menu.add_command(label="View Diff", command=self.view_file_diff)
        self.modified_listbox.bind("<Button-3>", self.show_modified_menu)
        self.modified_listbox.bind("<Double-Button-1>", self.view_file_diff)
        
        # Staged files
        staged_frame = ttk_bootstrap.LabelFrame(paned, text="Staged Files", padding=5)
        paned.add(staged_frame, weight=1)
        
        self.staged_listbox = tk.Listbox(staged_frame, height=6)
        staged_scroll = ttk_bootstrap.Scrollbar(staged_frame, orient=VERTICAL, command=self.staged_listbox.yview)
        self.staged_listbox.configure(yscrollcommand=staged_scroll.set)
        
        self.staged_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        staged_scroll.pack(side=RIGHT, fill=Y)
        
        # Context menu for staged files
        self.staged_menu = tk.Menu(self.staged_listbox, tearoff=0)
        self.staged_menu.add_command(label="Unstage File", command=self.unstage_selected_file)
        self.staged_menu.add_command(label="View Diff", command=self.view_staged_diff)
        self.staged_listbox.bind("<Button-3>", self.show_staged_menu)
        
        # Untracked files
        untracked_frame = ttk_bootstrap.LabelFrame(paned, text="Untracked Files", padding=5)
        paned.add(untracked_frame, weight=1)
        
        self.untracked_listbox = tk.Listbox(untracked_frame, height=6)
        untracked_scroll = ttk_bootstrap.Scrollbar(untracked_frame, orient=VERTICAL, command=self.untracked_listbox.yview)
        self.untracked_listbox.configure(yscrollcommand=untracked_scroll.set)
        
        self.untracked_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        untracked_scroll.pack(side=RIGHT, fill=Y)
        
        # Context menu for untracked files
        self.untracked_menu = tk.Menu(self.untracked_listbox, tearoff=0)
        self.untracked_menu.add_command(label="Stage File", command=self.stage_untracked_file)
        self.untracked_listbox.bind("<Button-3>", self.show_untracked_menu)
    
    def refresh(self):
        """Refresh status panel"""
        if not self.app.git_ops:
            self.repo_info_var.set("No repository selected")
            self.clear_lists()
            return
        
        # Update repository info
        repo_name = os.path.basename(self.app.current_repo)
        branch = self.app.git_ops.get_current_branch()
        self.repo_info_var.set(f"Repository: {repo_name} | Branch: {branch}")
        
        # Get status
        status = self.app.git_ops.get_status()
        
        if 'error' in status:
            self.clear_lists()
            return
        
        # Update file lists
        self.update_file_list(self.modified_listbox, status.get('modified', []))
        self.update_file_list(self.staged_listbox, status.get('staged', []))
        self.update_file_list(self.untracked_listbox, status.get('untracked', []))
    
    def clear_lists(self):
        """Clear all file lists"""
        self.modified_listbox.delete(0, tk.END)
        self.staged_listbox.delete(0, tk.END)
        self.untracked_listbox.delete(0, tk.END)
    
    def update_file_list(self, listbox, files):
        """Update a file list"""
        listbox.delete(0, tk.END)
        for file in files:
            listbox.insert(tk.END, file)
    
    def show_modified_menu(self, event):
        """Show context menu for modified files"""
        if self.modified_listbox.curselection():
            self.modified_menu.post(event.x_root, event.y_root)
    
    def show_staged_menu(self, event):
        """Show context menu for staged files"""
        if self.staged_listbox.curselection():
            self.staged_menu.post(event.x_root, event.y_root)
    
    def show_untracked_menu(self, event):
        """Show context menu for untracked files"""
        if self.untracked_listbox.curselection():
            self.untracked_menu.post(event.x_root, event.y_root)
    
    def stage_selected_file(self):
        """Stage selected modified file"""
        selection = self.modified_listbox.curselection()
        if selection and self.app.git_ops:
            filename = self.modified_listbox.get(selection[0])
            success, output = self.app.git_ops.add_files([filename])
            if success:
                self.refresh()
            else:
                messagebox.showerror("Error", f"Failed to stage file: {output}")
    
    def stage_untracked_file(self):
        """Stage selected untracked file"""
        selection = self.untracked_listbox.curselection()
        if selection and self.app.git_ops:
            filename = self.untracked_listbox.get(selection[0])
            success, output = self.app.git_ops.add_files([filename])
            if success:
                self.refresh()
            else:
                messagebox.showerror("Error", f"Failed to stage file: {output}")
    
    def unstage_selected_file(self):
        """Unstage selected staged file"""
        selection = self.staged_listbox.curselection()
        if selection and self.app.git_ops:
            filename = self.staged_listbox.get(selection[0])
            success, output = self.app.git_ops.execute_command(['git', 'reset', 'HEAD', filename])
            if success:
                self.refresh()
            else:
                messagebox.showerror("Error", f"Failed to unstage file: {output}")
    
    def view_file_diff(self):
        """View diff for selected modified file"""
        selection = self.modified_listbox.curselection()
        if selection and self.app.git_ops:
            filename = self.modified_listbox.get(selection[0])
            diff = self.app.git_ops.get_file_diff(filename)
            self.show_diff_window(filename, diff)
    
    def view_staged_diff(self):
        """View diff for selected staged file"""
        selection = self.staged_listbox.curselection()
        if selection and self.app.git_ops:
            filename = self.staged_listbox.get(selection[0])
            diff = self.app.git_ops.get_file_diff(filename, staged=True)
            self.show_diff_window(filename, diff, staged=True)
    
    def show_diff_window(self, filename, diff, staged=False):
        """Show diff in a new window"""
        diff_window = tk.Toplevel(self.app.root)
        diff_window.title(f"Diff: {filename} {'(Staged)' if staged else ''}")
        diff_window.geometry("800x600")
        
        # Diff text area
        diff_text = tk.Text(diff_window, wrap=tk.NONE, font=('Courier', 10))
        diff_scroll_y = ttk_bootstrap.Scrollbar(diff_window, orient=VERTICAL, command=diff_text.yview)
        diff_scroll_x = ttk_bootstrap.Scrollbar(diff_window, orient=HORIZONTAL, command=diff_text.xview)
        diff_text.configure(yscrollcommand=diff_scroll_y.set, xscrollcommand=diff_scroll_x.set)
        
        diff_text.pack(side=LEFT, fill=BOTH, expand=True)
        diff_scroll_y.pack(side=RIGHT, fill=Y)
        diff_scroll_x.pack(side=BOTTOM, fill=X)
        
        diff_text.insert(1.0, diff)
        diff_text.configure(state='disabled')
        
        # Color coding for diff
        diff_text.tag_configure("added", foreground="green")
        diff_text.tag_configure("removed", foreground="red")
        diff_text.tag_configure("header", foreground="blue", font=('Courier', 10, 'bold'))
        
        # Apply tags
        lines = diff.split('\n')
        for i, line in enumerate(lines, 1):
            if line.startswith('+') and not line.startswith('+++'):
                diff_text.tag_add("added", f"{i}.0", f"{i}.end")
            elif line.startswith('-') and not line.startswith('---'):
                diff_text.tag_add("removed", f"{i}.0", f"{i}.end")
            elif line.startswith('@@') or line.startswith('diff'):
                diff_text.tag_add("header", f"{i}.0", f"{i}.end")

class HistoryPanel(BasePanel):
    """Panel showing commit history"""
    
    def create_widgets(self):
        main_frame = ttk_bootstrap.Frame(self.frame, padding=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Controls
        controls_frame = ttk_bootstrap.Frame(main_frame)
        controls_frame.pack(fill=X, pady=5)
        
        ttk_bootstrap.Label(controls_frame, text="Limit:").pack(side=LEFT, padx=5)
        self.limit_var = tk.StringVar(value="50")
        limit_combo = ttk_bootstrap.Combobox(controls_frame, textvariable=self.limit_var, 
                                           values=["10", "25", "50", "100", "200"], width=10)
        limit_combo.pack(side=LEFT, padx=5)
        limit_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        
        ttk_bootstrap.Button(controls_frame, text="Refresh", command=self.refresh).pack(side=LEFT, padx=10)
        
        # History tree
        columns = ('Hash', 'Author', 'Date', 'Message')
        self.history_tree = ttk.Treeview(main_frame, columns=columns, show='tree headings', height=15)
        
        # Configure columns
        self.history_tree.heading('#0', text='Graph')
        self.history_tree.heading('Hash', text='Hash')
        self.history_tree.heading('Author', text='Author')
        self.history_tree.heading('Date', text='Date')
        self.history_tree.heading('Message', text='Message')
        
        self.history_tree.column('#0', width=100)
        self.history_tree.column('Hash', width=100)
        self.history_tree.column('Author', width=150)
        self.history_tree.column('Date', width=100)
        self.history_tree.column('Message', width=300)
        
        # Scrollbars
        history_scroll_y = ttk_bootstrap.Scrollbar(main_frame, orient=VERTICAL, command=self.history_tree.yview)
        history_scroll_x = ttk_bootstrap.Scrollbar(main_frame, orient=HORIZONTAL, command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=history_scroll_y.set, xscrollcommand=history_scroll_x.set)
        
        self.history_tree.pack(side=LEFT, fill=BOTH, expand=True)
        history_scroll_y.pack(side=RIGHT, fill=Y)
        history_scroll_x.pack(side=BOTTOM, fill=X)
        
        # Context menu
        self.history_menu = tk.Menu(self.history_tree, tearoff=0)
        self.history_menu.add_command(label="Copy Hash", command=self.copy_hash)
        self.history_menu.add_command(label="View Commit", command=self.view_commit)
        self.history_tree.bind("<Button-3>", self.show_history_menu)
    
    def refresh(self):
        """Refresh history panel"""
        if not self.app.git_ops:
            return
        
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Get commit history
        try:
            limit = int(self.limit_var.get())
        except ValueError:
            limit = 50
        
        commits = self.app.git_ops.get_commit_history(limit)
        
        # Add commits to tree
        for commit in commits:
            self.history_tree.insert('', 'end', 
                                   text=commit.get('graph', ''),
                                   values=(
                                       commit['hash'][:8],
                                       commit['author'],
                                       commit['date'],
                                       commit['message'][:80] + ('...' if len(commit['message']) > 80 else '')
                                   ))
    
    def show_history_menu(self, event):
        """Show context menu for history"""
        item = self.history_tree.identify_row(event.y)
        if item:
            self.history_tree.selection_set(item)
            self.history_menu.post(event.x_root, event.y_root)
    
    def copy_hash(self):
        """Copy commit hash to clipboard"""
        selection = self.history_tree.selection()
        if selection:
            item = selection[0]
            hash_short = self.history_tree.item(item)['values'][0]
            self.app.root.clipboard_clear()
            self.app.root.clipboard_append(hash_short)
    
    def view_commit(self):
        """View commit details"""
        selection = self.history_tree.selection()
        if selection:
            item = selection[0]
            hash_short = self.history_tree.item(item)['values'][0]
            
            # Get full commit info
            success, output = self.app.git_ops.execute_command(['git', 'show', hash_short])
            if success:
                self.show_commit_window(hash_short, output)
    
    def show_commit_window(self, commit_hash, commit_info):
        """Show commit details in new window"""
        commit_window = tk.Toplevel(self.app.root)
        commit_window.title(f"Commit: {commit_hash}")
        commit_window.geometry("800x600")
        
        # Commit info text area
        commit_text = tk.Text(commit_window, wrap=tk.NONE, font=('Courier', 10))
        commit_scroll_y = ttk_bootstrap.Scrollbar(commit_window, orient=VERTICAL, command=commit_text.yview)
        commit_scroll_x = ttk_bootstrap.Scrollbar(commit_window, orient=HORIZONTAL, command=commit_text.xview)
        commit_text.configure(yscrollcommand=commit_scroll_y.set, xscrollcommand=commit_scroll_x.set)
        
        commit_text.pack(side=LEFT, fill=BOTH, expand=True)
        commit_scroll_y.pack(side=RIGHT, fill=Y)
        commit_scroll_x.pack(side=BOTTOM, fill=X)
        
        commit_text.insert(1.0, commit_info)
        commit_text.configure(state='disabled')

class FilesPanel(BasePanel):
    """Panel showing repository files"""
    
    def create_widgets(self):
        main_frame = ttk_bootstrap.Frame(self.frame, padding=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        # File tree
        self.file_tree = ttk.Treeview(main_frame, show='tree')
        file_scroll = ttk_bootstrap.Scrollbar(main_frame, orient=VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=file_scroll.set)
        
        self.file_tree.pack(side=LEFT, fill=BOTH, expand=True)
        file_scroll.pack(side=RIGHT, fill=Y)
        
        # Context menu
        self.file_menu = tk.Menu(self.file_tree, tearoff=0)
        self.file_menu.add_command(label="Open File", command=self.open_file)
        self.file_menu.add_command(label="Open in Explorer", command=self.open_in_explorer)
        self.file_tree.bind("<Button-3>", self.show_file_menu)
        self.file_tree.bind("<Double-Button-1>", self.open_file)
    
    def refresh(self):
        """Refresh files panel"""
        if not self.app.git_ops or not self.app.current_repo:
            return
        
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Build file tree
        self.build_file_tree(self.app.current_repo, '')
    
    def build_file_tree(self, path, parent):
        """Build file tree recursively"""
        try:
            items = os.listdir(path)
            items.sort()
            
            for item in items:
                if item.startswith('.git'):
                    continue
                
                item_path = os.path.join(path, item)
                relative_path = os.path.relpath(item_path, self.app.current_repo)
                
                if os.path.isdir(item_path):
                    # Directory
                    node = self.file_tree.insert(parent, 'end', text=f"📁 {item}", 
                                                values=[relative_path], open=False)
                    # Add placeholder to make it expandable
                    self.file_tree.insert(node, 'end', text='Loading...')
                    self.file_tree.bind('<<TreeviewOpen>>', self.on_tree_open)
                else:
                    # File
                    icon = self.get_file_icon(item)
                    self.file_tree.insert(parent, 'end', text=f"{icon} {item}", 
                                        values=[relative_path])
        except PermissionError:
            pass
    
    def on_tree_open(self, event):
        """Handle tree node expansion"""
        item = self.file_tree.selection()[0]
        children = self.file_tree.get_children(item)
        
        # Remove placeholder
        if children and self.file_tree.item(children[0])['text'] == 'Loading...':
            self.file_tree.delete(children[0])
            
            # Load actual children
            relative_path = self.file_tree.item(item)['values'][0]
            full_path = os.path.join(self.app.current_repo, relative_path)
            self.build_file_tree(full_path, item)
    
    def get_file_icon(self, filename):
        """Get icon for file type"""
        ext = os.path.splitext(filename)[1].lower()
        
        icons = {
            '.py': '🐍',
            '.js': '📜',
            '.html': '🌐',
            '.css': '🎨',
            '.md': '📝',
            '.txt': '📄',
            '.json': '📋',
            '.xml': '📋',
            '.yml': '⚙️',
            '.yaml': '⚙️',
            '.git': '📁',
            '.png': '🖼️',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.gif': '🖼️',
            '.pdf': '📕',
            '.zip': '📦',
            '.tar': '📦',
            '.gz': '📦'
        }
        
        return icons.get(ext, '📄')
    
    def show_file_menu(self, event):
        """Show context menu for files"""
        item = self.file_tree.identify_row(event.y)
        if item:
            self.file_tree.selection_set(item)
            self.file_menu.post(event.x_root, event.y_root)
    
    def open_file(self):
        """Open selected file"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            relative_path = self.file_tree.item(item)['values'][0]
            full_path = os.path.join(self.app.current_repo, relative_path)
            
            if os.path.isfile(full_path):
                try:
                    os.startfile(full_path)  # Windows
                except AttributeError:
                    os.system(f'open "{full_path}"')  # macOS
                except:
                    os.system(f'xdg-open "{full_path}"')  # Linux
    
    def open_in_explorer(self):
        """Open file location in explorer"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            relative_path = self.file_tree.item(item)['values'][0]
            full_path = os.path.join(self.app.current_repo, relative_path)
            
            try:
                os.startfile(os.path.dirname(full_path))  # Windows
            except AttributeError:
                os.system(f'open "{os.path.dirname(full_path)}"')  # macOS
            except:
                os.system(f'xdg-open "{os.path.dirname(full_path)}"')  # Linux

class ReadmePanel(BasePanel):
    """Panel for README preview"""
    
    def create_widgets(self):
        main_frame = ttk_bootstrap.Frame(self.frame, padding=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        # README content
        self.readme_text = tk.Text(main_frame, wrap=tk.WORD, font=('Arial', 11))
        readme_scroll = ttk_bootstrap.Scrollbar(main_frame, orient=VERTICAL, command=self.readme_text.yview)
        self.readme_text.configure(yscrollcommand=readme_scroll.set)
        
        self.readme_text.pack(side=LEFT, fill=BOTH, expand=True)
        readme_scroll.pack(side=RIGHT, fill=Y)
        
        # Configure text tags for markdown-like formatting
        self.readme_text.tag_configure("heading1", font=('Arial', 16, 'bold'), spacing1=10, spacing3=5)
        self.readme_text.tag_configure("heading2", font=('Arial', 14, 'bold'), spacing1=8, spacing3=4)
        self.readme_text.tag_configure("heading3", font=('Arial', 12, 'bold'), spacing1=6, spacing3=3)
        self.readme_text.tag_configure("code", font=('Courier', 10), background='#f0f0f0')
        self.readme_text.tag_configure("bold", font=('Arial', 11, 'bold'))
        self.readme_text.tag_configure("italic", font=('Arial', 11, 'italic'))
    
    def refresh(self):
        """Refresh README panel"""
        if not self.app.current_repo:
            self.readme_text.delete(1.0, tk.END)
            self.readme_text.insert(1.0, "No repository selected")
            return
        
        # Look for README files
        readme_files = ['README.md', 'readme.md', 'README.txt', 'readme.txt', 'README']
        readme_path = None
        
        for readme_file in readme_files:
            path = os.path.join(self.app.current_repo, readme_file)
            if os.path.exists(path):
                readme_path = path
                break
        
        if not readme_path:
            self.readme_text.delete(1.0, tk.END)
            self.readme_text.insert(1.0, "No README file found in repository")
            return
        
        # Read and display README
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.readme_text.delete(1.0, tk.END)
            
            if readme_path.endswith('.md'):
                self.render_markdown(content)
            else:
                self.readme_text.insert(1.0, content)
                
        except Exception as e:
            self.readme_text.delete(1.0, tk.END)
            self.readme_text.insert(1.0, f"Error reading README: {str(e)}")
    
    def render_markdown(self, content):
        """Simple markdown rendering"""
        lines = content.split('\n')
        
        for line in lines:
            line = line.rstrip()
            
            if line.startswith('# '):
                self.readme_text.insert(tk.END, line[2:] + '\n', 'heading1')
            elif line.startswith('## '):
                self.readme_text.insert(tk.END, line[3:] + '\n', 'heading2')
            elif line.startswith('### '):
                self.readme_text.insert(tk.END, line[4:] + '\n', 'heading3')
            elif line.startswith('```'):
                # Code block (simplified)
                self.readme_text.insert(tk.END, line + '\n', 'code')
            elif '`' in line:
                # Inline code (simplified)
                parts = line.split('`')
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        self.readme_text.insert(tk.END, part)
                    else:
                        self.readme_text.insert(tk.END, part, 'code')
                self.readme_text.insert(tk.END, '\n')
            else:
                # Regular text with bold/italic (simplified)
                if '**' in line:
                    parts = line.split('**')
                    for i, part in enumerate(parts):
                        if i % 2 == 0:
                            self.readme_text.insert(tk.END, part)
                        else:
                            self.readme_text.insert(tk.END, part, 'bold')
                    self.readme_text.insert(tk.END, '\n')
                elif '*' in line:
                    parts = line.split('*')
                    for i, part in enumerate(parts):
                        if i % 2 == 0:
                            self.readme_text.insert(tk.END, part)
                        else:
                            self.readme_text.insert(tk.END, part, 'italic')
                    self.readme_text.insert(tk.END, '\n')
                else:
                    self.readme_text.insert(tk.END, line + '\n')
        
        self.readme_text.configure(state='disabled')
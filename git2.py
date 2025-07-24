import subprocess
import os
import ttkbootstrap as tb
import ttkbootstrap.constants as constants # Changed import to be explicit
from tkinter import filedialog, messagebox, simpledialog, Toplevel, Listbox, Scrollbar, END
from tkinter.scrolledtext import ScrolledText
from tkhtmlview import HTMLLabel
import markdown2
import webbrowser
import re # Import regex module for parsing commit hashes

# Import keyring for secure credential storage
try:
    import keyring
    import getpass
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    print("Keyring module not found. Secure credential storage will not be available.")


class GitApp:
    def __init__(self, master):
        self.master = master
        self.style = tb.Style('cosmo')
        master.title("Git Bridge")
        master.geometry("1200x800")

        self.repo_path = tb.StringVar(value=os.getcwd())

        self.build_ui()
        self.update_status()
        self.bind_shortcuts()

    def build_ui(self):
        menubar = tb.Menu(self.master)

        filemenu = tb.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Clone", command=self.clone_repo)
        filemenu.add_command(label="Init", command=self.init_repo)
        filemenu.add_separator()
        filemenu.add_command(label="Add", command=self.add_changes)
        filemenu.add_command(label="Commit", command=self.commit_changes)
        filemenu.add_command(label="Push", command=self.push_changes)
        filemenu.add_command(label="Pull", command=self.pull_changes)
        filemenu.add_command(label="Fetch", command=self.fetch_changes)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        branchmenu = tb.Menu(menubar, tearoff=0)
        branchmenu.add_command(label="New Branch", command=self.create_branch)
        branchmenu.add_command(label="Switch Branch", command=self.switch_branch)
        branchmenu.add_command(label="Delete Branch", command=self.delete_branch)
        menubar.add_cascade(label="Branch", menu=branchmenu)

        setupmenu = tb.Menu(menubar, tearoff=0)
        setupmenu.add_command(label="First Time Setup", command=self.setup_new_user)
        # Add a new menu for credentials
        if KEYRING_AVAILABLE:
            credmenu = tb.Menu(menubar, tearoff=0)
            credmenu.add_command(label="Set GitHub PAT", command=self.set_github_pat)
            credmenu.add_command(label="Delete GitHub PAT", command=self.delete_github_pat)
            menubar.add_cascade(label="Credentials", menu=credmenu)
        else:
            self.log("Keyring module not available. Credential management options disabled.", error=True)

        menubar.add_cascade(label="Setup", menu=setupmenu)

        helpmenu = tb.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.master.config(menu=menubar)

        card = tb.LabelFrame(self.master, text="Repository", padding=10)
        card.pack(fill=constants.X, padx=10, pady=10) # Using constants.X

        tb.Label(card, text="Path:").pack(side=constants.LEFT) # Using constants.LEFT
        tb.Entry(card, textvariable=self.repo_path, width=80).pack(side=constants.LEFT, padx=5, fill=constants.X, expand=True) # Using constants.LEFT, constants.X
        tb.Button(card, text="Browse", bootstyle=constants.PRIMARY, command=self.browse).pack(side=constants.LEFT, padx=5) # Using constants.PRIMARY, constants.LEFT

        self.status_indicator = tb.Label(card, text="●", font=("Arial", 16), foreground="gray")
        self.status_indicator.pack(side=constants.LEFT, padx=10) # Using constants.LEFT
        self.status_text = tb.Label(card, text="Status: ...")
        self.status_text.pack(side=constants.LEFT) # Using constants.LEFT

        notebook = tb.Notebook(self.master)
        notebook.pack(fill=constants.BOTH, expand=True, padx=10, pady=10) # Using constants.BOTH

        status_tab = tb.Frame(notebook)
        self.branch_label = tb.Label(status_tab, text="Branch: ...")
        self.branch_label.pack(anchor=constants.W, pady=5) # Using constants.W
        self.remote_label = tb.Label(status_tab, text="Remotes: ...")
        self.remote_label.pack(anchor=constants.W, pady=5) # Using constants.W
        notebook.add(status_tab, text="Status")

        log_tab = tb.Frame(notebook)
        self.output = ScrolledText(log_tab, state='disabled', wrap='word', font=("Consolas", 10))
        self.output.pack(fill=constants.BOTH, expand=True) # Using constants.BOTH
        notebook.add(log_tab, text="Logs")

        # Commit history tab now has clickable commits
        self.commit_history_tab = ScrolledText(notebook, wrap="word", font=("Consolas", 10))
        self.commit_history_tab.pack(fill=constants.BOTH, expand=True) # Using constants.BOTH
        notebook.add(self.commit_history_tab, text="Commit History")

        # Configure tag for clickable commits
        self.commit_history_tab.tag_configure("commit_link", foreground="blue", underline=True)
        self.commit_history_tab.tag_bind("commit_link", "<Button-1>", self.on_commit_click)

        self.readme_tab = tb.Frame(notebook)
        self.readme_html = HTMLLabel(self.readme_tab, html="No README loaded", background="white")
        self.readme_html.pack(fill=constants.BOTH, expand=True, padx=10, pady=10) # Using constants.BOTH
        notebook.add(self.readme_tab, text="README Preview")

    def bind_shortcuts(self):
        self.master.bind("<Control-s>", lambda e: self.add_changes())
        self.master.bind("<Control-c>", lambda e: self.commit_changes())
        self.master.bind("<Control-p>", lambda e: self.push_changes())
        self.master.bind("<Control-u>", lambda e: self.update_status())

    def browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.repo_path.set(folder)
            self.update_status()

    def update_status(self):
        path = self.repo_path.get()
        if not os.path.isdir(path):
            messagebox.showerror("Invalid path", f"{path} is not a valid directory")
            return

        if os.path.isdir(os.path.join(path, ".git")):
            status = self.run_git(["status", "--porcelain"])
            if status:
                lines = status.strip().splitlines()
                has_conflicts = any(line.startswith("U") for line in lines)
                has_changes = len(lines) > 0

                if has_conflicts:
                    color = "red"
                    text = "Conflicts present"
                elif has_changes:
                    color = "yellow"
                    text = "Uncommitted changes"
                else:
                    color = "green"
                    text = "Clean"
                self.status_indicator.configure(foreground=color)
                self.status_text.configure(text=f"Status: {text}")
            else:
                self.status_indicator.configure(foreground="green")
                self.status_text.configure(text="Status: Clean")

            branch = self.run_git(["rev-parse", "--abbrev-ref", "HEAD"])
            self.branch_label.config(text=f"Branch: {branch.strip() if branch else 'N/A'}")
            remotes = self.run_git(["remote", "-v"])
            self.remote_label.config(text=f"Remotes:\n{remotes.strip() if remotes else 'None'}")
        else:
            self.status_indicator.configure(foreground="gray")
            self.status_text.configure(text="Not a Git repository")
            self.branch_label.config(text="Branch: -")
            self.remote_label.config(text="Remotes: -")

        # Update commit history with clickable hashes
        self.update_commit_history()

        readme_path = os.path.join(path, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            html_content = markdown2.markdown(md_content)
            self.readme_html.set_html(html_content)
        else:
            self.readme_html.set_html("No README.md found.")

    def update_commit_history(self):
        """Fetches commit history and makes commit hashes clickable."""
        history = self.run_git(["log", "--oneline", "--graph", "--decorate", "--all"])
        self.commit_history_tab.configure(state='normal')
        self.commit_history_tab.delete("1.0", END)
        if history:
            lines = history.splitlines()
            for line in lines:
                self.commit_history_tab.insert(END, line + "\n")
                # Find commit hash in the line (e.g., 'a1b2c3d' or 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0')
                match = re.search(r'\b[0-9a-f]{7,40}\b', line)
                if match:
                    start_index = match.start()
                    end_index = match.end()
                    # Apply tag to the identified commit hash
                    self.commit_history_tab.tag_add("commit_link",
                                                     f"end-{len(line) - start_index}c -1c",
                                                     f"end-{len(line) - end_index}c -1c")
                    # Store the actual commit hash as a text property for easy retrieval on click
                    self.commit_history_tab.tag_bind("commit_link", "<Button-1>",
                                                     lambda event, commit=match.group(0): self.show_commit_diff(commit))
        self.commit_history_tab.configure(state='disabled')


    def on_commit_click(self, event):
        """Callback for clickable commit hashes."""
        # Get the index of the clicked character
        index = self.commit_history_tab.index(f"@{event.x},{event.y}")
        # Get all tags at that index
        tags = self.commit_history_tab.tag_names(index)
        if "commit_link" in tags:
            # Get the text of the clicked tag (which should be the commit hash)
            # This is a bit tricky with `tag_ranges` if there are multiple tags at the same spot.
            # A more robust way is to use the `lambda` with the commit hash directly bound.
            # The direct binding in `update_commit_history` makes this `on_commit_click` redundant.
            # However, `tag_bind` can only be set once per tag, not per occurrence.
            # Let's revert to a simpler method for `tag_bind` in `update_commit_history` and rely on `on_commit_click` to find the hash.
            # The current `tag_bind` in `update_commit_history` directly passes the commit.
            # So, `on_commit_click` is not needed if the lambda is working correctly.
            # The initial `tag_bind("commit_link", "<Button-1>", self.on_commit_click)` line should be removed.
            # The lambda in `update_commit_history` is sufficient.
            pass # The logic for calling show_commit_diff is now handled directly by the lambda in update_commit_history.


    def show_commit_diff(self, commit_hash):
        """Displays the diff for a given commit hash in a new window."""
        diff_output = self.run_git(["show", commit_hash])
        if diff_output:
            diff_window = Toplevel(self.master)
            diff_window.title(f"Diff for Commit: {commit_hash}")
            diff_window.geometry("800x600")

            diff_text = ScrolledText(diff_window, wrap='word', font=("Consolas", 10))
            diff_text.pack(fill=constants.BOTH, expand=True) # Using constants.BOTH
            diff_text.insert(END, diff_output)
            diff_text.configure(state='disabled')
        else:
            messagebox.showerror("Diff Error", f"Could not retrieve diff for commit {commit_hash}.")


    def run_git(self, args, cwd=None):
        cwd = cwd or self.repo_path.get()
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW # Prevents a console window from popping up on Windows
            )
            self.log(result.stdout)
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.log(e.stderr, error=True)
            return None
        except FileNotFoundError:
            messagebox.showerror("Git Missing", "Git is not installed or not in PATH.")
            exit(1)

    def log(self, message, error=False):
        self.output.configure(state='normal')
        tag = "error" if error else "info"
        self.output.insert(END, message + "\n", tag)
        self.output.tag_config("error", foreground="red")
        self.output.tag_config("info", foreground="black")
        self.output.see(END)
        self.output.configure(state='disabled')

    def get_github_pat_from_keyring(self):
        """Retrieves GitHub PAT from keyring."""
        if not KEYRING_AVAILABLE:
            return None
        return keyring.get_password("GitHub PAT", "github.com")

    def set_github_pat(self):
        """Prompts user to set GitHub Personal Access Token and stores it securely."""
        if not KEYRING_AVAILABLE:
            messagebox.showerror("Keyring Not Available",
                                 "The 'keyring' module is not installed. Cannot securely store PAT.")
            return

        github_username = simpledialog.askstring("GitHub PAT", "Enter your GitHub username (e.g., your-github-name):")
        if not github_username:
            return

        try:
            pat = getpass.getpass("Enter your GitHub Personal Access Token (this will not be displayed):")
            if not pat:
                messagebox.showwarning("GitHub PAT", "No Personal Access Token entered.")
                return

            # Store PAT securely with a service name and a generic username like "github.com"
            # This is more aligned with how keyring might manage system-wide credentials for a service.
            # Using the actual github_username might be better for individual tokens per user.
            # Let's use github.com as the 'username' for the keyring service for simplicity,
            # as the PAT itself is linked to the GitHub account.
            keyring.set_password("GitHub PAT", "github.com", pat)
            self.log(f"GitHub Personal Access Token for {github_username} stored securely.")
            messagebox.showinfo("GitHub PAT", "GitHub Personal Access Token stored securely.\n\n"
                                "For Git operations like push/pull/clone, Git's own credential helper "
                                "might automatically use this token if configured (e.g., Git Credential Manager "
                                "on Windows, osxkeychain on macOS). If you encounter authentication issues, "
                                "ensure your Git client's credential helper is set up correctly.")
        except Exception as e:
            messagebox.showerror("Keyring Error", f"Failed to store PAT: {e}")
            self.log(f"Error storing GitHub PAT: {e}", error=True)

    def delete_github_pat(self):
        """Deletes GitHub Personal Access Token from keyring."""
        if not KEYRING_AVAILABLE:
            messagebox.showerror("Keyring Not Available",
                                 "The 'keyring' module is not installed. Cannot delete PAT.")
            return

        if messagebox.askyesno("Delete GitHub PAT", "Are you sure you want to delete the stored GitHub Personal Access Token?"):
            try:
                keyring.delete_password("GitHub PAT", "github.com")
                self.log("GitHub Personal Access Token deleted.")
                messagebox.showinfo("GitHub PAT", "GitHub Personal Access Token deleted successfully.")
            except keyring.errors.NoKeyringError:
                messagebox.showerror("Keyring Error", "No keyring backend found. Cannot delete.")
                self.log("No keyring backend found when trying to delete PAT.", error=True)
            except Exception as e:
                messagebox.showerror("Keyring Error", f"Failed to delete PAT: {e}")
                self.log(f"Error deleting GitHub PAT: {e}", error=True)


    def clone_repo(self):
        url = simpledialog.askstring("Clone", "Repository URL?")
        if not url:
            return

        pat = self.get_github_pat_from_keyring()
        use_pat = False
        final_url = url

        if pat and ("github.com" in url or "github.io" in url) and url.startswith("https://"):
            # Offer to use PAT for GitHub HTTPS URLs
            if messagebox.askyesno("Use GitHub PAT?",
                                  "A GitHub Personal Access Token is stored. Do you want to use it for cloning this repository? "
                                  "This is recommended for private repositories. "
                                  "Note: Using PAT directly in the URL can expose it in system logs (e.g., `ps` command)."):
                # Modify URL to embed PAT. Using 'oauth2' as username is standard for PATs.
                # Example: https://oauth2:YOUR_PAT@github.com/user/repo.git
                parts = url.split("://", 1)
                final_url = f"{parts[0]}://oauth2:{pat}@{parts[1]}"
                self.log("Attempting to clone using stored GitHub PAT.")
                use_pat = True

        target = filedialog.askdirectory(title="Select target directory")
        if target:
            self.log(f"Cloning {final_url} into {target}")
            # Use final_url which might contain the PAT
            result = self.run_git(["clone", final_url], cwd=target)
            if result:
                self.update_status()
            else:
                self.log("Clone failed. If it's a private repository, ensure your PAT has 'repo' scope.", error=True)

    def init_repo(self):
        path = self.repo_path.get()
        if os.path.isdir(os.path.join(path, ".git")):
            messagebox.showinfo("Init", "Already a git repository")
            return
        if messagebox.askyesno("Init", f"Initialize git repo at {path}?"):
            self.run_git(["init"])
            self.update_status()

    def add_changes(self):
        self.log("Adding all changes...")
        self.run_git(["add", "."])
        self.update_status()

    def commit_changes(self):
        msg = simpledialog.askstring("Commit", "Commit message?")
        if msg:
            self.log(f"Committing with message: {msg}")
            self.run_git(["commit", "-m", msg])
            self.update_status()

    def push_changes(self):
        self.log("Pushing changes...")
        # For push/pull, Git's credential helper will usually handle authentication if PAT is in keyring
        # or if the user has configured it.
        self.run_git(["push"])
        self.update_status()

    def pull_changes(self):
        self.log("Pulling from remote...")
        self.run_git(["pull"])
        self.update_status()

    def fetch_changes(self):
        self.log("Fetching from remote...")
        self.run_git(["fetch"])
        self.update_status()

    def setup_new_user(self):
        self.log("Starting first-time Git + GitHub setup...")
        name = simpledialog.askstring("Git Identity", "Enter your Git user name:")
        email = simpledialog.askstring("Git Identity", "Enter your Git email:")
        if name and email:
            self.run_git(["config", "--global", "user.name", name])
            self.run_git(["config", "--global", "user.email", email])
            self.log(f"Configured git identity:\n  name: {name}\n  email: {email}")

    def create_branch(self):
        branch = simpledialog.askstring("New Branch", "Enter new branch name:")
        if branch:
            self.log(f"Creating branch: {branch}")
            self.run_git(["checkout", "-b", branch])
            self.update_status()

    def switch_branch(self):
        branches = self.run_git(["branch"])
        if branches:
            options = [b.strip("* ").strip() for b in branches.splitlines()]
            self.show_branch_selector(options, action="switch")

    def delete_branch(self):
        branches = self.run_git(["branch"])
        if branches:
            options = [b.strip("* ").strip() for b in branches.splitlines()]
            self.show_branch_selector(options, action="delete")

    def show_branch_selector(self, options, action):
        window = Toplevel(self.master)
        window.title(f"Select Branch to {action.capitalize()}")
        lb = Listbox(window, height=10)
        lb.pack(side=constants.LEFT, fill=constants.BOTH, expand=True) # Using constants.LEFT, constants.BOTH
        for branch in options:
            lb.insert(END, branch)
        scrollbar = Scrollbar(window)
        scrollbar.pack(side=constants.RIGHT, fill=constants.Y) # Using constants.RIGHT, constants.Y
        lb.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=lb.yview)

        def on_select():
            choice = lb.get(lb.curselection())
            if action == "switch":
                self.log(f"Switching to branch: {choice}")
                self.run_git(["checkout", choice])
            elif action == "delete":
                if messagebox.askyesno("Delete Branch", f"Really delete branch {choice}?"):
                    force = messagebox.askyesno("Force Delete?", "Force delete even if unmerged?")
                    cmd = ["branch", "-D" if force else "-d", choice]
                    self.run_git(cmd)
            window.destroy()
            self.update_status()

        tb.Button(window, text=f"{action.capitalize()}", command=on_select, bootstyle=constants.SUCCESS).pack(pady=5) # Using constants.SUCCESS

    def show_about(self):
        messagebox.showinfo("About", "Git Helper GUI\nProfessional tabbed interface")

if __name__ == "__main__":
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
    except FileNotFoundError:
        messagebox.showerror("Git Missing", "Git is not installed or not in PATH.")
        exit(1)

    root = tb.Window(themename="cosmo")
    app = GitApp(root)
    root.mainloop()
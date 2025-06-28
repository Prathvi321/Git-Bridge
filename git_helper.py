import subprocess
import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
import webbrowser

class GitApp:
    def __init__(self, master):
        self.master = master
        self.style = tb.Style('flatly')
        master.title("Git Bridge")
        master.geometry("1000x700")

        self.repo_path = tb.StringVar(value=os.getcwd())

        self.build_ui()
        self.update_status()
        self.bind_shortcuts()

    def build_ui(self):
        # Menu bar
        menubar = tb.Menu(self.master)

        # File menu
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
        filemenu.add_command(label="Status", command=self.show_status)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # Branch menu
        branchmenu = tb.Menu(menubar, tearoff=0)
        branchmenu.add_command(label="New Branch", command=self.create_branch)
        branchmenu.add_command(label="Switch Branch", command=self.switch_branch)
        branchmenu.add_command(label="Delete Branch", command=self.delete_branch)
        menubar.add_cascade(label="Branch", menu=branchmenu)

        # Setup menu
        setupmenu = tb.Menu(menubar, tearoff=0)
        setupmenu.add_command(label="First Time Setup", command=self.setup_new_user)
        menubar.add_cascade(label="Setup", menu=setupmenu)

        # History menu
        historymenu = tb.Menu(menubar, tearoff=0)
        historymenu.add_command(label="Show Commit History", command=self.show_commit_history)
        menubar.add_cascade(label="History", menu=historymenu)

        # Help menu
        helpmenu = tb.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about)
        helpmenu.add_command(label="GitHub SSH Keys", command=lambda: webbrowser.open("https://github.com/settings/keys"))
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.master.config(menu=menubar)

        # Repo path frame
        path_frame = tb.LabelFrame(self.master, text="Repository Path", padding=10)
        path_frame.pack(fill=X, padx=10, pady=10)

        tb.Label(path_frame, text="Path:").pack(side=LEFT)
        tb.Entry(path_frame, textvariable=self.repo_path, width=70).pack(side=LEFT, fill=X, expand=True, padx=5)
        tb.Button(path_frame, text="Browse", bootstyle=PRIMARY, command=self.browse).pack(side=LEFT, padx=5)

        # Status frame
        self.status_frame = tb.LabelFrame(self.master, text="Repository Status", padding=10)
        self.status_frame.pack(fill=X, padx=10, pady=5)

        self.status_label = tb.Label(self.status_frame, text="Status: ...")
        self.status_label.pack(anchor=W)
        self.branch_label = tb.Label(self.status_frame, text="Branch: ...")
        self.branch_label.pack(anchor=W)
        self.remote_label = tb.Label(self.status_frame, text="Remotes: ...")
        self.remote_label.pack(anchor=W)

        # Output log
        output_frame = tb.LabelFrame(self.master, text="Output Log", padding=10)
        output_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.output = ScrolledText(output_frame, state='disabled', wrap='word', font=("Consolas", 10))
        self.output.pack(fill=BOTH, expand=True)

    def bind_shortcuts(self):
        self.master.bind("<Control-s>", lambda e: self.add_changes())
        self.master.bind("<Control-c>", lambda e: self.commit_changes())
        self.master.bind("<Control-p>", lambda e: self.push_changes())
        self.master.bind("<Control-u>", lambda e: self.show_status())

    def browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.repo_path.set(folder)
            self.update_status()

    def update_status(self):
        path = self.repo_path.get()
        if os.path.isdir(os.path.join(path, ".git")):
            self.status_label.config(text="Status: Git repository", foreground="green")
            branch = self.run_git(["rev-parse", "--abbrev-ref", "HEAD"])
            self.branch_label.config(text=f"Branch: {branch.strip() if branch else 'N/A'}")
            remotes = self.run_git(["remote", "-v"])
            self.remote_label.config(text=f"Remotes:\n{remotes.strip() if remotes else 'None'}")
        else:
            self.status_label.config(text="Status: Not a Git repository", foreground="red")
            self.branch_label.config(text="Branch: -")
            self.remote_label.config(text="Remotes: -")

    def run_git(self, args, cwd=None):
        cwd = cwd or self.repo_path.get()
        try:
            result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, check=True)
            self.log(result.stdout)
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.log(e.stderr, error=True)
            return None

    def log(self, message, error=False):
        self.output.configure(state='normal')
        tag = "error" if error else "info"
        self.output.insert(END, message + "\n", tag)
        self.output.tag_config("error", foreground="red")
        self.output.tag_config("info", foreground="black")
        self.output.see(END)
        self.output.configure(state='disabled')

    def clone_repo(self):
        url = simpledialog.askstring("Clone", "Repository URL?")
        if url:
            target = filedialog.askdirectory(title="Select target directory")
            if target:
                self.log(f"Cloning {url} into {target}")
                self.run_git(["clone", url], cwd=target)
                self.update_status()

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

    def show_status(self):
        self.log("Checking status...")
        self.run_git(["status"])

    def setup_new_user(self):
        self.log("Starting first-time Git + GitHub setup...")
        name = simpledialog.askstring("Git Identity", "Enter your Git user name:")
        email = simpledialog.askstring("Git Identity", "Enter your Git email:")
        if name and email:
            self.run_git(["config", "--global", "user.name", name])
            self.run_git(["config", "--global", "user.email", email])
            self.log(f"Configured git identity:\n  name: {name}\n  email: {email}")
        else:
            self.log("Git identity setup canceled.")
            return

        # Generate SSH key
        ssh_dir = os.path.expanduser("~/.ssh")
        pubkey_path = os.path.join(ssh_dir, "id_ed25519.pub")
        if not os.path.exists(pubkey_path):
            if messagebox.askyesno("SSH Key", "No SSH key found. Generate a new one?"):
                if not os.path.exists(ssh_dir):
                    os.makedirs(ssh_dir)
                cmd = [
                    "ssh-keygen",
                    "-t", "ed25519",
                    "-C", email,
                    "-f", os.path.join(ssh_dir, "id_ed25519"),
                    "-N", ""
                ]
                try:
                    subprocess.run(cmd, check=True)
                    self.log("SSH key generated successfully.")
                except Exception as e:
                    self.log(f"Error generating SSH key: {e}", error=True)
                    return
        else:
            self.log("Existing SSH key detected.")

        # Show public key
        try:
            with open(pubkey_path, "r") as f:
                pubkey = f.read()
                self.log(f"Public SSH key:\n{pubkey}")
                messagebox.showinfo("Copy your SSH key", f"Your SSH public key:\n\n{pubkey}\n\nCopy and paste this on GitHub.")
        except Exception as e:
            self.log(f"Error reading SSH public key: {e}", error=True)

        webbrowser.open("https://github.com/settings/keys")
        self.log("Opened GitHub SSH keys page.")

    def show_commit_history(self):
        log = self.run_git(["log", "--oneline", "--graph", "--decorate", "--all"])
        if log:
            history_window = tb.Toplevel(self.master)
            history_window.title("Commit History")
            history_window.geometry("700x500")
            st = ScrolledText(history_window, wrap="word", font=("Consolas", 10))
            st.insert("end", log)
            st.pack(fill="both", expand=True)

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
            choice = simpledialog.askstring("Switch Branch", f"Available branches:\n\n{', '.join(options)}\n\nWhich to switch to?")
            if choice and choice in options:
                self.log(f"Switching to branch: {choice}")
                self.run_git(["checkout", choice])
                self.update_status()
            else:
                self.log("Branch switch canceled or invalid.", error=True)

    def delete_branch(self):
        branches = self.run_git(["branch"])
        if branches:
            options = [b.strip("* ").strip() for b in branches.splitlines()]
            choice = simpledialog.askstring("Delete Branch", f"Available branches:\n\n{', '.join(options)}\n\nWhich to delete?")
            if choice and choice in options:
                if messagebox.askyesno("Delete Branch", f"Really delete branch {choice}?"):
                    self.log(f"Deleting branch: {choice}")
                    self.run_git(["branch", "-d", choice])
                    self.update_status()
            else:
                self.log("Branch deletion canceled or invalid.", error=True)

    def show_about(self):
        messagebox.showinfo("About", "Git Helper GUI\nBuilt with ttkbootstrap + tkinter\nfor easy git operations.")

if __name__ == "__main__":
    root = tb.Window(themename="flatly")
    app = GitApp(root)
    root.mainloop()

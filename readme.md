# 🌉 Git Bridge

**A Modern, User-Friendly GUI for Git Operations**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/Prathvi321/Git-Bridge)
[![Website](https://img.shields.io/badge/Website-Live-brightgreen.svg)](https://prathvi321.github.io/Git-Bridge/website/)

Git Bridge makes Git accessible to everyone while empowering advanced users with a beautiful, modern interface built with Python and Tkinter.

![Git Bridge Screenshot](https://via.placeholder.com/800x500/2c3e50/ecf0f1?text=Git+Bridge+Interface)

## ✨ Features

### 🎯 Core Git Operations
- **Repository Management**: Create, open, and clone repositories with ease
- **Version Control**: Stage, commit, push, and pull changes visually
- **Branch Management**: Create, switch, delete, and merge branches
- **Remote Management**: Add, remove, and manage remote repositories
- **History Visualization**: Beautiful commit history with graph-like display
- **File Operations**: View diffs, manage staged/unstaged files with context menus

### 🎨 Modern User Interface
- **Contemporary Design**: Built with ttkbootstrap for a sleek, modern look
- **Dark/Light Themes**: Toggle between themes to match your preference
- **Tabbed Interface**: Organized panels for Status, History, Files, and README
- **Context Menus**: Right-click operations on files and commits
- **Tooltips & Help**: Comprehensive guidance for Git beginners

### ⚡ Advanced Features
- **Command Console**: Execute Git commands directly for power users
- **README Preview**: Live markdown rendering for documentation
- **Secure Credentials**: Safe storage using system keyring
- **Multi-Repository Support**: Manage multiple projects effortlessly
- **Export History**: Save commit history to text files
- **Keyboard Shortcuts**: Lightning-fast navigation and operations

## 🚀 Quick Start

### Prerequisites
- **Python 3.7+** - [Download Python](https://python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)

### Installation

#### Option 1: Easy Install (Windows)
1. Download the latest release
2. Extract the files
3. Double-click `run.bat`

#### Option 2: Manual Install
```bash
# Clone the repository
git clone https://github.com/Prathvi321/Git-Bridge.git
cd Git-Bridge

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

#### Option 3: Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + N` | Create new repository |
| `Ctrl + O` | Open existing repository |
| `Ctrl + Shift + C` | Commit changes |
| `Ctrl + P` | Push to remote |
| `Ctrl + L` | Pull from remote |
| `Ctrl + B` | Create/switch branch |
| `Ctrl + H` | Show commit history |
| `Ctrl + R` | Refresh repository status |
| `Ctrl + /` | Focus on command input |
| `F1` | Show help |
| `Ctrl + Q` | Quit application |

## 🎯 Usage Guide

### First Time Setup
When you first run Git Bridge, you'll be guided through:
1. **Git Configuration**: Set your username and email
2. **GitHub Integration**: Optional Personal Access Token for private repos
3. **Theme Selection**: Choose your preferred interface theme

### Getting Started
1. **Create Repository**: `Ctrl + N` or click "New" to initialize a Git repository
2. **Open Repository**: `Ctrl + O` or click "Open" to work with existing projects
3. **Clone Repository**: Click "Clone" to download repositories from GitHub/GitLab

### Daily Workflow
1. **View Changes**: The Status tab shows all modified, staged, and untracked files
2. **Stage Files**: Right-click files to stage them individually or use "Stage All"
3. **Commit Changes**: `Ctrl + Shift + C` to commit with a descriptive message
4. **Sync Changes**: Push/Pull buttons to synchronize with remote repositories

### Branch Management
- **Create Branch**: `Ctrl + B` to create and switch to a new branch
- **Switch Branch**: Select from existing branches in the dropdown
- **Merge Branches**: Safely merge feature branches into main
- **Delete Branches**: Clean up completed feature branches

### Advanced Features
- **Command Console**: Type Git commands directly for complex operations
- **File Explorer**: Browse repository files with the Files tab
- **History Viewer**: Visualize commit history with the History tab
- **README Preview**: View rendered markdown in the README tab

## 🏗️ Architecture

```
Git Bridge/
├── main.py              # Application entry point
├── git_operations.py    # Core Git command operations
├── auth.py             # Credential management & storage
├── utils.py            # Utility functions & helpers
├── ui/
│   ├── __init__.py     # UI package initialization
│   ├── main_window.py  # Main application window
│   ├── dialogs.py      # Dialog windows (commit, clone, etc.)
│   └── panels.py       # UI panels (Status, History, Files, README)
├── requirements.txt    # Python dependencies
├── run.bat            # Windows quick-start script
├── .gitignore         # Git ignore patterns
└── README.md          # This file
```

## 🔧 Dependencies

- **ttkbootstrap** - Modern Tkinter themes and widgets
- **keyring** - Secure credential storage
- **markdown2** - Markdown rendering for README preview

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/Prathvi321/Git-Bridge.git
cd Git-Bridge

# Create development environment
python -m venv dev-env
source dev-env/bin/activate  # or dev-env\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest

# Start development
python main.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Bug Reports & Feature Requests

Found a bug or have a feature request? Please open an issue on our [GitHub Issues](https://github.com/Prathvi321/Git-Bridge/issues) page.

When reporting bugs, please include:
- Operating system and version
- Python version
- Git version
- Steps to reproduce the issue
- Expected vs actual behavior

## 📞 Support

- **Documentation**: Check this README and the built-in help (`F1`)
- **Issues**: [GitHub Issues](https://github.com/Prathvi321/Git-Bridge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Prathvi321/Git-Bridge/discussions)

## 🙏 Acknowledgments

- **ttkbootstrap** team for the beautiful modern themes
- **Git** community for the amazing version control system
- **Python** community for the excellent ecosystem
- All contributors who help make Git Bridge better

## 📊 Project Stats

- **Language**: Python
- **GUI Framework**: Tkinter with ttkbootstrap
- **Supported Platforms**: Windows, macOS, Linux
- **License**: MIT
- **Status**: Active Development

---

**Git Bridge** - Making Git accessible to everyone while empowering advanced users.

*Built with ❤️ by developers, for developers.*
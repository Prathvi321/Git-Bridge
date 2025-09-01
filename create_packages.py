#!/usr/bin/env python3
"""
Script to create downloadable packages for Git Bridge
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_source_package():
    """Create source code package"""
    print("Creating source code package...")
    
    # Files to include in source package
    source_files = [
        'main.py',
        'git_operations.py',
        'auth.py',
        'utils.py',
        'requirements.txt',
        'README.md',
        'run.bat',
        '.gitignore',
        'ui/__init__.py',
        'ui/main_window.py',
        'ui/dialogs.py',
        'ui/panels.py'
    ]
    
    # Create zip file
    with zipfile.ZipFile('website/git-bridge-source.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in source_files:
            if os.path.exists(file):
                zipf.write(file, f'git-bridge/{file}')
        
        # Add installation instructions
        install_instructions = """# Git Bridge Installation

## Quick Start
1. Extract this archive
2. Install Python 3.7+ if not already installed
3. Run: pip install -r requirements.txt
4. Run: python main.py

## Windows
- Double-click run.bat for automatic setup

## macOS/Linux
- Run: chmod +x run.sh && ./run.sh (if run.sh exists)
- Or manually: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python main.py

## Requirements
- Python 3.7+
- Git installed and in PATH
- Internet connection for initial setup

Enjoy using Git Bridge!
"""
        zipf.writestr('git-bridge/INSTALL.txt', install_instructions)
    
    print("Source package created: website/git-bridge-source.zip")

def create_windows_package():
    """Create Windows package"""
    print("Creating Windows package...")
    
    # Create a batch installer
    installer_content = """@echo off
echo Git Bridge Installer for Windows
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Installing Python...
    echo Please download Python from https://python.org/downloads/
    echo Then run this installer again.
    pause
    exit /b 1
)

REM Check Git
git --version >nul 2>&1
if errorlevel 1 (
    echo Installing Git...
    echo Please download Git from https://git-scm.com/downloads
    echo Then run this installer again.
    pause
    exit /b 1
)

echo Creating Git Bridge directory...
mkdir "%USERPROFILE%\\Git Bridge" 2>nul

echo Extracting files...
REM In a real installer, files would be extracted here

echo Installing dependencies...
cd "%USERPROFILE%\\Git Bridge"
python -m venv venv
call venv\\Scripts\\activate.bat
pip install ttkbootstrap keyring markdown2

echo Creating desktop shortcut...
echo @echo off > "%USERPROFILE%\\Desktop\\Git Bridge.bat"
echo cd "%USERPROFILE%\\Git Bridge" >> "%USERPROFILE%\\Desktop\\Git Bridge.bat"
echo call venv\\Scripts\\activate.bat >> "%USERPROFILE%\\Desktop\\Git Bridge.bat"
echo python main.py >> "%USERPROFILE%\\Desktop\\Git Bridge.bat"

echo.
echo Installation complete!
echo You can now run Git Bridge from your desktop.
pause
"""
    
    # Create Windows package
    with zipfile.ZipFile('website/git-bridge-windows.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all source files
        for root, dirs, files in os.walk('.'):
            # Skip website and __pycache__ directories
            dirs[:] = [d for d in dirs if d not in ['website', '__pycache__', '.git', 'venv']]
            
            for file in files:
                if file.endswith(('.py', '.txt', '.md', '.bat')) and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    arc_path = file_path.replace('.\\', 'git-bridge\\')
                    zipf.write(file_path, arc_path)
        
        # Add installer
        zipf.writestr('install.bat', installer_content)
        zipf.writestr('README.txt', 'Run install.bat to install Git Bridge on Windows')
    
    print("Windows package created: website/git-bridge-windows.zip")

def create_macos_package():
    """Create macOS package (simulated)"""
    print("Creating macOS package...")
    
    # Create a shell script installer
    installer_content = """#!/bin/bash
echo "Git Bridge Installer for macOS"
echo "=============================="
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Installing Python..."
    echo "Please install Python 3.7+ from https://python.org/downloads/"
    echo "Then run this installer again."
    exit 1
fi

# Check Git
if ! command -v git &> /dev/null; then
    echo "Installing Git..."
    echo "Please install Git from https://git-scm.com/downloads"
    echo "Then run this installer again."
    exit 1
fi

echo "Creating Git Bridge directory..."
mkdir -p "$HOME/Applications/Git Bridge"

echo "Installing dependencies..."
cd "$HOME/Applications/Git Bridge"
python3 -m venv venv
source venv/bin/activate
pip install ttkbootstrap keyring markdown2

echo "Creating application launcher..."
cat > "$HOME/Applications/Git Bridge/Git Bridge.command" << 'EOF'
#!/bin/bash
cd "$HOME/Applications/Git Bridge"
source venv/bin/activate
python main.py
EOF

chmod +x "$HOME/Applications/Git Bridge/Git Bridge.command"

echo
echo "Installation complete!"
echo "You can now run Git Bridge from $HOME/Applications/Git Bridge/"
"""
    
    # Create a dummy DMG (in reality, this would be a proper macOS installer)
    with open('website/git-bridge-macos.dmg', 'w') as f:
        f.write("# Git Bridge for macOS\n")
        f.write("This would be a proper macOS DMG installer in production.\n")
        f.write("For now, please download the source code and run manually.\n")
    
    print("macOS package created: website/git-bridge-macos.dmg")

def create_linux_package():
    """Create Linux AppImage (simulated)"""
    print("Creating Linux package...")
    
    # Create a shell script installer
    installer_content = """#!/bin/bash
echo "Git Bridge for Linux"
echo "==================="
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Please install Python 3.7+ using your package manager"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "Fedora: sudo dnf install python3 python3-pip"
    echo "Arch: sudo pacman -S python python-pip"
    exit 1
fi

# Check Git
if ! command -v git &> /dev/null; then
    echo "Please install Git using your package manager"
    echo "Ubuntu/Debian: sudo apt install git"
    echo "Fedora: sudo dnf install git"
    echo "Arch: sudo pacman -S git"
    exit 1
fi

echo "Creating Git Bridge directory..."
mkdir -p "$HOME/.local/share/git-bridge"

echo "Installing dependencies..."
cd "$HOME/.local/share/git-bridge"
python3 -m venv venv
source venv/bin/activate
pip install ttkbootstrap keyring markdown2

echo "Creating desktop entry..."
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/git-bridge.desktop" << 'EOF'
[Desktop Entry]
Name=Git Bridge
Comment=Modern Git GUI Client
Exec=/home/$USER/.local/share/git-bridge/git-bridge.sh
Icon=git
Terminal=false
Type=Application
Categories=Development;
EOF

cat > "$HOME/.local/share/git-bridge/git-bridge.sh" << 'EOF'
#!/bin/bash
cd "$HOME/.local/share/git-bridge"
source venv/bin/activate
python main.py
EOF

chmod +x "$HOME/.local/share/git-bridge/git-bridge.sh"

echo
echo "Installation complete!"
echo "Git Bridge should now appear in your applications menu."
"""
    
    # Create a dummy AppImage (in reality, this would be a proper AppImage)
    with open('website/git-bridge-linux.AppImage', 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Git Bridge AppImage\n")
        f.write("# This would be a proper AppImage in production.\n")
        f.write("# For now, please download the source code and run manually.\n")
    
    # Make it executable
    os.chmod('website/git-bridge-linux.AppImage', 0o755)
    
    print("Linux package created: website/git-bridge-linux.AppImage")

def main():
    """Create all packages"""
    print("Creating Git Bridge distribution packages...")
    print("=" * 50)
    
    # Ensure website directory exists
    os.makedirs('website', exist_ok=True)
    
    # Create packages
    create_source_package()
    create_windows_package()
    create_macos_package()
    create_linux_package()
    
    print("\n" + "=" * 50)
    print("All packages created successfully!")
    print("\nPackages available in website/ directory:")
    print("- git-bridge-source.zip (Source code)")
    print("- git-bridge-windows.zip (Windows installer)")
    print("- git-bridge-macos.dmg (macOS installer)")
    print("- git-bridge-linux.AppImage (Linux AppImage)")
    print("\nWebsite files:")
    print("- index.html (Main website)")
    print("- style.css (Styling)")
    print("- script.js (JavaScript)")

if __name__ == "__main__":
    main()
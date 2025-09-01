"""
Build executable for Git Bridge using PyInstaller
"""
import os
import subprocess
import sys

def build_executable():
    """Build Git Bridge executable"""
    print("Building Git Bridge executable...")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=GitBridge',
        '--icon=../favicon.ico',
        '--add-data=ui;ui',
        'main.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Build completed! Executable created in dist/ directory")
        
        # Move exe to current directory for download
        if os.path.exists('dist/GitBridge.exe'):
            import shutil
            shutil.copy('dist/GitBridge.exe', 'GitBridge.exe')
            print("Executable ready for download")
            
    except subprocess.CalledProcessError:
        print("Build failed. Make sure PyInstaller is installed: pip install pyinstaller")
    except FileNotFoundError:
        print("PyInstaller not found. Install with: pip install pyinstaller")

if __name__ == "__main__":
    build_executable()
# Building Git Bridge Executable

## Prerequisites
```bash
pip install pyinstaller
```

## Build Steps
1. Install PyInstaller: `pip install pyinstaller`
2. Run build script: `python build_exe.py`
3. Executable will be created in `dist/` and copied to `website/`

## Manual Build
```bash
pyinstaller --onefile --windowed --name=GitBridge --icon=../favicon.ico --add-data=ui;ui main.py
```

The executable will be available for download on the website.
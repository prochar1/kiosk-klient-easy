Kiosk desktop app (Flask + pywebview)

Quick start

1. Create virtualenv and install dependencies:

```powershell
# Create a project-local virtualenv (this repo uses `.venv312`)
python -m venv .venv312
& ".\.venv312\Scripts\Activate.ps1"
pip install -r requirements.txt
```

2. Run app locally:

```powershell
python main.py
```

The app starts a local webserver and opens a native window which loads the HTML from the `html/` folder.

Build single-file .exe with PyInstaller

Install PyInstaller into the active virtualenv and run the recommended build command:

```powershell
pip install pyinstaller
# recommended: clean build and put exe into `dist/`
pyinstaller --noconfirm --onefile --windowed --clean --distpath dist main.py
```

After the build, copy your `html` folder next to the produced EXE — the application requires an external `html/` directory at runtime and will exit with an error dialog if it's missing:

```powershell
# copy html into the dist folder next to the exe
Copy-Item -Recurse -Force .\html .\dist\html
```

Notes

- On Windows `pywebview` will use Microsoft Edge WebView2 — make sure the WebView2 runtime is installed on target machines.
  -- This project enforces using an external `html/` folder located next to the executable.
- Do NOT pass `--add-data` for `html` when building; instead distribute the `html` folder alongside the produced `main.exe`.
- Example packaging workflow:

```powershell
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed main.py
# After build, copy your html folder next to the produced exe:
# copy -Recurse html dist\html
```

-- Notes:

- The built EXE enforces using an external `html/` folder located next to the executable — do NOT pass `--add-data` for `html` when building. Distribute the `html` folder alongside `main.exe` (see copy example above).
- If `dist\html` is missing the EXE will show an error dialog and exit.
- On Windows `pywebview` will use Microsoft Edge WebView2 — make sure the WebView2 runtime is installed on target machines.

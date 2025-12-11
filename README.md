Kiosk desktop app (Flask + pywebview)

Quick start

1. Create virtualenv and install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Run app locally:

```powershell
python main.py
```

The app starts a local webserver and opens a native window which loads the HTML from the `html/` folder.

Build single-file .exe with PyInstaller

Install PyInstaller and run:

```powershell
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed main.py
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

- Notes: The built EXE will exit with an error if `dist\html` is missing. Ensure WebView2 runtime is installed on target machines.

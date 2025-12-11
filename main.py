import os
import sys
import threading
import socket
import time
from flask import Flask, send_from_directory, abort
import ctypes

try:
    import webview
except Exception:
    webview = None


def show_error_dialog(message, title='Error'):
    """Show a user-visible error dialog where possible, fallback to console.

    On Windows uses MessageBoxW; otherwise tries tkinter; finally prints.
    """
    # Try Windows MessageBox via ctypes
    try:
        if sys.platform.startswith('win'):
            ctypes.windll.user32.MessageBoxW(0, str(message), str(title), 0x00000010)
            return
    except Exception:
        pass

    # Fallback to tkinter if available
    try:
        from tkinter import Tk, messagebox
        root = Tk()
        root.withdraw()
        messagebox.showerror(title, str(message))
        root.destroy()
        return
    except Exception:
        pass

    # Last resort: print to console    try:
        print(title + ':', message)
    except Exception:
        pass


def find_free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    addr, port = s.getsockname()
    s.close()
    return port


def get_html_dir():
    # When the app is frozen (PyInstaller), prefer an external `html/`
    # directory located next to the executable. This allows distributing
    # the EXE separately from the HTML files.
    if getattr(sys, 'frozen', False):
        # When frozen, require an external `html/` directory located next to
        # the executable. Do NOT fall back to bundled resources — this enforces
        # that the EXE always reads HTML from the external folder.
        exe_dir = os.path.dirname(sys.executable)
        external_html = os.path.join(exe_dir, 'html')
        if os.path.isdir(external_html):
            return external_html
        show_error_dialog(f'Required external "html" folder not found at:\n{external_html}', 'Missing HTML folder')
        sys.exit(1)
    else:
        base = os.path.abspath(os.path.dirname(__file__))

    return os.path.join(base, 'html')


def create_app(html_dir):
    app = Flask(__name__, static_folder=None)

    @app.route('/', defaults={'path': 'index.html'})
    @app.route('/<path:path>')
    def serve(path):
        full = os.path.join(html_dir, path)
        if os.path.isfile(full):
            return send_from_directory(html_dir, path)
        else:
            abort(404)

    return app


def main():
    html_dir = get_html_dir()
    if not os.path.isdir(html_dir):
        show_error_dialog(f'html folder not found at:\n{html_dir}\n\nCreate a folder named "html" in the project directory (or next to the executable).', 'Missing HTML folder')
        sys.exit(1)

    port = find_free_port()
    app = create_app(html_dir)

    server_thread = threading.Thread(
        target=app.run,
        kwargs={
            'host': '127.0.0.1',
            'port': port,
            'threaded': True,
            'use_reloader': False,
        },
        daemon=True,
    )
    server_thread.start()

    # short wait for server to start
    time.sleep(0.4)

    url = f'http://127.0.0.1:{port}/'

    if webview is None:
        print('pywebview is not installed. Open the app in your browser at', url)
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass
        return

    # Kiosk mode: exact Full HD, borderless, non-resizable, positioned at (0,0).
    # Note: `frameless=True` makes the window borderless; `resizable=False` disables resizing.
    try:
        window = webview.create_window(
            'Kiosk App',
            url,
            width=1920,
            height=1080,
            x=0,
            y=0,
            resizable=False,
            min_size=(1920, 1080),
            frameless=True,
            shadow=False,
            on_top=True,
            easy_drag=False
        )
    except TypeError:
        # Fallback if `frameless` or positioning is not supported by the backend.
        window = webview.create_window('Kiosk App', url, width=1920, height=1080, resizable=False)

    webview.start()


if __name__ == '__main__':
    main()

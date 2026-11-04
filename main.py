import os
import sys
import threading
import socket
import time
from flask import Flask, send_from_directory, abort
import ctypes
from ctypes import wintypes

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
    # When the app is frozen (PyInstaller), look for content next to the
    # executable first, then in an external `html/` directory.
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        return exe_dir
    else:
        base = os.path.abspath(os.path.dirname(__file__))

    return base


def get_html_search_dirs():
    base_dir = get_html_dir()
    return [base_dir, os.path.join(base_dir, 'html')]


def find_existing_file(search_dirs, path):
    for directory in search_dirs:
        full = os.path.join(directory, path)
        if os.path.isfile(full):
            return directory, full
    return None, None


def get_launch_screen():
    if not sys.platform.startswith('win'):
        return None

    # Match the physical coordinates used by the Windows webview backend.
    ctypes.windll.user32.SetProcessDPIAware()
    position = wintypes.POINT()
    if not ctypes.windll.user32.GetCursorPos(ctypes.byref(position)):
        raise ctypes.WinError()

    for screen in webview.screens:
        if (screen.x <= position.x < screen.x + screen.width
                and screen.y <= position.y < screen.y + screen.height):
            return screen

    raise RuntimeError('No monitor found at the launch cursor position.')


def fit_window_to_screen(window, screen):
    if screen is None:
        return

    from System.Drawing import Rectangle

    # Bypass backend placement scaling, which can select the wrong monitor.
    window.native.Bounds = Rectangle(screen.x, screen.y, screen.width, screen.height)


def force_window_topmost(window):
    if not sys.platform.startswith('win'):
        return

    try:
        native = getattr(window, 'native', None)
        if native is None:
            return

        hwnd = native.Handle.ToInt32()
        swp_nomove = 0x0002
        swp_nosize = 0x0001
        swp_showwindow = 0x0040
        hwnd_topmost = -1

        ctypes.windll.user32.SetWindowPos(
            hwnd,
            hwnd_topmost,
            0,
            0,
            0,
            0,
            swp_nomove | swp_nosize | swp_showwindow,
        )
        ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception:
        pass


def create_app(html_dirs):
    app = Flask(__name__, static_folder=None)

    @app.route('/', defaults={'path': 'index.html'})
    @app.route('/<path:path>')
    def serve(path):
        directory, full = find_existing_file(html_dirs, path)
        if full is None:
            abort(404)
        return send_from_directory(directory, path)

    return app


def main():
    try:
        launch_screen = get_launch_screen() if webview is not None else None
    except (OSError, RuntimeError) as error:
        show_error_dialog(str(error), 'Monitor detection failed')
        sys.exit(1)

    html_dirs = get_html_search_dirs()
    if not any(os.path.isfile(os.path.join(directory, 'index.html')) for directory in html_dirs):
        show_error_dialog(
            'index.html not found in:\n' + '\n'.join(html_dirs) + '\n\nCreate index.html in the project root or in the html folder.',
            'Missing HTML file',
        )
        sys.exit(1)

    port = find_free_port()
    app = create_app(html_dirs)

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

    window = webview.create_window(
        'Kiosk App',
        url,
        screen=launch_screen,
        fullscreen=True,
        resizable=False,
        frameless=True,
        shadow=False,
        on_top=True,
        easy_drag=False,
    )

    window.events.before_show += lambda: fit_window_to_screen(window, launch_screen)
    window.events.shown += force_window_topmost

    webview.start()


if __name__ == '__main__':
    main()

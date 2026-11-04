import ctypes
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import main


class LaunchScreenTests(unittest.TestCase):
    def setUp(self):
        self.screens = [
            SimpleNamespace(x=0, y=0, width=2560, height=1440),
            SimpleNamespace(x=-1920, y=0, width=1920, height=1080),
            SimpleNamespace(x=2560, y=-1200, width=1920, height=1200),
        ]

    def select_screen(self, x, y, success=True):
        def get_cursor_pos(pointer):
            point = ctypes.cast(pointer, ctypes.POINTER(main.wintypes.POINT)).contents
            point.x, point.y = x, y
            return success

        user32 = Mock(GetCursorPos=Mock(side_effect=get_cursor_pos))
        with (
            patch.object(main.sys, 'platform', 'win32'),
            patch.object(main.ctypes, 'windll', SimpleNamespace(user32=user32), create=True),
            patch.object(main, 'webview', SimpleNamespace(screens=self.screens)),
        ):
            return main.get_launch_screen()

    def test_selects_monitor_under_cursor(self):
        for x, y, index in [(10, 10, 0), (-1, 100, 1), (3000, -100, 2)]:
            with self.subTest(x=x, y=y):
                self.assertIs(self.select_screen(x, y), self.screens[index])

    def test_shared_edge_belongs_to_monitor_starting_at_edge(self):
        self.assertIs(self.select_screen(0, 100), self.screens[0])

    def test_cursor_api_failure_is_reported(self):
        with self.assertRaises(OSError):
            self.select_screen(0, 0, success=False)

    def test_missing_monitor_is_reported(self):
        with self.assertRaisesRegex(RuntimeError, 'No monitor'):
            self.select_screen(9999, 9999)

    def test_other_platform_uses_default_fullscreen_monitor(self):
        with patch.object(main.sys, 'platform', 'linux'):
            self.assertIsNone(main.get_launch_screen())


if __name__ == '__main__':
    unittest.main()

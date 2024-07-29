import win32api, win32con

from ctypes import windll, byref
from ctypes.wintypes import HWND, POINT


class Mouse:

    def __init__(self):
        self.PostMessageW = windll.user32.PostMessageW
        self.ClientToScreen = windll.user32.ClientToScreen

        self.WM_MOUSEMOVE = 0x0200
        self.WM_LBUTTONDOWN = 0x0201
        self.WM_LBUTTONUP = 0x202
        self.WM_MOUSEWHEEL = 0x020A
        self.WHEEL_DELTA = 120

    def moveTo(self, handle: HWND, x: int, y: int):
        """移动鼠标到坐标（x, y)"""
        wparam = 0
        lparam = y << 16 | x
        self.PostMessageW(handle, self.WM_MOUSEMOVE, wparam, lparam)

    def leftDown(self, handle: HWND, x: int, y: int):
        """在坐标(x, y)按下鼠标左键"""
        wparam = 0
        lparam = y << 16 | x
        self.PostMessageW(handle, self.WM_LBUTTONDOWN, wparam, lparam)

    def leftUp(self, handle: HWND, x: int, y: int):
        """在坐标(x, y)放开鼠标左键"""
        wparam = 0
        lparam = y << 16 | x
        self.PostMessageW(handle, self.WM_LBUTTONUP, wparam, lparam)

    def click(self, handle: HWND, pos: tuple):
        self.leftDown(handle, pos[0], pos[1])
        self.leftUp(handle, pos[0], pos[1])

    def rightClick(self, handle: HWND, pos: tuple):
        # 没有找到ctypes后台鼠标右键单击的文档，这里使用win32api.SendMessage
        pos = win32api.MAKELONG(pos[0], pos[1])  # 模拟鼠标指针 传送到指定坐标
        win32api.SendMessage(handle, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, pos)  # 模拟鼠标按下
        win32api.SendMessage(handle, win32con.WM_RBUTTONUP, win32con.MK_RBUTTON, pos)  # 模拟鼠标弹起

    def scroll(self, handle: HWND, delta: int, x: int, y: int):
        """
            在坐标(x, y)滚动鼠标滚轮
            :param
                handle (HWND): 窗口句柄
                delta (int): 为正向上滚动，为负向下滚动
                x (int): 横坐标
                y (int): 纵坐标
        """
        self.moveTo(handle, x, y)
        wparam = delta << 16
        p = POINT(x, y)
        self.ClientToScreen(handle, byref(p))
        lparam = p.y << 16 | p.x
        self.PostMessageW(handle, self.WM_MOUSEWHEEL, wparam, lparam)

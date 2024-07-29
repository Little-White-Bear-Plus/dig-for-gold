import string
from ctypes import windll
from ctypes.wintypes import HWND


class Key:

    def __init__(self):
        self.PostMessageW = windll.user32.PostMessageW
        self.MapVirtualKeyW = windll.user32.MapVirtualKeyW
        self.VkKeyScanA = windll.user32.VkKeyScanA

        self.WM_KEYDOWN = 0x100
        self.WM_KEYUP = 0x101

        self.VkCode = {
            'back': 0x08,
            'tab': 0x09,
            'return': 0x0D,
            'shift': 0x10,
            'control': 0x11,
            'menu': 0x12,
            'pause': 0x13,
            'capital': 0x14,
            'escape': 0x1B,
            'space': 0x20,
            'end': 0x23,
            'home': 0x24,
            'left': 0x25,
            'up': 0x26,
            'right': 0x27,
            'down': 0x28,
            'print': 0x2A,
            'snapshot': 0x2C,
            'insert': 0x2D,
            'delete': 0x2E,
            'lwin': 0x5B,
            'rwin': 0x5C,
            '0': 0x60,
            '1': 0x61,
            '2': 0x62,
            '3': 0x63,
            '4': 0x64,
            '5': 0x65,
            '6': 0x66,
            '7': 0x67,
            '8': 0x68,
            '9': 0x69,
            'multiply': 0x6A,
            'add': 0x6B,
            'separator': 0x6C,
            'subtract': 0x6D,
            'decimal': 0x6E,
            'divide': 0x6F,
            'f1': 0x70,
            'f2': 0x71,
            'f3': 0x72,
            'f4': 0x73,
            'f5': 0x74,
            'f6': 0x75,
            'f7': 0x76,
            'f8': 0x77,
            'f9': 0x78,
            'f10': 0x79,
            'f11': 0x7A,
            'f12': 0x7B,
            'numlock': 0x90,
            'scroll': 0x91,
            'lshift': 0xA0,
            'rshift': 0xA1,
            'lcontrol': 0xA2,
            'rcontrol': 0xA3,
            'lmenu': 0xA4,
            'rmenu': 0XA5
        }

    def getVirtualKeycode(self, key: str):
        """根据按键名获取虚拟按键码"""
        if len(key) == 1 and key in string.printable:
            return self.VkKeyScanA(ord(key)) & 0xff
        else:
            return self.VkCode[key]

    def keyDown(self, handle: HWND, key: str):
        """按下指定按键"""
        vkCode = self.getVirtualKeycode(key)
        scanCode = self.MapVirtualKeyW(vkCode, 0)
        wparam = vkCode
        lparam = (scanCode << 16) | 1
        self.PostMessageW(handle, self.WM_KEYDOWN, wparam, lparam)

    def keyUp(self, handle: HWND, key: str):
        """松开指定按键"""
        vkCode = self.getVirtualKeycode(key)
        scanCode = self.MapVirtualKeyW(vkCode, 0)
        wparam = vkCode
        lparam = (scanCode << 16) | 0XC0000001
        self.PostMessageW(handle, self.WM_KEYUP, wparam, lparam)

    def press(self, handle: HWND, key: str):
        """按下并松开指定按键"""
        self.keyDown(handle, key)
        self.keyUp(handle, key)

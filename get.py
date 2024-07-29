import os

from core import Core
from base.window import *
from constant import *
from PIL import Image

"""
该文件有两个用途：
1.获取resource（图库）
2.测试core.compareImage，调整LIMIT参数
"""

# 这里直接通过大漠工具获取窗口句柄（手动更改）
windowList = [Window(i) for i in getWindowHwnd('#32770', 800, 600)]
mainWindow = WindowManage(windowList).setMainWindow()
totalGraph = mainWindow.screenShot([240, 40, 700, 500])
core = Core()
totalWidth, totalHeight = totalGraph.size
gridImages = core.splitImage(totalGraph, totalWidth/COL, totalHeight/ROW)

fileNumber = len(os.listdir('temp'))
for i in range(ROW):
    for j in range(COL):
        isExist = False
        # 不能将os.listdir('temp')定义为一个变量，因为定义出来的这个变量实际上是一个静态的值（文件夹发生变化时它不会跟着变化）
        for fileName in os.listdir('temp'):
            if compareImage(gridImages[(i, j)], Image.open('temp/' + fileName)):
                isExist = True
                break
        if not isExist:
            gridImages[(i, j)].save(f'temp/{fileNumber}.png')
            fileNumber += 1
            print('更新1张图片')

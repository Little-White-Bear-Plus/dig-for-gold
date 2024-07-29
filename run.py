import threading

from base.window import *
from core import *
from constant import *


class Run:

    def __init__(self):
        self.map = Map()
        self.core = Core()

        self.windowList = []  # 窗口列表
        self.mainWindow = None  # 主窗口

        self.resource = None  # 图库

        self.gridWidth = 0  # 单元格宽度
        self.gridHeight = 0  # 单元格高度

        self.newGridImages = []  # 图片经过映射之后得到的二维数组
        self.againList = []  # 需要重新映射的坐标集合

        self.coordinateList = {}  # 操作序列

        self.useItem = Image.open('other-images/useitem.png')
        self.gameOver = Image.open('other-images/gameover.png')
        self.timeIcon = Image.open('other-images/time.png')

    def bindWindow(self, className):
        """绑定窗口"""
        self.windowList = [Window(i) for i in getWindowHwnd(className, 800, 600)]
        self.mainWindow = WindowManage(self.windowList).setMainWindow()

    def runSrcipt(self, window: Window):
        while True:
            # 检测开始按钮是否按下，如果没有则点击按钮
            gameStart = window.screenShot([642, 570, 683, 592])
            if compareImage(gameStart, Image.open('other-images/gamestart.png'), limit=7):
                window.click((642 + 10, 570 + 10))

            if window == self.mainWindow:
                # 等待进入游戏界面
                while True:
                    timeIcon = window.screenShot([709, 80, 750, 96])
                    if compareImage(timeIcon, self.timeIcon, limit=2):
                        break
                    time.sleep(0.5)

                while True:
                    gameOver = window.screenShot([650, 144, 668, 162])
                    if compareImage(gameOver, self.gameOver, limit=2):
                        print('game over')
                        # 关闭分数窗口
                        window.click((650 + 5, 144 + 5))
                        # 初始化关键序列
                        self.newGridImages.clear()
                        self.againList.clear()
                        self.coordinateList.clear()
                        time.sleep(1)
                        break

                    useItem = window.screenShot([486, 317, 516, 331])
                    if compareImage(useItem, self.useItem, limit=2):
                        print('step on a step mine')
                        # 关闭提示窗口
                        window.click((486 + 10, 317 + 5))
                        # 初始化关键序列
                        self.newGridImages.clear()
                        self.againList.clear()
                        self.coordinateList.clear()
                        time.sleep(0.5)
                        continue

                    # 截取游戏区域，初始化单元格参数
                    totalGraph = window.screenShot([240, 40, 700, 500])
                    if self.gridWidth == 0:
                        totalWidth, totalHeight = totalGraph.size
                        self.gridWidth = totalWidth / COL
                        self.gridHeight = totalHeight / ROW

                    # 将游戏区域进行拆解（单元格集合）
                    gridImages = self.map.splitImage(totalGraph, self.gridWidth, self.gridHeight)

                    # 加载图库
                    if self.resource is None:
                        self.resource = loadResource()

                    timeStart = time.time()

                    # 测试运行时间发现，下行代码耗时巨大（甚至会超过2s）-- 必须优化
                    # self.newGridImages = self.map.mapping(self.resource, gridImages)

                    removeList = []

                    # 对映射失败的单元格进行重新映射
                    for pos in self.againList:
                        gridValue = self.map.posMapping(self.resource, gridImages, pos)
                        if gridValue != '?':
                            self.newGridImages[pos] = gridValue
                            removeList.append(pos)

                    # 将重新映射成功的单元格移出 againList 列表
                    for pos in removeList:
                        self.againList.pop(self.againList.index(pos))

                    if len(self.newGridImages) == 0:
                        # 实际上此时所有单元格都是'■'（初始单元格），mapping 耗时不高
                        self.newGridImages = self.map.mapping(self.resource, gridImages)
                    else:
                        # 改进之后，耗时只有0.02s，提升了100倍
                        for pos in self.coordinateList.keys():
                            # 操作数   0：插旗  1：点击  2：跳过
                            operand = self.coordinateList.get(pos)
                            if operand == 2:
                                continue
                            self.newGridImages, op = self.map.advancedMapping(self.resource, gridImages, self.newGridImages, pos)
                            if op == 0:
                                # 此时已经完成了对整个游戏图片的映射
                                break
                            elif op == -1:
                                # 爆金币动画导致映射失败（而且会连带到其上方单元格）
                                # 这里所作的处理就是重新截图，拆解，映射（实际上在动画持续时间段会一直失败）
                                self.againList.append(pos)
                                if 0 <= pos[0]-1 < ROW:
                                    self.againList.append((pos[0]-1, pos[1]))
                                break

                    if self.againList:
                        print('映射失败: ', self.againList)
                        time.sleep(0.25)
                        continue

                    self.coordinateList.clear()
                    print('time: ', time.time() - timeStart)

                    self.coordinateList = self.core.autoCalculate(self.newGridImages)
                    # 执行操作序列
                    for pos, op in self.coordinateList.items():
                        print("选定位置【%d, %d】, 操作为：%d" % (pos[0] + 1, pos[1] + 1, op))
                        x = int(self.gridWidth * (pos[1] + 0.5)) + 240
                        y = int(self.gridHeight * (pos[0] + 0.5)) + 40
                        if op == 0:
                            window.rightClick((x, y))
                        elif op == 1:
                            window.click((x, y))

                    # 这里必须给延迟，否则会导致重复截取到同一个游戏画面（反复执行同样操作）
                    # 网络影响很大，根据自己的情况进行调节
                    if len(self.coordinateList) == 1:
                        time.sleep(0.04)
                    else:
                        time.sleep(0.02)
            else:
                # 主窗口以外的窗口只需要一直等待直到游戏结束
                while True:
                    gameOver = window.screenShot([650, 144, 668, 162])
                    if compareImage(gameOver, self.gameOver, limit=2):
                        # print('game over')
                        window.click((650 + 5, 144 + 5))
                        break
                    time.sleep(0.5)
                time.sleep(1.2)


if __name__ == '__main__':
    run = Run()
    run.bindWindow('#32770')
    for window in run.windowList:
        # 想要控制线程需要加入stopEvent（threading.Event），将它作为主循环的条件
        threading.Thread(target=run.runSrcipt, args=(window,), daemon=True).start()
    while True:
        time.sleep(1)

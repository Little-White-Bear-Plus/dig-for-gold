import os
import random
import time

from PIL import Image
from constant import *
from base.window import compareImage


def loadResource():
    """加载单元格图片"""
    images = {}
    for fileName in os.listdir(RES_DIR):
        images[fileName.split('.')[0]] = Image.open(RES_DIR + f"/{fileName}")
    return images


class Map:

    def splitImage(self, totalGraph: Image.Image, gridWidth, gridHeight):
        """分割游戏图片并保存到二维数组中"""
        # 键：坐标  值：单个格子的图片
        posToImage = {}
        for i in range(ROW):
            for j in range(COL):
                gridLeft = j * gridWidth
                gridTop = i * gridHeight
                # crop 截取指定区域的图片
                gridImage = totalGraph.crop((gridLeft, gridTop, gridLeft+gridWidth,gridTop+gridHeight))
                posToImage[(i, j)] = gridImage
        return posToImage

    # 优化思路
    # 1、使用哈希表（即字典）完成查找操作，时间复杂度为常量级:
    #   由于Image对象不可哈希，所以可以做的就是拆解list；但是提升不明显，因为list的体量并不大
    # 2、在每次操作之后，只对操作可能改变的位置进行重新映射-->advancedMapping ☆☆☆
    def mapping(self, resource, girdImages):
        """完成整个游戏画面的映射"""
        isFind = False
        newImages = {}
        for i in range(ROW):
            for j in range(COL):
                # 遍历图库找到对应的图片并完成映射
                for k, v in resource.items():
                    if compareImage(v, girdImages[(i, j)]):
                        newImages[(i, j)] = MAP.get(k)
                        isFind = True
                        break
                if not isFind:
                    newImages[(i, j)] = '?'
                else:
                    isFind = False
        return newImages

    def posMapping(self, resource, girdImages, pos: tuple):
        """完成指定单元格的映射（需要保证pos是有效的--不能越界）"""
        for k, v in resource.items():
            if compareImage(v, girdImages[pos]):
                return MAP.get(k)
        return '?'

    def advancedMapping(self, resource, girdImages, newGridImages, pos: tuple):
        """
        只对操作可能改变的位置进行重新映射

        返回值中的数字表示需要进行的操作
        -1：映射失败，需要重新进行映射
        0：需要映射的区域未知，对整个图片进行映射
        1：映射完成
        """
        newGridImages[pos] = self.posMapping(resource, girdImages, pos)
        if newGridImages[pos] == '?':
            return newGridImages, -1
        posValue = newGridImages[pos]
        print('value: ', posValue)
        if posValue == 0:
            # posValue == 0 时，其影响是未知的，因此要对整个界面重新映射（此时的时间成本是最大的）
            return self.mapping(resource, girdImages), 0
        elif type(posValue) is int and posValue != 0:
            # posValue 是除0以外的其他数字时，只改变自身，不做其他操作
            return newGridImages, 1
        else:
            # 插旗，除本身以外还会影响其上方的单元格
            if 0 <= pos[0]-1 < ROW:
                newGridImages[(pos[0]-1, pos[1])] = self.posMapping(resource, girdImages, (pos[0]-1, pos[1]))
            return newGridImages, 1


class Core:

    def autoCalculate(self, newGridImages):
        # 操作序列（键：坐标，值：操作数）
        # 0：插旗      1：点击    2：跳过
        coordinateList = {}

        # 以先列后行的方式进行处理（效率会高一点）
        for j in range(COL):
            for i in range(ROW):
                gridValue = newGridImages[(i, j)]
                if type(gridValue) is int and gridValue > 0:
                    # POS_MAP 中记录的是偏移坐标（完成对目标单元格周围所有单元格的遍历）
                    for dx, dy in POS_MAP:
                        # 注意 x,y 与 i,j 的对应关系
                        x = j + dx
                        y = i + dy
                        if 0 <= x < COL and 0 <= y < ROW:
                            # '☠'：插过旗的单元格（地雷）
                            if newGridImages[(y, x)] == '☠':
                                gridValue -= 1
                            # '■'：初始单元格（未处理）
                            elif newGridImages[(y, x)] == '■':
                                # 记录初始单元格的坐标，默认操作数为 0
                                coordinateList.setdefault((y, x), 0)

                    # gridValue 最后的值是其周围目前没有被检测出的地雷数量
                    if gridValue == 0:
                        # 没有地雷
                        for pos in coordinateList.keys():
                            coordinateList[pos] = 1
                    elif gridValue == len(coordinateList):
                        # 全部是地雷
                        for pos in coordinateList.keys():
                            coordinateList[pos] = 0
                    else:
                        # 其他情况，需要清空操作序列（方案一只针对上述两种情况）
                        coordinateList.clear()

                    if coordinateList:
                        return coordinateList

        # 进入高级计算
        print("调用高级计算处理，请等候...")
        coordinateList = self.advancedCalculate(newGridImages)
        if coordinateList:
            return coordinateList
        else:
            # 这里可能会进入死循环（进入死局并且随机坐标对应的单元格不是初始单元格）
            # 可以加入一个数组，记录初始单元格的坐标（当然也可以手动点击）
            print("生成随机坐标")
            count = 0
            # 重置种子
            random.seed(time.time())
            x = random.randint(0, COL - 1)
            y = random.randint(0, ROW - 1)
            gridValue = newGridImages[(y, x)]
            while gridValue != '■':
                print('value: ', gridValue)
                if count >= 99:
                    # 2 表示 跳过
                    coordinateList.setdefault((-1, -1), 2)
                    return coordinateList
                random.seed(time.time())
                x = random.randint(0, COL - 1)
                y = random.randint(0, ROW - 1)
                count += 1
            coordinateList.setdefault((y, x), 1)
            return coordinateList

    def advancedCalculate(self, newGridImages):
        coordinateList = {}

        posSetToValue = {}  # 键：周围初始单元格的坐标集合  值：集合中存在地雷的数量
        processedList = newGridImages.copy()

        # 逻辑同上
        for j in range(COL):
            for i in range(ROW):
                gridValue = processedList[(i, j)]
                if type(gridValue) is int and gridValue > 0:
                    posSet = set()
                    for dx, dy in POS_MAP:
                        x = j + dx
                        y = i + dy
                        if 0 <= x < COL and 0 <= y < ROW:
                            if processedList[(y, x)] == '☠':
                                gridValue -= 1
                            elif processedList[(y, x)] == '■':
                                posSet.add((y, x))

                    if posSet:
                        # set 类型不可哈希，这里需要进行转换
                        posSetToValue[tuple(posSet)] = gridValue

        # 寻找存在包含关系的两个集合
        keyList = list(posSetToValue.keys())
        for i in range(len(keyList)):
            for j in range(i+1, len(keyList)):
                # p 始终为较小的集合，q 始终为较大的集合
                if len(keyList[i]) < len(keyList[j]):
                    p = i
                    q = j
                elif len(keyList[i]) > len(keyList[j]):
                    q = i
                    p = j
                else:
                    continue

                # 如果 q 区域包含 p 区域
                if set(keyList[p]).issubset(set(keyList[q])):
                    # deWeight 为 q 去除 p 后剩余的部分
                    deWeight = list(set(keyList[q]) - set(keyList[p]))
                    # 数字相等意味着deWeight中没有地雷（剩余没有检测到的地雷全部在 p 区域中）
                    if posSetToValue[keyList[q]] - posSetToValue[keyList[p]] == 0:
                        for d in deWeight:
                            coordinateList.setdefault(d, 1)
                    # 差值等于deWeight的长度意味着deWeight中全部都是地雷
                    elif posSetToValue[keyList[q]] - posSetToValue[keyList[p]] == len(deWeight):
                        for d in deWeight:
                            coordinateList.setdefault(d, 0)

        return coordinateList

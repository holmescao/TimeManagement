'''
Author: Holmescao
Date: 2021-04-02 22:56:30
LastEditors: Holmescao
LastEditTime: 2021-04-02 23:05:26
Description: 
'''

import os
from os import listdir
from PIL import Image


def pinjie():
    # 获取当前文件夹中所有JPG图像
    im_list = [Image.open(fn) for fn in listdir() if fn.endswith('.jpg')]

    # 图片转化为相同的尺寸
    ims = []
    for i in im_list:
        new_img = i.resize((550, 1280), Image.BILINEAR)
        ims.append(new_img)

    # 单幅图像尺寸
    width, height = ims[0].size

    # 创建空白长图
    result = Image.new(ims[0].mode, (width * len(ims), height))

    # 拼接图片
    for i, im in enumerate(ims):
        result.paste(im, box=(i*width, 0))

    # 保存图片
    captcha = result.convert('RGB')
    captcha.save('res1.jpg')


if __name__ == '__main__':
    os.remove('res1.jpg')
    pinjie()

- [TimeManagement](#timemanagement)
  - [前言](#前言)
  - [简介​​](#简介)
  - [功能](#功能)
    - [1. 提供记录文本模板：](#1-提供记录文本模板)
    - [2. 多维度可视化分析：](#2-多维度可视化分析)
  - [使用方法](#使用方法)
    - [极速演示版](#极速演示版)
    - [正常版](#正常版)
      - [1. 在markdown中记录当天情况](#1-在markdown中记录当天情况)
        - [1.1 计划部分](#11-计划部分)
        - [1.2 执行部分](#12-执行部分)
        - [1.3 复盘部分](#13-复盘部分)
          - [1.3.1 信息摄入部分](#131-信息摄入部分)
          - [1.3.2 收获部分](#132-收获部分)
      - [2. 运行脚本](#2-运行脚本)
        - [2.1 设定分析参数](#21-设定分析参数)
        - [2.2 运行程序](#22-运行程序)
  - [依赖](#依赖)
    - [1.软件](#1软件)
    - [2. python第三方库](#2-python第三方库)
  - [TODO](#todo)
# TimeManagement

## 前言

本项目的功能是本人10余年做个人时间管理的经验总结而成的，旨在提供<u>***高效、可量化、可复盘***</u>的时间管理工作流。欢迎大家提出更好的意见，助你成为时间管理大师！~

## 简介​​

本项目针对个人每日规划和执行情况，提供了记录文本模板（基于`typora`的markdown文件），基于markdown里的内容，通过运行脚本进行数据处理，并提供多维度可视化分析。此外，分析结果会自动插入到每日计划的markdown文件中。

tips：下载源码解压后，进入`src`目录，直接运行`schedule_analysis.py --demo True`，即可在`'./demo/schedule/'`下得到可视化分析后的示例markdown文档。

## 功能

### 1. 提供记录文本模板：

**markdown文件，以`xxxx年xx月xx日.md`命名**

- 模板中包括计划、执行、复盘 3个部分
- 每个部分的记录方式都给出了示例

### 2. 多维度可视化分析：

**程序会根据你在markdown的记录内容，自动分析你最近的投入（学习/工作）情况。**

可视化维度如下：

- 投入情况
  - 每小时的投入时长（当天）
  
  - 每时每刻在做什么任务（近7天）
  
  - 一天之中投入时长的概率分布（近7天）
  
  - 当日投入总时长（近30天）
  - 各类别任务投入比例（近30天）
	<center class='half'>
    <img src='https://github.com/holmescao/TimeManagement/blob/main/src/demo/output/figure/Figure1/Figure1-activate-bar-20210326_20210326.png' width="250" height="200"' />
    <img src='https://github.com/holmescao/TimeManagement/blob/main/src/demo/output\figure\Figure2\Figure2-activate-brokenbarh-20210320_20210326.png' width="250" height="200"' />
    <img src='https://github.com/holmescao/TimeManagement/blob/main/src/demo/output\figure\Figure3\Figure3-activate-waterfall-20210320_20210326.png' width="250" height="200"' />
    <img src='https://github.com/holmescao/TimeManagement/blob/main/src/demo/output\figure\Figure4\Figure4-activate-bar-20210225_20210326.png' width="250" height="200"' />
    <img src='https://github.com/holmescao/TimeManagement/blob/main/src/demo/output\figure\Figure5\Figure5-investment-pie-20210225_20210326.png' width="400" height="200"' />
    </center>
  
- 信息摄入情况：
  - 高、中、低质量信息摄入比例（当天）
  - 高、中、低质量信息摄入时长（当天）
  - 高、中、低质量信息摄入比例、高质量信息占比（近30天）
  <center class='half'>
    <img src='https://github.com/holmescao/TimeManagement/blob/main/src/demo/output/figure/Figure6\Figure6-dayinformation-pie-20210326_20210326.png' width="250" height="200"' />
    <img src='https://github.com/holmescao/TimeManagement/blob/main/src/demo/output/figure/Figure7\Figure7-dayinformation-stackbar-20210326_20210326.png' width="250" height="200"' />
    <img src='https://github.com/holmescao/TimeManagement/blob/main/src/demo/output/figure/Figure8\Figure8-monthinformation-stackbar-20210225_20210326.png' width="250" height="200"' />
    </center>
  
- 收获情况：
  
  - 各类收获对比、排序（近30天）

  <center class='half'>
    <img src='https://github.com/holmescao/TimeManagement/blob/main/src/demo/output/figure/Figure9\Figure9-harvest-cloud-20210225_20210326.png' width="250" height="200"' />
    <img src='https://github.com/holmescao/TimeManagement/blob/main/src/demo/output/figure/Figure10\Figure10-harvest-vbar-20210225_20210326.png' width="250" height="200"' />
  </center>
## 使用方法

### 极速演示版

下载源码解压后，进入`src`目录，直接运行`schedule_analysis.py --demo True`，即可在`'./demo/schedule/'`下得到可视化分析后的示例markdown文档。

### 正常版

#### 1. 在markdown中记录当天情况

##### 1.1 计划部分

每个任务的写法为：标签+内容，如`[learn] 学会使用 TimeManagement项目的使用。 100%完成`

```python
### 一、计划

可选任务标签：['learn', 'paper', 'write', 'think', 'code', 'survey', 'material', 'discussion', 'meeting', 'extra']

1. [learn] 学会使用TimeManagement项目的使用。 100% 预计1小时 （~~若执行完可以划掉~~）
2. [extra] 临时额外因素
3. [think] 复盘。100% 预计0.4小时
```

tips：执行每日计划时，经常会出现一些临时任务、突发事件，导致你无法完成既定计划。考虑这类情况，可以使用`extra`这个额外因素的任务。

##### 1.2 执行部分

每次执行都要记录开始和结束时间，写法为：任务序号@ 开始时间 to 结束时间，如：`1@ 10:00:00 to 11:00:00`

```python
### 二、执行

1@ 09:34:38 to 10:51:17
```

##### 1.3 复盘部分

包括信息摄入和收获的记录

###### 1.3.1 信息摄入部分

记录h（高）、m（中）、l（低）质量信息摄入情况，写法为：信息质量-信息来源-时长（分钟），如`h-书-10m`

```python
#### 3. 信息摄入

h-书-10m

m-文章-5m

l-娱乐八卦-15m
```

note：信息质量只能是`h\m\l`三种，但中间的信息来源可以自选

###### 1.3.2 收获部分

记录每天的收获，写法为：二级标签+链接，如`software.convenient [你收获的地址]`

```python
#### 4. 收获

(如有则填写，规则为：二级标签+链接，eg：code.leetcode [link])

- software.convenient [https://github.com/holmescao/TimeManagement#timemanagement]
```

#### 2. 运行脚本

##### 2.1 设定分析参数

- 修改文件路径
  - 打开`config.py`文件，修改`config.path.root_path`为你存放每日计划文件的路径，默认为`'./schedule/daily/'`
- 选择待分析内容
  - 在`schedule_analysis.py`程序中，设置参数`activate\infomation\harvest`，来选择需要分析的内容。默认是都分析
- 设定要分析的日期
  - 在`schedule_analysis.py`程序中，设置参数`today_dt`，来决定分析哪天的内容。默认为当天

##### 2.2 运行程序

- 运行`schedule_analysis.py`，等待20秒内即可获得所有分析结果。分析结果会自动插入到markdown文件中，并会备份存在`./output/figure/`目录下。

## 依赖

### 1.软件

`typora`(下载链接：https://typora.io/)

### 2. python第三方库

- wordcloud

- joypy

- openpyxl

以上package均可通过`pip install xxx`实现快速安装

如果安装速度过慢，可以换源，即采用如下命令：

`pip install xxx -i https://pypi.tuna.tsinghua.edu.cn/simple/ `

## TODO

1. 在投入那边，把当天各个标签执行总时长和预计总时长画柱状图，其中预计总时长用背景阴影，谁长就谁在底部


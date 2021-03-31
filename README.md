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
# TimeManagement

## 前言

当前市场的时间管理方法、工具均是面向执行前和执行时的管理，但如何对每天的执行情况进行`复盘、分析`，并没有一个好的辅助工具。

本人总结了自己10余年个人时间管理的经验，包括中学时代开始实践schedule用于日常学习，到研究生阶段用于科研，再到腾讯AI Lab实习期间用于项目推进，一步步完善我的时间管理、复盘方式。

基于本人长年累月的实践经验，设计并开发了该项目，旨在为更多的人提供标准化的<u>***高效、可量化、可复盘***</u>的时间管理、复盘工作流，助你成为时间管理大师！

欢迎大家提出改进意见~

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
  - 24小时任务监控（近7天）
  - 投入时间段概率分布（近7天）
  - 每日投入总时长（近30天）
  - 各类别任务投入比例（近30天）
  - 各任务投入与预测时间对比（当天）
  - 任务执行次数统计（近12个月）

<center class='half'>
	<img src='https://gitee.com/holmescao/figure-bed/raw/master/20210331200407.png' width="100"' />
	<img src='https://gitee.com/holmescao/figure-bed/raw/master/20210331200342.png' width="100"' />
	<img src='https://gitee.com/holmescao/figure-bed/raw/master/20210331200343.png' width="100"' />
	<img src='https://gitee.com/holmescao/figure-bed/raw/master/20210331200344.png' width="250" height="200"' />
	<img src='https://gitee.com/holmescao/figure-bed/raw/master/20210331200345.png' width="250" height="160"' />
	<img src='https://gitee.com/holmescao/figure-bed/raw/master/20210331200346.png' width="250" height="200"' />
	<img src='https://gitee.com/holmescao/figure-bed/raw/master/20210331200347.png' width="650" height="200"' />    
</center>


- 信息摄入情况：
  - 高、中、低质量信息摄入比例（当天）
  - 高、中、低质量信息摄入时长（当天）
  - 高、中、低质量信息摄入比例、高质量信息占比（近30天）
  
  
<center class="half">
	<img src='https://gitee.com/holmescao/figure-bed/raw/master/Figure1-dayinformation-pie-20210331_20210331.png' width="250" height="200"' />
	<img src='https://gitee.com/holmescao/figure-bed/raw/master/Figure2-dayinformation-stackbar-20210331_20210331.png' width="250" height="200"' />
	<img src='https://gitee.com/holmescao/figure-bed/raw/master/Figure3-monthinformation-stackbar-20210302_20210331.png' width="250" height="200"' />      
</center>



- 收获情况：
  
  - 各类收获概览、统计（近365天）

<center class="half">
	<img src='https://gitee.com/holmescao/figure-bed/raw/master/Figure1-harvest-cloud-20200401_20210331.png' width="250" height="200"' />
	<img src='https://gitee.com/holmescao/figure-bed/raw/master/Figure2-harvest-vbar-20200401_20210331.png' width="250" height="200"' />  
</center>


## 使用方法

### 极速演示版

下载源码解压后，进入`src`目录，直接运行`schedule_analysis.py --demo True`，即可在`'./demo/schedule/'`下得到可视化分析后的示例markdown文档。

### 正常版

#### 1. 在markdown中记录当天情况

##### 1.1 计划部分

你需要在如下表格中填写当天的每项计划任务的信息。

除了`extra`任务标签外，其余的任务每一列均要填写内容

可选任务标签：['learn', paper', 'write', 'think', 'code', 'survey', 'material', 'discussion', 'meeting', 'extra']

| 任务序号 | 任务标签 | 任务描述                         | 预计完成率（%） | 预计时长（小时） | 是否可选 |
| -------- | -------- | -------------------------------- | --------------- | ---------------- | -------- |
| 1        | learn    | 学会使用TimeManagement项目的使用 | 100             | 1                | 否       |
| 2        | extra    | 临时额外因素                     |                 |                  | 否       |
| 3        | think    | 复盘                             | 100             | 0.4              | 是       |
|          |          |                                  |                 |                  |          |

*注：`extra`的临时额外因素是为了记录每天突发的需求，这不属于计划范围，所以不考虑完成率和时长。*

##### 1.2 执行部分

你需要在如下表格中填写每次执行的任务序号和起止时刻

| 任务序号 | 开始时刻 | 结束时刻 |
| -------- | -------- | -------- |
| 2        | 09:34:38 | 10:51:17 |
| 1        | 12:51:17 | 13:51:17 |
| 2        | 14:00:00 | 15:00:00 |
| 3        | 15:51:17 | 18:51:17 |

*注：一个任务可以执行多次，这里只是记录你在哪个时间段做了什么事。*

##### 1.3 复盘部分

包括信息摄入和收获的记录

###### 1.3.1 信息摄入部分

你需要在如下表格中填写当天的信息摄入情况。

信息质量为：高（h）、中（m）、低（l）3种，在表格的`信息质量`那列请填写首字母

（请不要删除该表格，如果今天未摄入信息，则把相应行的`时长`列的数值改为0即可）

| 信息质量 | 信息源类别 | 时长（分钟） |
| -------- | ---------- | ------------ |
| h        | 书籍       | 10           |
| m        | 文章       | 5            |
| l        | 娱乐八卦   | 15           |

###### 1.3.2 收获部分

你需要在如下表格中填写当天的收获情况。

(如有则填写，否则请在当天结束前清空或删除该表格)

| 一级标签 | 二级标签   | 访问链接（如有）                                           |
| -------- | ---------- | ---------------------------------------------------------- |
| software | convenient | https://github.com/holmescao/TimeManagement#timemanagement |
| code     | convenient | https://github.com/holmescao/TimeManagement#timemanagement |
| learn    | convenient | https://github.com/holmescao/TimeManagement#timemanagement |

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


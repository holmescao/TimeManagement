'''
Author: Holmescao
Date: 2021-03-13 16:41:06
LastEditors: Holmescao
LastEditTime: 2021-03-30 10:17:44
Description: schedule数据处理模块，包含对执行信息、信息摄入、收获3种类型信息的处理。
'''


import os
import datetime
import re
import pandas as pd
from utils.common_function import *


class Schedule:
    """处理schedule文件中的时间管理信息"""

    def __init__(self, args, root_path, tmp_path, data_columns):
        """初始化

        Args:
            args ([type]): 主要包括待处理的信息类别
            root_path ([type]): 待处理的文件路径
            tmp_path ([type]): 数据处理结果的保存路径
            data_columns ([type]): 包含不同信息类别的属性
        """
        self.args = args
        self.root_path = root_path
        self.tmp_path = tmp_path
        self.data_columns = data_columns

        self.scheduleFlag = '### 一、计划\n'
        self.carryFlag = '### 二、执行\n'
        self.reviewFlag = '### 三、复盘\n'

        mkdir(tmp_path)

    @property
    @class_func_timer("Schedule")
    def HandleDailySchedule(self):
        """处理每日schedule文件
        """
        files_path = GetFilePath(self.root_path)
        pre_files_path = GetFilePath(self.tmp_path)

        self.ExtractandSaveSchedule(files_path, pre_files_path)

    def ExtractandSaveSchedule(self, files_path, pre_files_path):
        """提取和保存schedule文件中的信息

        Args:
            files_path ([list]): schedule文件路径
            pre_files_path ([list]): 已处理的schedule文件的数据结果路径
        """
        exist_files = '_'.join(pre_files_path)

        for file in files_path:
            self.date = ExtractDateFromStr(file)
            # avoid redundant process, except today's file
            if (self.date not in exist_files) or (self.date == str(self.args.today_dt)):
                self.context = OpenFile(file)

                # process data
                df_list = []
                if self.args.activate:
                    df_list.append((self.GetActivate, 'activate'))

                if self.args.information:
                    df_list.append((self.GetInformation, 'information'))

                if self.args.harvest:
                    df_list.append((self.GetHarvest, 'harvest'))

                # save data
                SaveToExcel(df_list,
                            save_path=os.path.join(self.tmp_path, self.date+'.xlsx'))

    @property
    def GetActivate(self):
        """获取activate类别信息

        Returns:
            [type]: activate类别信息
        """
        startIdx = GetFlagIdx(self.context, self.carryFlag)
        endIdx = GetFlagIdx(self.context, self.reviewFlag)
        datetime_label_pairs = self.GetDateTimeAndLabelPair(startIdx, endIdx)

        activate = pd.DataFrame(datetime_label_pairs,
                                columns=self.data_columns['activate'])

        return activate

    def GetDateTimeAndLabelPair(self, startIdx, endIdx,
                                planlabelFlag='. ', carrylabelFlag='@', timeSep='to'):
        """获取文本中的时间和标签

        Args:
            startIdx ([type]): 起始索引
            endIdx ([type]): 结束索引
            planlabelFlag (str, optional): [description]. Defaults to '. '.
            carrylabelFlag (str, optional): [description]. Defaults to '@'.
            timeSep (str, optional): [description]. Defaults to 'to'.

        Returns:
            [list]: 时间和标签对
        """
        datetime_label_pairs = []
        for idx in range(startIdx, endIdx):
            line = self.context[idx]
            if timeSep in line:
                # find time period
                time_re_str = r"\d{1,2}:\d{1,2}:\d{1,2}"
                time_regex = re.compile(time_re_str)
                time_period = time_regex.findall(line)

                # change strptime format
                assert len(time_period) == 2, "必须在`执行`中输入`开始`、`结束`的时间段"
                startTime = datetime.datetime.strptime(
                    self.date+" "+time_period[0], "%Y-%m-%d %H:%M:%S")
                endTime = datetime.datetime.strptime(
                    self.date+" "+time_period[1], "%Y-%m-%d %H:%M:%S")

                # duration
                duration = (endTime - startTime).seconds

                #  location label idx
                labelFlagIdx = line.find(carrylabelFlag)
                taskId = line[:labelFlagIdx]
                carryIdx = self.context.index(self.scheduleFlag) + 1
                findtask = False
                while not findtask:
                    if taskId+planlabelFlag in self.context[carryIdx]:
                        taskIdx = carryIdx
                        findtask = True
                    else:
                        carryIdx += 1

                task_line = self.context[taskIdx]

                # match label
                label_re_str = "(\\[).*?(\\])"
                span_ = re.search(label_re_str, task_line).span()
                label_ = task_line[span_[0]:span_[1]]
                span = re.search(r"\w+", label_).span()
                label = label_[span[0]:span[1]]

                # task id
                taskId = int(taskId)

                # match predict time
                try:
                    predTime_re_str = "预计(.*)小时"
                    span = re.search(predTime_re_str, task_line).span()
                    predTime_ = task_line[span[0]:span[1]]
                    predTime = float(re.findall(r"\d+\.?\d*", predTime_)[0])
                except Exception:
                    predTime = 0

                # option task
                option = False
                if "[可选]" in task_line:
                    option = True

                # append record
                datetime_label_pairs.append(
                    [self.date, startTime, endTime, duration, label, taskId, predTime, option])

        return datetime_label_pairs

    @property
    def GetInformation(self):
        """获取information类别信息

        Returns:
            [type]: information类别信息
        """
        Idx = GetFlagIdx(self.context, self.reviewFlag)
        information_quality_pairs = self.GetDateInformationQualityPair(Idx)

        information = pd.DataFrame(information_quality_pairs,
                                   columns=self.data_columns['information'])

        return information

    def GetDateInformationQualityPair(self, Idx):
        """获取文本中的信息源

        Args:
            Idx ([type]): 开始处理的索引

        Returns:
            [list]: 信息源数据
        """
        information_quality_pairs = []
        for idx in range(Idx, len(self.context)):
            line = self.context[idx]
            try:
                # extract columns
                re_str = r"[hml]-(.*)-\d{1,4}"
                m = re.search(re_str, line)
                string = m.group(0)
                str_list = string.split("-")

                # append record
                quality = str_list[0]
                assert quality in 'hml', u"信息质量填写有误，只能是'h','m','l'"

                if quality == 'h':
                    quality = 'high'
                elif quality == 'm':
                    quality = 'middle'
                elif quality == 'l':
                    quality = 'low'

                label = str_list[1]
                duration = int(str_list[2])
                information_quality_pairs.append(
                    [self.date, quality, duration, label])
            except AttributeError:
                continue

        return information_quality_pairs

    @property
    def GetHarvest(self):
        """获取harvest类别信息

        Returns:
            [type]: harvest类别信息
        """
        Idx = GetFlagIdx(self.context, self.reviewFlag)
        harvest_label = self.GetDateHarvest(Idx)

        harvest = pd.DataFrame(harvest_label,
                               columns=self.data_columns['harvest'])

        return harvest

    def GetDateHarvest(self, Idx):
        """获取文本中的收获信息

        Args:
            Idx ([type]): 开始处理的索引

        Returns:
            [list]: 收获数据
        """
        harvest = []
        for idx in range(Idx, len(self.context)):
            line = self.context[idx]
            try:
                # extract harvest string
                re_str = "- (.*).(.*) \\[(.*)\\]"
                m = re.search(re_str, line)
                string = m.group(0)
                # del link
                link_idx = string.index('[')
                string = string[:link_idx]

                # extract label
                label_str = "\w{1,100}"
                regex = re.compile(label_str)
                label_list = regex.findall(string)

                # append record
                label1 = label_list[0]
                label2 = label_list[1]
                harvest.append([self.date, label1, label2])

            except AttributeError:
                continue

        return harvest

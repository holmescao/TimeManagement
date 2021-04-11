'''
Author: Holmescao
Date: 2021-03-13 16:41:06
LastEditors: Holmescao
LastEditTime: 2021-04-11 14:14:39
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
        files_path = GetFilePath(self.root_path, suffix='.md')
        pre_files_path = GetFilePath(self.tmp_path, suffix='.xlsx')

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

    def GetDateTimeAndLabelPair(self, startIdx, endIdx):
        """获取文本中的时间和标签

        Args:
            startIdx ([type]): 起始索引
            endIdx ([type]): 结束索引

        Returns:
            [list]: 时间和标签对
        """
        datetime_label_pairs = []
        for idx in range(startIdx, endIdx):
            line = self.context[idx].replace(" ", "")
            record = r"\|\d{1,2}\|\d{1,2}:\d{1,2}:\d{1,2}\|\d{1,2}:\d{1,2}:\d{1,2}\|"
            m = re.search(record, line)
            if m is not None:
                # find time period
                time_re_str = r"\d{1,2}:\d{1,2}:\d{1,2}"
                time_regex = re.compile(time_re_str)
                time_period = time_regex.findall(line)

                # change strptime format
                assert len(time_period) == 2, "必须在`执行`中输入`开始时刻`、`结束时刻`的时间对"
                startTime = datetime.datetime.strptime(
                    self.date+" "+time_period[0], "%Y-%m-%d %H:%M:%S")
                endTime = datetime.datetime.strptime(
                    self.date+" "+time_period[1], "%Y-%m-%d %H:%M:%S")

                # duration
                duration = (endTime - startTime).seconds

                #  location task idx
                task_re_str = r'\d{1,2}'
                m = re.search(task_re_str, line)
                try:
                    taskId = m.group(0)
                except Exception:
                    print("请在`执行`表格中输入任务序号")
                    sys.exit()
                carryIdx = self.context.index(self.scheduleFlag) + 1
                findtask = False
                while not findtask:
                    schedule_task_re_str = r'\|%s\|(.*)\|(.*)\|(.*)\|(.*)\|(.*)\|' % taskId
                    string = self.context[carryIdx].replace(
                        " ", "").strip("\n")
                    m = re.search(schedule_task_re_str, string)
                    if m is not None:
                        taskLoc = carryIdx
                        findtask = True
                    else:
                        carryIdx += 1

                task_line = self.context[taskLoc].replace(" ", "")

                # split elements
                plan_list = task_line.strip("\n").split("|")[1:-1]
                label = plan_list[1]
                predTime = plan_list[4]
                optional = plan_list[5]

                taskId = int(taskId)
                predTime = float(predTime) if len(predTime) > 0 else 0
                option = True if "是" in optional else False

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
            line = self.context[idx].replace(" ", "")
            re_str = r"\|[hml]\|"
            m = re.search(re_str, line)
            if m is not None:
                record_list = line.strip("\n").split("|")[1:-1]

                # append record
                quality = record_list[0]
                assert quality in 'hml', u"信息质量填写有误，只能是'h','m','l'"

                if quality == 'h':
                    quality = 'high'
                elif quality == 'm':
                    quality = 'middle'
                elif quality == 'l':
                    quality = 'low'

                label = record_list[1]
                duration = int(record_list[2])
                information_quality_pairs.append(
                    [self.date, quality, duration, label])

        return information_quality_pairs

    @property
    def GetHarvest(self):
        """获取harvest类别信息

        Returns:
            [type]: harvest类别信息
        """
        Idx = GetFlagIdx(self.context, "#### 4. 收获\n")
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
            line = self.context[idx].replace(" ", "")
            re_str = r"\|([a-zA-Z_]){1,100}\|([a-zA-Z_]){1,100}\|"
            m = re.search(re_str, line)
            if m is not None:
                label_list = line.strip("\n").split("|")[1:-1]
                label1 = label_list[0]
                label2 = label_list[1]

                harvest.append([self.date, label1, label2])

        return harvest

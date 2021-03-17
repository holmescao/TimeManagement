'''
Author: Holmescao
Date: 2021-03-16 13:22:08
LastEditors: Holmescao
LastEditTime: 2021-03-16 17:22:43
Description: 用于时间管理分析的通用函数
'''
import numpy as np
import pandas as pd
import re
import datetime
import time
import os


def class_func_timer(class_name):
    """用装饰器实现函数计时

    Args:
        class_name ([type]): 类名

    Returns:
        [type]: 函数调用结果
    """

    def deco(function):
        def wrapper(*args, **kwargs):
            print('[Class: {class_name}, Function: {name} start...]'.format(class_name=class_name,
                                                                            name=function.__name__))
            t0 = time.time()
            result = function(*args, **kwargs)
            function(*args, **kwargs)
            t1 = time.time()
            print('[Class: {class_name}, Function: {name} finished, spent time: {time:.2f}s]'.format(class_name=class_name,
                                                                                                     name=function.__name__, time=t1 - t0))

            return result

        return wrapper

    return deco


def mkdir(path):
    """创建路径

    Args:
        path ([type]): 路径名
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def ExtractDateFromStr(string):
    """从包含日期的字符串中提取日期

    Args:
        string ([type]): 包含日期的字符串

    Returns:
        [type]: xxxx-xx-xx格式的日期
    """
    string = string.replace("年", "-")
    string = string.replace("月", "-")
    string = string.replace("日", "-")
    date_re_str = r"(\d{4}-\d{1,2}-\d{1,2})"
    match = re.search(date_re_str, string)
    date = match.group(1)

    date = datetime.datetime.strptime(
        date, "%Y-%m-%d").strftime("%Y-%m-%d")

    return date


def GetFlagIdx(context, flag):
    """获取文本列表中满足指定字符串的索引

    Args:
        context ([type]): 文本列表
        flag ([type]): 指定字符串

    Returns:
        [type]: 索引
    """

    return context.index(flag)


def GetFilePath(root_path):
    """获取路径下所有文件

    Args:
        root_path ([str]): 根路径

    Returns:
        [list]: 所有文件的相对路径
    """
    files_path = []
    for root, _, files in os.walk(root_path):
        for file in files:
            file_path = os.path.join(root, file)
            files_path.append(file_path)

    return sorted(files_path)


def OpenFile(file):
    """打开文件，并读取文件内容

    Args:
        file ([type]): 文件路径

    Returns:
        [type]: 文件内容
    """
    try:
        with open(file, mode='r', encoding='gbk') as f:
            context = f.readlines()
    except Exception:
        with open(file, mode='r', encoding='utf-8') as f:
            context = f.readlines()

    return context


def SaveToExcel(df_list, save_path):
    """将dataframe数据保存到同一个excel文件的不同sheet_name中

    Args:
        df_list ([type]): 每个元素为：(df,sheet_name)
        save_path ([type]): 保存的excel相对路径
    """

    with pd.ExcelWriter(save_path) as writer:
        for df_sheet in df_list:
            df = df_sheet[0]
            sheet_name = df_sheet[1]
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def DatetimeToSecond(dt):
    seconds = dt.hour * 3600 + dt.minute * 60 + dt.second

    return seconds


def GetNDayList(n):
    before_n_days = []
    for i in range(n)[::-1]:
        before_n_days.append(
            str(datetime.date.today() - datetime.timedelta(days=i)))
    return before_n_days


def ActivateSecondsPerHour(current_date_data):
    point = 0
    length = len(current_date_data)
    hour = 0

    activate = np.zeros(24)
    while hour < 24:
        lower_bound = hour*3600
        upper_bound = (hour+1)*3600

        InHour = True
        while InHour and (point < length):
            startTime = current_date_data[point][0]
            endTime = current_date_data[point][1]
            if (startTime <= lower_bound < endTime):
                if upper_bound >= endTime:
                    activate[hour] += endTime - lower_bound
                    point += 1
                elif upper_bound < endTime:
                    activate[hour] = 3600
                    InHour = False
            elif lower_bound <= startTime:
                if upper_bound >= endTime:
                    activate[hour] += endTime - startTime
                    point += 1
                elif startTime < upper_bound < endTime:
                    activate[hour] += upper_bound - startTime
                    InHour = False
                elif upper_bound <= startTime:
                    InHour = False
            else:
                InHour = False

        hour += 1

    return list(activate)


def LastNdayActivateTime(df, back_days):
    # datetime to second
    startSecond = df['startTime'].apply(DatetimeToSecond)
    endSecond = df['endTime'].apply(DatetimeToSecond)
    tuple_of_Activate = tuple(zip(startSecond, endSecond))

    NdayActivateTime = []
    date_list = GetNDayList(back_days)
    for date in date_list:
        idx = df[df['date'].str.contains(date)].index
        if len(idx) > 0:
            # activate
            stIdx, edIdx = idx[0], idx[-1]
            current_date_data = tuple_of_Activate[stIdx:edIdx+1]
            activate = ActivateSecondsPerHour(current_date_data)

            NdayActivateTime.append(activate)
        else:
            NdayActivateTime.append([0]*24)

    return NdayActivateTime


def generate_fig_path(date_list, root_path, fig_id, fig_name):
    startdate = date_list[0].replace("-", "")
    enddate = date_list[-1].replace("-", "")

    fig_save_path = os.path.join(root_path, 'figure/Figure%s' % fig_id)
    mkdir(fig_save_path)
    fig_path = fig_save_path + \
        f'/Figure{fig_id}-{fig_name}-{startdate}_{enddate}.png'

    fig_abs_path = os.path.abspath(fig_path)

    return fig_abs_path


def InsertFigureToFile(fig_path, output_file_path, addFlag):
    lines = OpenFile(output_file_path)

    try:
        InsertIdx = lines.index(addFlag) + 1
    except Exception:
        InsertIdx = lines.index(addFlag+'\n') + 1

    # grammar: figure insert to markdown
    fig_grammar = f"<img src='{fig_path}' style='zoom:20%;' />\n"
    exist_Figure_flag = "<center class='half'>\n"
    end_flag = "</center>\n"

    if exist_Figure_flag not in lines[InsertIdx]:
        lines.insert(InsertIdx, exist_Figure_flag)
        lines.insert(InsertIdx + 1, fig_grammar)
        lines.insert(InsertIdx + 2, end_flag)
    else:
        # avoid redunant insert
        if fig_grammar not in lines:
            find = False
            while not find:
                if end_flag in lines[InsertIdx]:
                    find = True
                else:
                    InsertIdx += 1

            lines.insert(InsertIdx, fig_grammar)
        else:
            InsertIdx = lines.index(fig_grammar)
            lines[InsertIdx] = fig_grammar

    # insert
    with open(output_file_path, mode='w', encoding='utf-8')as fp:
        fp.writelines(lines)


def GetRecentData(self, sheet_name):
    last_day = self.GetLastData(1,  sheet_name)
    last_week = self.GetLastData(7, sheet_name)
    last_month = self.GetLastData(30, sheet_name)

    return last_day, last_week, last_month


def GetLastData(self, back_day, sheet_name, suffix='.xlsx'):
    today_dt = datetime.date.today()

    current_dt = today_dt - datetime.timedelta(days=back_day-1)

    while current_dt <= today_dt:
        current_date = current_dt.strftime("%Y-%m-%d")
        file_path = os.path.join(self.input_path, current_date+suffix)

        try:
            cur_df = pd.read_excel(file_path, sheet_name=sheet_name)
            try:
                overall_df = pd.concat([overall_df, cur_df], axis=0)
            except NameError:
                overall_df = cur_df

        except Exception:
            pass

        current_dt += datetime.timedelta(days=1)

    # if the last N day no schedule
    if 'overall_df' in dir():
        overall_df = overall_df.reset_index(drop=True)
        exist_df = True
    else:
        assert 'overall_df' in dir(
        ), f"近{back_day}天没有{sheet_name}信息，无法分析。请先在文本添加"

    return overall_df, exist_df


def DataFormatForBrokenBarh(work_states, df, back_days):
    work_states_dic = dict(zip(work_states, range(len(work_states))))
    startSecond = df['startTime'].apply(DatetimeToSecond)
    tuple_of_BrokenBarh = tuple(zip(startSecond, df['duration']))
    data_of_BrokenBarh = []
    data_of_reBrokenBarh = []
    date_list = GetNDayList(back_days)
    for date in date_list:
        idx = df[df['date'].str.contains(date)].index
        if len(idx) > 0:
            # activate
            stIdx, edIdx = idx[0], idx[-1]
            current_date_data = tuple_of_BrokenBarh[stIdx:edIdx+1]

            labels = []
            for idx in range(stIdx, edIdx+1):
                state = df['label'].iloc[idx]
                labels.append(work_states_dic[state])

            data_of_BrokenBarh.append([current_date_data, labels])

            # inactivate
            # head
            if current_date_data[0][0] > 0:
                tuple_of_reBrokenBarh = [(0, current_date_data[0][0]-1)]

            for i in range(len(current_date_data)-1):
                i_end = current_date_data[i][0] + current_date_data[i][1]
                gap = current_date_data[i+1][0] - i_end
                if gap > 0:
                    tuple_of_reBrokenBarh.append((i_end, gap))

            # tail
            gap = 3600*24 - \
                (current_date_data[-1][0] + current_date_data[-1][1])
            if gap > 0:
                tuple_of_reBrokenBarh.append((3600*24-gap, gap))
            data_of_reBrokenBarh.append(tuple_of_reBrokenBarh)

        else:
            data_of_BrokenBarh.append([(0, 0)])
            data_of_reBrokenBarh.append([(0, 0)])

    return data_of_BrokenBarh, data_of_reBrokenBarh


def GenerateFrequent(data, fast):
    length = len(data)
    date_list = GetNDayList(length)

    d_date_data = []
    for d in range(length):
        if sum(data[d]) == 0:
            continue

        for i in range(24):
            d_i = int(data[d][i])
            if d_i == 0:
                continue
            else:
                d_i = d_i // 60 if fast else d_i
                date_data0 = [date_list[d], i]
                date_data = [date_data0] * d_i

            d_date_data += date_data

    all_df = pd.DataFrame(d_date_data, columns=['date', 'hour'])

    return all_df.reset_index(drop=True)


def SumTimePerDay(data):
    data = np.array(data) / 3600

    return data.sum(axis=1)


def ymd2md(ymd):
    md = ymd.split("-")[1:]

    return '-'.join(md)


def DataFormatForPie(activate_data, work_states):
    n_day = len(activate_data)

    data = np.zeros(len(work_states))
    for d in range(n_day):
        d_date_data = activate_data[d]
        # There have been missions that day
        if len(d_date_data) > 1:
            labels = d_date_data[1]
            for i, label in enumerate(labels):
                data[label] += d_date_data[0][i][1]
    return data


def MergeDataOfBelowThreshold(data, threshold=0.1):
    data /= data.sum()
    mergeIdx = np.where(data < threshold)
    splitIdx = np.where(data >= threshold)
    otherdata = np.array([np.sum(data[mergeIdx])])
    splitdata = data[splitIdx]
    data = np.concatenate((splitdata, otherdata), axis=0)

    return data, otherdata, mergeIdx, splitIdx


def GetQualityDuration(df):
    df_group = df.groupby(by='quality')
    df = df_group['duration'].sum()
    labels = list(df_group.groups.keys())

    return df.values, labels


def DataFormatForStackBar(data):
    new_df = pd.DataFrame(None)
    quality_type = ['high', 'middle', 'low']
    for qt in quality_type:
        df = data[data['quality'] == qt]
        val = df['duration'].values
        col = df['label'].values
        qt_df = pd.DataFrame([val], columns=col)
        qt_df['quality'] = qt

        new_df = pd.concat([new_df, qt_df], axis=0)

    return new_df.reset_index(drop=True)


def DataFormatForMonthStackBar(data):
    data = data.groupby(['date', 'quality']).agg(
        {'duration': np.sum}).reset_index()
    data = data.sort_values(by=['date'])

    date_list = data.date.unique().tolist()
    quality_type = ['high', 'middle', 'low']
    columns = ['date']+quality_type

    date_quality = np.zeros((len(date_list), len(columns)))

    for d, date in enumerate(date_list):
        date_df = data[data['date'] == date].reset_index()
        for i in range(len(date_df)):
            qt = str(date_df['quality'].iloc[i])
            qt_idx = quality_type.index(qt) + 1  # first col is date
            date_quality[d, qt_idx] = int(date_df['duration'].iloc[i])

    new_df = pd.DataFrame(date_quality, columns=columns)
    new_df['date'] = date_list

    return new_df


def MergeWord(df):
    df['label_l1'] = df['label_l1'].str.title()
    df['label_l2'] = df['label_l2'].str.title()
    df['label'] = df['label_l1']+df['label_l2']

    return df['label'].to_list()


def GetOutputFilePath(root_path, suffix='.md'):
    """获取处理结果的保存路径

    Args:
        root_path ([type]): 根路径
        suffix (str, optional): [description]. Defaults to '.md'.

    Returns:
        [type]: 处理结果的保存路径
    """
    today_dt = datetime.datetime.now()

    year = str(today_dt.year)
    month = str(today_dt.month)
    day = str(today_dt.day)
    today_date = f"{year}年{month}月{day}日"

    output_file_path = os.path.join(root_path, today_date+suffix)

    return output_file_path

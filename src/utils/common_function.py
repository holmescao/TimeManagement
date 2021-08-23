'''
Author: Holmescao
Date: 2021-03-16 13:22:08
LastEditors: Holmescao
LastEditTime: 2021-08-12 15:45:40
Description: 用于时间管理分析的通用函数
'''
import sys
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
    try:
        match = re.search(date_re_str, string)
        date = match.group(1)
    except AttributeError:
        print(u"error: schedule文件命名应该为`xxxx年xx月xx日.md`")
        sys.exit()

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


def GetFilePath(root_path, suffix='.md'):
    """获取路径下所有文件

    Args:
        root_path ([str]): 根路径

    Returns:
        [list]: 所有文件的相对路径
    """
    files_path = []
    for root, _, files in os.walk(root_path):
        for file in files:
            if file.endswith(suffix):
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


def WriteFile(file, data):
    """打开文件，并写入文件内容

    Args:
        file ([type]): 文件路径
        data ([type]): 文件内容

    Returns:
        [type]: 文件内容
    """
    try:
        with open(file, mode='w', encoding='gbk') as f:
            f.writelines(data)
    except Exception:
        with open(file, mode='w', encoding='utf-8') as f:
            f.writelines(data)


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


def GetNDayList(today_dt, n):
    before_n_days = []
    for i in range(n)[::-1]:
        before_n_days.append(
            str(today_dt - datetime.timedelta(days=i)))
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


def LastNdayActivateTime(df, today_dt, back_days):
    # datetime to second
    startSecond = df['startTime'].apply(DatetimeToSecond)
    endSecond = df['endTime'].apply(DatetimeToSecond)
    tuple_of_Activate = tuple(zip(startSecond, endSecond))

    NdayActivateTime = []
    date_list = GetNDayList(today_dt, back_days)
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


def generate_fig_path(date_list, root_path, fig_type, fig_id, fig_name):
    startdate = date_list[0].replace("-", "")
    enddate = date_list[-1].replace("-", "")

    fig_save_path = os.path.join(root_path, f'figure/{enddate}/{fig_type}')
    mkdir(fig_save_path)
    fig_path = fig_save_path + \
        f'/Figure{fig_id}-{fig_name}-{startdate}_{enddate}.png'

    fig_abs_path = os.path.abspath(fig_path)

    return fig_abs_path


def InsertFigureToFile(fig_cloud, cloud_root_path,
                       fig_path, output_file_path, addFlag, width=230):
    lines = OpenFile(output_file_path)

    try:
        InsertIdx = lines.index(addFlag) + 1
    except Exception:
        InsertIdx = lines.index(addFlag+'\n') + 1

    # upload to cloud
    fig_ori_name = fig_path.replace("\\", "/").split("/")[-1]
    if fig_cloud:
        print(f'uploading {fig_path} to cloud')
        sys_res = os.popen(f'picgo upload {fig_path}').read()
        assert "PicGo SUCCESS" in sys_res, "上传到云失败！"

        fig_real_name = sys_res.split("img/")[-1].strip("\n")
        fig_path = cloud_root_path + fig_real_name

    # grammar: figure insert to markdown
    fig_grammar = f"<img src='{fig_path}' width='{width};' />\n"
    exist_Figure_flag = "<center class='half'>\n"
    end_flag = "</center>\n"

    if exist_Figure_flag not in lines[InsertIdx]:
        lines.insert(InsertIdx, exist_Figure_flag)
        lines.insert(InsertIdx + 1, fig_grammar)
        lines.insert(InsertIdx + 2, end_flag)
    else:
        # avoid redunant insert
        lines_str = '@'.join(lines)
        if fig_ori_name not in lines_str:
            find = False
            while not find:
                if end_flag in lines[InsertIdx]:
                    find = True
                else:
                    InsertIdx += 1

            lines.insert(InsertIdx, fig_grammar)
        else:
            # locate that old figure
            find = False
            while not find:
                if fig_ori_name in lines[InsertIdx]:
                    find = True
                else:
                    InsertIdx += 1
            del lines[InsertIdx]  # remove that old figure

            # insert new
            lines.insert(InsertIdx, fig_grammar)

    # insert
    with open(output_file_path, mode='w', encoding='utf-8')as fp:
        fp.writelines(lines)


def DataFormatForBrokenBarh(work_states, df, today_dt, back_days):
    work_states_dic = dict(zip(work_states, range(len(work_states))))
    startSecond = df['startTime'].apply(DatetimeToSecond)
    tuple_of_BrokenBarh = tuple(zip(startSecond, df['duration']))
    data_of_BrokenBarh = []
    data_of_reBrokenBarh = []
    date_list = GetNDayList(today_dt, back_days)
    for date in date_list[::-1]:
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
            else:
                tuple_of_reBrokenBarh = []

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


def GenerateFrequent(data, today_dt, fast):
    length = len(data)
    date_list = GetNDayList(today_dt, length)

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


def DataFormatForMonthStackBar(data, today_dt):
    data = data.groupby(['date', 'quality']).agg(
        {'duration': np.sum}).reset_index()
    data = data.sort_values(by=['date'])

    date_list = data.date.unique().tolist()
    quality_type = ['high', 'middle', 'low']

    date_quality = np.zeros((len(date_list), len(quality_type)))

    for d, date in enumerate(date_list):
        date_df = data[data['date'] == date].reset_index()
        for i in range(len(date_df)):
            qt = str(date_df['quality'].iloc[i])
            qt_idx = quality_type.index(qt)
            date_quality[d, qt_idx] = int(date_df['duration'].iloc[i])

    date_quality_np = np.zeros((30, 4), dtype=object)
    last30_date_list = GetNDayList(today_dt, 30)
    date_quality_np[:, 0] = last30_date_list
    for d in range(date_quality_np.shape[0]):
        try:
            idx = date_list.index(last30_date_list[d])
            date_quality_np[d, 1:] = date_quality[idx]
        except ValueError:
            continue
    new_df = pd.DataFrame(date_quality_np, columns=['date']+quality_type)

    return new_df


def MergeWord(df):
    df['label_l1'] = df['label_l1'].str.title()
    df['label_l2'] = df['label_l2'].str.title()
    df['label'] = df['label_l1']+df['label_l2']

    return df['label'].to_list()


def GetOutputFilePath(today_dt, root_path, suffix='.md'):
    """获取处理结果的保存路径

    Args:
        root_path ([type]): 根路径
        suffix (str, optional): [description]. Defaults to '.md'.

    Returns:
        [type]: 处理结果的保存路径
    """
    year = str(today_dt.year).zfill(4)
    month = str(today_dt.month).zfill(2)
    day = str(today_dt.day).zfill(2)
    today_date = f"{year}年{month}月{day}日"

    output_file_path = os.path.join(root_path, today_date+suffix)

    return output_file_path


def DateFormatForCompBar(df):
    duration_df = df.groupby(by=['taskId'])['duration'].sum()
    duration = duration_df.values
    taskId = list(duration_df.index)

    predTime_df = df.drop_duplicates(
        subset='taskId', keep='first', inplace=False)
    predTime_df.sort_values('taskId', ascending=True, inplace=True)
    predTime = predTime_df['predTime'].values
    labels = predTime_df['label'].tolist()
    option = predTime_df['option'].tolist()

    data = np.zeros((2, len(duration)))
    data[0, :] = duration[:] / 3600
    data[1, :] = predTime[:]

    return taskId, data, labels, option


def Datetime2Daytime(ymd_hms):
    hour = ymd_hms.hour
    minute = ymd_hms.minute
    second = ymd_hms.second

    return hour * 3600 + minute * 60 + second


def DataFormatForTomato(df):
    tomato_time = 60 * 25
    df['tomato_num'] = df['duration'].apply(
        lambda x: min(int(x/tomato_time), 4))

    date_list = sorted(list(df.date.value_counts().index))
    date_repeat = []
    for d in date_list:
        d_df = df[df.date == d]
        need_relax = False
        for i in range(len(d_df)):
            if not need_relax:
                # exceed 4 tomato time, you need relax least 5 min.
                if d_df['duration'].iloc[i] >= 4 * tomato_time:
                    need_relax = True
            else:
                # relax less 5 min, will not add score.
                relax_time = Datetime2Daytime(d_df['startTime'].iloc[i]) - \
                    Datetime2Daytime(d_df['endTime'].iloc[i-1])
                if relax_time < 5 * 60:
                    d_df['tomato_num'].iloc[i] = 0
                else:
                    need_relax = False
        score = d_df.tomato_num.sum()
        date_repeat += [d] * score

    new_df = pd.DataFrame(None, columns=['date'])
    new_df.date = pd.to_datetime(date_repeat)
    index = new_df.date.tolist()
    value = np.ones(len(index))
    YearCalendar = pd.Series(value, index=index)

    return YearCalendar

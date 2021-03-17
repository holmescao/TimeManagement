from palettable.colorbrewer.diverging import *
from collections import OrderedDict
from config import config
from wordcloud import WordCloud
from functools import wraps

import jieba
import argparse
import time
import joypy
import seaborn as sns
import numpy as np
import pandas as pd
import re
import datetime
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
import cufflinks as cf
import plotly
import warnings

warnings.filterwarnings("ignore")

cf.go_offline()
cf.set_config_file(offline=True, world_readable=True)
setattr(plotly.offline, "__PLOTLY_OFFLINE_INITIALIZED", True)

mpl.rcParams["font.sans-serif"] = ["LiSu"]
mpl.rcParams["axes.unicode_minus"] = False


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def func_timer(function):
    '''
    用装饰器实现函数计时
    :param function: 需要计时的函数
    :return: None
    '''
    @wraps(function)
    def function_timer(*args, **kwargs):
        print('[Function: {name} start...]'.format(name=function.__name__))
        t0 = time.time()
        result = function(*args, **kwargs)
        function(*args, **kwargs)
        t1 = time.time()
        print('[Function: {name} finished, spent time: {time:.2f}s]'.format(
            name=function.__name__, time=t1 - t0))
        return result

    return function_timer


def OpenFile(file):
    try:
        with open(file, mode='r', encoding='gbk') as f:
            context = f.readlines()
    except Exception:
        with open(file, mode='r', encoding='utf-8') as f:
            context = f.readlines()

    return context


def ExtractandSaveSchedule(args,
                           data_columns,
                           files_path,
                           pre_files_path,
                           tmp_path,
                           suffix='.md',
                           scheduleFlag='### 计划\n',
                           carryFlag='### 执行\n',
                           reviewFlag='### 复盘\n'):
    for file in files_path:
        date = GetDate(file)
        exist_files = '_'.join(pre_files_path)
        # avoid redundant process, except today's file
        if (date not in exist_files) or (file == files_path[-1]):
            context = OpenFile(file)

            save_path = os.path.join(tmp_path, date+'.xlsx')

            df_list = []
            if args.activate:
                activate = GetActivate(date, context, data_columns,
                                       carryFlag, reviewFlag, scheduleFlag)
                df_list.append((activate, 'activate'))

            if args.information:
                information = GetInformation(date, context, data_columns,
                                             reviewFlag)
                df_list.append((information, 'information'))

            if args.harvest:
                harvest = GetHarvest(date, context, data_columns,
                                     reviewFlag)
                df_list.append((harvest, 'harvest'))

            SaveToExcel(df_list, save_path)


def GetActivate(date, context, data_columns,
                carryFlag, reviewFlag, scheduleFlag):
    startIdx = GetFlagIdx(context, carryFlag)
    endIdx = GetFlagIdx(context, reviewFlag)
    datetime_label_pairs = GetDateTimeAndLabelPair(
        context, date, startIdx, endIdx, scheduleFlag)
    activate = pd.DataFrame(datetime_label_pairs,
                            columns=data_columns['activate'])

    return activate


def GetInformation(date, context, data_columns, reviewFlag):
    Idx = GetFlagIdx(context, reviewFlag)
    information_quality_pairs = GetDateInformationQualityPair(
        context, date, Idx)
    information = pd.DataFrame(information_quality_pairs,
                               columns=data_columns['information'])

    return information


def GetHarvest(date, context, data_columns, reviewFlag):
    Idx = GetFlagIdx(context, reviewFlag)
    harvest_label = GetDateHarvest(
        context, date, Idx)
    harvest = pd.DataFrame(harvest_label,
                           columns=data_columns['harvest'])

    return harvest


def SaveToExcel(df_list, save_path):
    with pd.ExcelWriter(save_path) as writer:
        for df_sheet in df_list:
            df = df_sheet[0]
            sheet_name = df_sheet[1]
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def GetFlagIdx(context, flag):
    return context.index(flag)


def GetDate(string):
    string = string.replace("年", "-")
    string = string.replace("月", "-")
    string = string.replace("日", "-")
    date_re_str = r"(\d{4}-\d{1,2}-\d{1,2})"
    match = re.search(date_re_str, string)
    date = match.group(1)

    date = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")

    return date


def GetDateTimeAndLabelPair(context, date,
                            startIdx, endIdx,
                            scheduleFlag,
                            planlabelFlag='. ',
                            carrylabelFlag='@',
                            timeSep='to'):
    datetime_label_pairs = []
    for idx in range(startIdx, endIdx):
        line = context[idx]
        if timeSep in line:
            # find time period
            time_re_str = r"\d{1,2}:\d{1,2}:\d{1,2}"
            time_regex = re.compile(time_re_str)
            time_period = time_regex.findall(line)

            # change strptime format
            startTime = datetime.datetime.strptime(
                date+" "+time_period[0], "%Y-%m-%d %H:%M:%S")
            endTime = datetime.datetime.strptime(
                date+" "+time_period[1], "%Y-%m-%d %H:%M:%S")

            # duration
            duration = (endTime - startTime).seconds

            #  location label idx
            labelFlagIdx = line.find(carrylabelFlag)
            taskId = line[:labelFlagIdx]
            carryIdx = context.index(scheduleFlag) + 1
            findtask = False
            while not findtask:
                if taskId+planlabelFlag in context[carryIdx]:
                    taskIdx = carryIdx
                    findtask = True
                else:
                    carryIdx += 1

            # match label
            task_line = context[taskIdx]
            label_re_str = "(\\[).*?(\\])"
            span = re.search(label_re_str, task_line).span()
            label = task_line[span[0]+1:span[1]-1]

            # append record
            datetime_label_pairs.append(
                [date, startTime, endTime, duration, label])

    return datetime_label_pairs


def GetDateInformationQualityPair(context, date, Idx):
    information_quality_pairs = []
    for idx in range(Idx, len(context)):
        line = context[idx]
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
            information_quality_pairs.append([date, quality, duration, label])
        except AttributeError:
            continue

    return information_quality_pairs


def GetDateHarvest(context, date, Idx):
    harvest = []
    for idx in range(Idx, len(context)):
        line = context[idx]
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
            harvest.append([date, label1, label2])

        except AttributeError:
            continue

    return harvest


def GetFilePath(root_path):
    files_path = []
    for root, _, files in os.walk(root_path):
        for file in files:
            file_path = os.path.join(root, file)
            files_path.append(file_path)

    return sorted(files_path)


@func_timer
def HandleDailySchedule(args, root_path, tmp_path, data_columns):
    files_path = GetFilePath(root_path)
    pre_files_path = GetFilePath(tmp_path)
    ExtractandSaveSchedule(args, data_columns,
                           files_path, pre_files_path, tmp_path)


@func_timer
def Analyze(args, work_states, input_path, output_path, output_file_path):
    if args.activate:
        AnalyzeActivate(work_states, input_path, output_path, output_file_path)

    if args.information:
        AnalyzeInformation(input_path, output_path, output_file_path)

    if args.harvest:
        AnalyzeHarvest(input_path, output_path, output_file_path)


def DatetimeToSecond(dt):
    seconds = dt.hour * 3600 + dt.minute * 60 + dt.second

    return seconds


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


def GenerateFrequent(data):
    length = len(data)
    date_list = GetNDayList(length)

    columns = ['date', 'hour']
    all_df = pd.DataFrame(None, columns=columns)
    for d in range(length):
        if sum(data[d]) == 0:
            continue
        for i in range(24):
            d_i = int(data[d][i])

            date_data0 = [date_list[d], i]
            date_data = [date_data0] if d_i == 0 else [date_data0] * d_i

            df = pd.DataFrame(date_data, columns=columns)
            all_df = pd.concat([all_df, df], axis=0)

    all_df['hour'] = all_df['hour'].apply(pd.to_numeric)

    return all_df.reset_index(drop=True)


def AnalyzeActivate(work_states, input_path, output_path, output_file_path):
    sheet_name = 'activate'
    last_day, exist_day = GetLastData(1, input_path, sheet_name)
    last_week, exist_week = GetLastData(7, input_path, sheet_name)
    last_month, exist_month = GetLastData(30, input_path, sheet_name)

    # last_day: bar
    if exist_day:
        NdayActivateTime = LastNdayActivateTime(last_day, back_days=1)
        # frequent = GenerateFrequent(NdayActivateTime)

        date_list = GetNDayList(1)
        fig_path = generate_fig_path(date_list, root_path=output_path,
                                     fig_id=2, fig_name='activate-bar')
        PlotDayBar(NdayActivateTime[0], fig_path)
        # PlotBarAndLine(frequent, fig_path)
        InsertFigureToFile(fig_path, output_file_path, addFlag='2. 学习情况？（分析图）')

    # last week: broken barh
    if exist_week:
        data_of_BrokenBarh, data_of_reBrokenBarh = DataFormatForBrokenBarh(
            work_states, last_week, back_days=7)

        date_list = GetNDayList(7)
        fig_path = generate_fig_path(date_list, root_path=output_path,
                                     fig_id=1, fig_name='activate-brokenbarh')
        PlotBrokenBarh(work_states,
                       data_of_BrokenBarh,
                       data_of_reBrokenBarh,
                       date_list,
                       fig_path)
        if exist_day:
            InsertFigureToFile(fig_path, output_file_path,
                               addFlag='2. 学习情况？（分析图）')

    # last week: waterfall
    if exist_week:
        NdayActivateTime = LastNdayActivateTime(last_week, back_days=7)
        frequent = GenerateFrequent(NdayActivateTime)

        date_list = GetNDayList(7)
        fig_path = generate_fig_path(date_list, root_path=output_path,
                                     fig_id=3, fig_name='activate-waterfall')

        PlotWaterFall(frequent, fig_path)

        if exist_day:
            InsertFigureToFile(fig_path, output_file_path,
                               addFlag='2. 学习情况？（分析图）')

    # last month: bar
    if exist_month:
        NdayActivateTime = LastNdayActivateTime(last_week, back_days=30)
        sum_activate_per_day = SumTimePerDay(NdayActivateTime)

        date_list = GetNDayList(30)
        fig_path = generate_fig_path(date_list, root_path=output_path,
                                     fig_id=4, fig_name='activate-bar')

        PlotMonthBar(sum_activate_per_day, fig_path)
        if exist_day:
            InsertFigureToFile(fig_path, output_file_path,
                               addFlag='2. 学习情况？（分析图）')
    # last month: pie
    if exist_month:
        data_of_BrokenBarh, _ = DataFormatForBrokenBarh(
            work_states, last_month, back_days=30)
        data_of_pie = DataFormatForPie(data_of_BrokenBarh)
        date_list = GetNDayList(30)
        fig_path = generate_fig_path(date_list, root_path=output_path,
                                     fig_id=5, fig_name='investment-pie')

        PlotPie(work_states, data_of_pie, fig_path)

        if exist_day:
            InsertFigureToFile(fig_path, output_file_path,
                               addFlag='2. 学习情况？（分析图）')


def DataFormatForPie(activate_data):
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


def SumTimePerDay(data):
    data = np.array(data) / 3600

    return data.sum(axis=1)


def ymd2md(ymd):
    md = ymd.split("-")[1:]

    return '-'.join(md)


def PlotWaterFall(activate_data, fig_path):
    fontsize = 20

    fig, axes = joypy.joyplot(
        activate_data,
        column=['hour'], by="date",
        grid=True,
        xlabelsize=fontsize,
        ylabelsize=fontsize,
        figsize=(10, 6),
        ylim='own',
        fill=True,
        linecolor=None,
        background=None,
        xlabels=True, ylabels=True,
        range_style='all',
        x_range=np.arange(25),
        color=cm.hsv(0.68))

    # params
    plt.xlabel(u"小时", fontsize=fontsize)
    plt.xticks(ticks=list(range(0, 24, 4))+[24],
               labels=list(range(0, 24, 4))+[24], fontsize=fontsize)
    plt.title(u"近一周学习情况", fontsize=fontsize+5)
    plt.grid(linestyle="--", alpha=0.45)

    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()


def PlotDayBar(activate_data, fig_path):
    fig, ax = plt.subplots(figsize=(8, 6))

    hours = np.arange(24)
    # bar
    plt.bar(hours, height=activate_data,
            label='activate', color=cm.hsv(0.4), alpha=0.8)
    # # line
    # x = np.linspace(0, 23, num=24)
    # x_new = np.linspace(x.min(), x.max(), 24)
    # activate_data_tck = splrep(x, activate_data)
    # activate_data_tck_new = splev(x_new, activate_data_tck)
    # activate_data_tck_new[activate_data_tck_new < 0] = 0
    # plt.plot(x_new, activate_data_tck_new,
    #          color=cm.hsv(0.63), marker='o', ms=4)

    # sns.distplot(activate_data['hour'],
    #              color=cm.hsv(0.63),
    #              label="activate",
    #              hist_kws={'alpha': 0.3},
    #              kde_kws={'linewidth': 3})

    # params
    fontsize = 20
    plt.legend(fontsize=fontsize-2, loc='upper left')
    plt.xlabel(u"小时", fontsize=fontsize)
    plt.ylabel(u"时长(秒)", fontsize=fontsize)
    plt.xticks(fontsize=fontsize-5)
    plt.yticks(fontsize=fontsize)
    plt.xticks(ticks=range(24), labels=hours)
    sumhours = sum(activate_data) / 3600
    # sumhours = len(activate_data) / 3600
    plt.title("今日学习投入情况 (%.2f 小时)" % sumhours, fontsize=fontsize+5)

    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()


def PlotBrokenBarh(work_states,
                   activate_data, inactivate_data,
                   date_list, fig_path):
    states_work_dic = dict(zip(range(len(work_states)), work_states))
    color_map = dict(zip(work_states, np.arange(len(work_states))))
    n_day = len(activate_data)

    fig, ax = plt.subplots(figsize=(8, 6))
    high, y_loc = 0.5, 0.7
    for x in range(n_day):
        x_day_data = activate_data[x]
        if len(x_day_data) > 1:
            idx = x_day_data[-1]
            # draw per work
            for work in range(len(idx)):
                label = states_work_dic[idx[work]]
                ax.broken_barh([x_day_data[0][work]], [x+y_loc, high],
                               color=cm.Set2(
                                   color_map[label]/len(work_states)),
                               label=label)
        # draw inactivate
        ax.broken_barh(inactivate_data[x], [x+y_loc, high],
                       color=cm.hsv(0), label='inactivate')

    # params
    interval = 1
    fontsize = 20
    ax.set_xticks(list(range(0, 3600*24+1, 3600*interval)))
    ax.set_xticklabels(list(range(0, 24+1, interval)), fontsize=fontsize-5)
    ax.set_yticks(list(range(1, n_day+1)))
    ax.set_yticklabels(date_list, fontsize=fontsize)
    plt.xlabel(u"小时", fontsize=fontsize)
    plt.ylabel(u"日期", fontsize=fontsize)
    plt.title(u"近一周投入时间", fontsize=fontsize+5)
    plt.grid(linestyle="--", alpha=0.15)

    # drop the redundant of labels via `dict.keys()`
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(),
               bbox_to_anchor=(0.1, -0.25), loc='center left',
               ncol=3, fontsize=fontsize-5)

    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()


def PlotPie(work_states,
            data, fig_path):
    fig, ax = plt.subplots(figsize=(8, 6))

    data, otherdata, mergeIdx, splitIdx = \
        MergeDataOfBelowThreshold(data)

    # process color and label
    colors = np.array([cm.Set2(i/len(work_states))
                       for i in range(len(work_states))])
    work_states = np.array(work_states)
    if otherdata > 0:
        colors = list(colors[splitIdx]) + [cm.hsv(0)]
        ohter_labels = '\n'.join(work_states[mergeIdx])
        work_states = list(work_states[splitIdx]) + ['others']

    # Segment the one with the largest percentage
    explode = [0] * data.shape[0]
    explode[np.argmax(data)] = 0.1

    # plot pie
    patches, l_text, p_text = \
        plt.pie(x=data, explode=explode, labels=work_states,
                labeldistance=1.1, colors=colors, autopct='%.0f%%',
                shadow=True, startangle=90, pctdistance=0.6)

    # params
    fontsize = 20
    list(map(lambda t: t.set_size(fontsize), l_text))
    list(map(lambda t: t.set_size(fontsize), p_text))
    plt.title(u"近一个月投入时间", fontsize=fontsize+5)
    plt.text(x=1.8, y=-1.2,
             s="*others(individual < 10%):\n"+ohter_labels,
             fontsize=fontsize+5)

    # drop the redundant of labels via `dict.keys()`
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(),
               bbox_to_anchor=(1.4, 1), loc='upper right',
               ncol=1, fontsize=fontsize+5)
    plt.axis('equal')

    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()


def PlotMonthBar(activate_data, fig_path):
    date_list = GetNDayList(30)
    md_list = list(map(ymd2md, date_list))

    fig, ax = plt.subplots(figsize=(8, 6))

    days = np.arange(30)
    plt.bar(days, height=activate_data,
            label='activate', color=cm.hsv(0.6), alpha=0.8)

    avg_hours = activate_data.mean()
    plt.axhline(y=avg_hours, ls=":", lw=4, c=cm.hsv(0))

    # params
    fontsize = 20
    plt.legend(fontsize=fontsize-2, loc='upper left')
    plt.xlabel(u"日期", fontsize=fontsize)
    plt.ylabel(u"时长(小时)", fontsize=fontsize)
    plt.xticks(fontsize=fontsize-5)
    plt.yticks(fontsize=fontsize)
    plt.xticks(ticks=range(0, 30+1, 4), labels=md_list[::4])

    plt.title("近一个月学习投入情况(平均{0:.2f}小时)".format(avg_hours),
              fontsize=fontsize+5)

    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()


def MergeDataOfBelowThreshold(data, threshold=0.1):
    data /= data.sum()
    mergeIdx = np.where(data < threshold)
    splitIdx = np.where(data >= threshold)
    otherdata = np.array([np.sum(data[mergeIdx])])
    splitdata = data[splitIdx]
    data = np.concatenate((splitdata, otherdata), axis=0)

    return data, otherdata, mergeIdx, splitIdx


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


def generate_fig_path(date_list, root_path, fig_id, fig_name):
    startdate = date_list[0].replace("-", "")
    enddate = date_list[-1].replace("-", "")

    fig_save_path = os.path.join(root_path, 'figure/Figure%s' % fig_id)
    mkdir(fig_save_path)
    fig_path = fig_save_path + \
        f'/Figure{fig_id}-{fig_name}-{startdate}_{enddate}.png'

    fig_abs_path = os.path.abspath(fig_path)

    return fig_abs_path


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


def GetNDayList(n):
    before_n_days = []
    for i in range(n)[::-1]:
        before_n_days.append(
            str(datetime.date.today() - datetime.timedelta(days=i)))
    return before_n_days


def GetLastData(back_day, file_root_path, sheet_name):
    today_dt = datetime.date.today()

    current_dt = today_dt - datetime.timedelta(days=back_day-1)

    while current_dt <= today_dt:
        current_date = current_dt.strftime("%Y-%m-%d")
        file_path = os.path.join(file_root_path, current_date+'.xlsx')

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
        overall_df = pd.DataFrame(None)
        exist_df = False

    return overall_df, exist_df


def GetOutputFilePath(root_path):
    today_dt = datetime.datetime.now()

    year = str(today_dt.year)
    month = str(today_dt.month)
    day = str(today_dt.day)
    today_date = f"{year}年{month}月{day}日"

    output_file_path = os.path.join(root_path, today_date+'.md')

    return output_file_path


def AnalyzeInformation(input_path, output_path, output_file_path):
    sheet_name = 'information'
    last_day, exist_day = GetLastData(1, input_path, sheet_name)
    last_month, exist_month = GetLastData(30, input_path, sheet_name)

    # last day: pie
    if exist_day:
        df_group = last_day.groupby(by='quality')
        df = df_group['duration'].sum()
        labels = list(df_group.groups.keys())

        date_list = GetNDayList(1)
        fig_path = generate_fig_path(date_list, root_path=output_path,
                                     fig_id=6, fig_name='dayinformation-pie')

        PlotPieForInformation(df.values, labels, fig_path)

        InsertFigureToFile(fig_path, output_file_path,
                           addFlag='3. 信息摄入')

    # last day: stack-bar
    if exist_day:
        df = DataFormatForStackBar(last_day)
        date_list = GetNDayList(1)
        fig_path = generate_fig_path(date_list, root_path=output_path,
                                     fig_id=7, fig_name='dayinformation-stackbar')

        PlotStackBarForInformation(df, fig_path)

        if exist_day:
            InsertFigureToFile(fig_path, output_file_path,
                               addFlag='3. 信息摄入')

    # last month: stack-bar
    if exist_month:
        df = DataFormatForMonthStackBar(last_month)
        date_list = GetNDayList(30)
        fig_path = generate_fig_path(date_list, root_path=output_path,
                                     fig_id=8, fig_name='monthinformation-stackbar')

        PlotMonthStackBarAndCurveForInformation(df, fig_path)

        if exist_day:
            InsertFigureToFile(fig_path, output_file_path,
                               addFlag='3. 信息摄入')


def AnalyzeHarvest(input_path, output_path, output_file_path):
    sheet_name = 'harvest'
    last_month, exist_month = GetLastData(30, input_path, sheet_name)

    # last month: cloud
    if exist_month:
        word_list = MergeWord(last_month)

        date_list = GetNDayList(30)
        fig_path = generate_fig_path(date_list, root_path=output_path,
                                     fig_id=9, fig_name='harvest-cloud')

        PlotWordCloudForHarvest(word_list, fig_path)

        InsertFigureToFile(fig_path, output_file_path,
                           addFlag='4. 收获')


def MergeWord(df):
    df['label_l1'] = df['label_l1'].str.title()
    df['label_l2'] = df['label_l2'].str.title()
    df['label'] = df['label_l1']+df['label_l2']

    return df['label'].to_list()


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


def PlotWordCloudForHarvest(data, fig_path):
    text_cut = ' '.join(data)

    word_cloud = WordCloud(font_path="simsun.ttc",
                           background_color="white",
                           max_font_size=40)
    word_cloud.generate(text_cut)

    plt.subplots(figsize=(8, 6))
    plt.imshow(word_cloud)
    plt.axis("off")

    # params
    fontsize = 30
    plt.title(u"近一个月收获情况", fontsize=fontsize)

    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()


def PlotPieForInformation(data, labels, fig_path):
    fig, ax = plt.subplots(figsize=(8, 6))

    # process color and label
    colors = [cm.Set2(i/len(labels)) for i in range(len(labels))]

    # Segment the one with the largest percentage
    explode = [0] * data.shape[0]
    explode[np.argmax(data)] = 0.1

    # plot pie
    patches, l_text, p_text = \
        plt.pie(x=data, explode=explode, labels=labels,
                labeldistance=1.1, colors=colors, autopct='%.0f%%',
                shadow=True, startangle=90, pctdistance=0.6)

    # params
    fontsize = 20
    list(map(lambda t: t.set_size(fontsize), l_text))
    list(map(lambda t: t.set_size(fontsize), p_text))
    plt.title(u"今日信息摄入质量情况", fontsize=fontsize+5)

    # drop the redundant of labels via `dict.keys()`
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(),
               bbox_to_anchor=(1.4, 1), loc='upper right',
               ncol=1, fontsize=fontsize+5)
    plt.axis('equal')

    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()


def PlotStackBarForInformation(stacked_bar_data, fig_path):
    quality_list = stacked_bar_data.quality.values
    columns = list(stacked_bar_data.columns)
    columns.remove('quality')
    colors = [cm.Set2(i/len(columns)) for i in range(len(columns))]

    del stacked_bar_data['quality']
    stacked_bar_data = stacked_bar_data.values
    stacked_bar_data[np.isnan(stacked_bar_data)] = 0

    # plot by stacking
    val = stacked_bar_data[:, 0]
    p1 = plt.bar(np.arange(len(quality_list)), val,
                 width=0.5, color=colors[0])
    sub_matrix = stacked_bar_data[:, 0:1]
    csum = np.cumsum(sub_matrix, axis=1)[:, -1]
    csum = csum.flatten()

    for i in range(1, len(columns)):
        sub_matrix = stacked_bar_data[:, 0:i]
        csum = np.cumsum(sub_matrix, axis=1)[:, -1]
        csum = csum.flatten()

        val = stacked_bar_data[:, i]
        p3 = plt.bar(np.arange(len(quality_list)), val,
                     width=0.5, bottom=csum, color=colors[i],
                     tick_label=quality_list)

    sub_matrix = stacked_bar_data[:, :]
    csum = np.cumsum(sub_matrix, axis=1)[:, -1]
    csum = csum.flatten()

    # params
    fontsize = 20
    plt.legend(fontsize=fontsize-2, loc='upper right', labels=columns)
    plt.xlabel(u"信息质量", fontsize=fontsize)
    plt.ylabel(u"时长(分钟)", fontsize=fontsize)
    plt.xticks(fontsize=fontsize-5)
    plt.yticks(fontsize=fontsize)
    plt.ylim([0, max(csum)*1.2])
    plt.title("今日信息摄入情况", fontsize=fontsize+5)

    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()


def PlotMonthStackBarAndCurveForInformation(stacked_bar_data, fig_path):
    date_list = stacked_bar_data['date'].tolist()

    columns = stacked_bar_data.columns.tolist()
    columns.remove('date')
    colors = [cm.Set2(i/len(columns)) for i in range(len(columns))]

    fig, ax = plt.subplots(figsize=(8, 6))

    # plot by stacking
    stacked_bar_data = stacked_bar_data[columns].values
    val = stacked_bar_data[:, 0]
    p1 = ax.bar(np.arange(len(date_list)), val,
                width=0.5, color=colors[0], label=columns[0])
    sub_matrix = stacked_bar_data[:, 0:1]
    csum = np.cumsum(sub_matrix, axis=1)[:, -1]
    csum = csum.flatten()

    for i in range(1, len(columns)):
        sub_matrix = stacked_bar_data[:, 0:i]
        csum = np.cumsum(sub_matrix, axis=1)[:, -1]
        csum = csum.flatten()

        val = stacked_bar_data[:, i]
        p3 = ax.bar(np.arange(len(date_list)), val,
                    width=0.5, bottom=csum, color=colors[i],
                    label=columns[i],
                    tick_label=list(map(ymd2md, date_list)))

    sub_matrix = stacked_bar_data[:, :]
    csum = np.cumsum(sub_matrix, axis=1)[:, -1]
    csum = csum.flatten()

    # curve
    ax1 = ax.twinx()
    high_rate = stacked_bar_data[:, 0] / np.sum(stacked_bar_data, axis=1)
    ax1.plot(np.arange(len(date_list)), high_rate,
             color='red', label='rate of high',
             marker='o', markersize=5)

    # params
    fontsize = 20
    plt.xlabel(u"日期", fontsize=fontsize)
    for tick in ax.get_xticklabels():
        tick.set_rotation(30)
    fig.legend(loc="upper right", bbox_to_anchor=(
        1, 1), bbox_transform=ax.transAxes, fontsize=fontsize)
    plt.title(u"近一个月信息摄入情况", fontsize=fontsize+5)
    plt.grid(linestyle='--', alpha=0.9)

    ax.set_label(columns)
    ax.tick_params(labelsize=fontsize)
    ax.set_ylabel(u"时长(分钟)", fontsize=fontsize)
    ax.set_ylim([0, max(csum)*1.2])

    ax1.set_label("high rate")
    ax1.tick_params(labelsize=fontsize)
    ax1.set_ylabel("%", fontsize=fontsize)
    ax1.set_ylim([0, 1.2])

    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--activate', type=bool, default=True)
    parser.add_argument('--information', type=bool, default=True)
    parser.add_argument('--harvest', type=bool, default=True)
    args = parser.parse_args()

    # settings
    root_path = config['path']['root_path']
    tmp_path = config['path']['tmp_path']
    output_path = config['path']['output_path']
    output_file_path = GetOutputFilePath(root_path)
    data_columns = config['data_columns']
    work_states = config['work_states']
    mkdir(tmp_path)
    mkdir(output_path)

    HandleDailySchedule(args, root_path, tmp_path, data_columns)
    Analyze(args, work_states, tmp_path, output_path, output_file_path)

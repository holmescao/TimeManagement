'''
Author: Holmescao
Date: 2021-03-16 13:17:04
LastEditors: Holmescao
LastEditTime: 2021-04-01 11:53:56
Description: 通过可视化分析时间管理情况，并自动将分析结果插入到相应文件中。
'''


from utils import calmap as calmap
from utils.common_function import *

from wordcloud import WordCloud
import calendar
import joypy
from collections import OrderedDict
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


mpl.rcParams["font.sans-serif"] = ["LiSu"]
mpl.rcParams["axes.unicode_minus"] = False


class Analyze:
    """可视化分析模块"""

    def __init__(self, args, work_states, input_path, output_path, output_file_path):
        """初始化

        Args:
            args ([type]): 主要包括待处理的信息类别
            work_states ([type]): [description]
            input_path ([type]): 待分析数据的路径
            output_path ([type]): 数据分析结果在本项目的保存路径
            output_file_path ([type]): 数据分析结果待插入图片到文件的路径
        """
        self.args = args
        self.work_states = work_states

        self.input_path = input_path
        self.output_path = output_path
        self.output_file_path = output_file_path
        mkdir(input_path)
        mkdir(output_path)

        self.schedule_date = "# xxxx年xx月xx日Schedule\n"
        self.sheet_names = ['activate', 'information', 'harvest']

    @property
    def DataAnalyze(self):
        """数据分析"""
        if self.args.activate:
            last_day, last_week, last_month, last_year = \
                self.GetRecentData(self.sheet_names[0])
            ActivateAnalyze(self.args.fast,
                            self.args.today_dt,
                            last_day,
                            last_week,
                            last_month,
                            last_year,
                            self.work_states,
                            self.output_path,
                            self.output_file_path).Analyze

        if self.args.information:
            last_day, _, last_month, _ = \
                self.GetRecentData(self.sheet_names[1])
            InformationAnalyze(self.args.today_dt,
                               last_day,
                               last_month,
                               self.output_path,
                               self.output_file_path).Analyze

        if self.args.harvest:
            _, _, _, last_year = \
                self.GetRecentData(self.sheet_names[2])
            HarvestAnalyze(self.args.today_dt,
                           last_year,
                           self.output_path,
                           self.output_file_path).Analyze

        lines = OpenFile(self.output_file_path)
        try:
            idx = lines.index(self.schedule_date)

            year = str(self.args.today_dt.year).zfill(4)
            month = str(self.args.today_dt.month).zfill(2)
            day = str(self.args.today_dt.day).zfill(2)
            lines[idx] = f"# {year}年{month}月{day}日Schedule\n"
            with open(self.output_file_path, mode='w', encoding='utf-8')as fp:
                fp.writelines(lines)
        except Exception:
            pass

    def GetRecentData(self, sheet_name):
        """获取最近1~30天的数据

        Args:
            sheet_name ([type]): 代表不同信息类别的sheet

        Returns:
            [type]: 最近1~30天的数据
        """
        last_day = self.GetLastData(1,  sheet_name)
        last_week = self.GetLastData(7, sheet_name)
        last_month = self.GetLastData(30, sheet_name)
        last_year = self.GetLastData(365, sheet_name)

        return last_day, last_week, last_month, last_year

    def GetLastData(self, back_day, sheet_name, suffix='.xlsx'):
        """从文件夹中提取获取前n天的指定类别数据

        Args:
            back_day ([type]): 表示获取前n天数据
            sheet_name ([type]): 代表不同信息类别的sheet
            suffix (str, optional): 文件名后缀. Defaults to '.xlsx'.

        Returns:
            [type]: 前n天的指定类别数据
        """

        current_dt = self.args.today_dt - datetime.timedelta(days=back_day-1)

        while current_dt <= self.args.today_dt:
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
        else:
            assert 'overall_df' in dir(
            ), f"近{back_day}天没有{sheet_name}信息，无法分析。请先在文本添加"

        return overall_df


class ActivateAnalyze:
    def __init__(self, fast, today_dt, last_day, last_week, last_month, last_year,
                 work_states, output_path, output_file_path):
        """初始化

        Args:
            last_day ([type]): 最近1天的数据（即今天）
            last_week ([type]): 最近7天的数据
            last_month ([type]): 最近30天的数据
            work_states ([type]): 工作状态类别
            output_path ([type]): 数据分析结果在本项目的保存路径
            output_file_path ([type]): 数据分析结果待插入图片到文件的路径
        """
        self.fast = fast
        self.today_dt = today_dt

        self.last_day = last_day
        self.last_week = last_week
        self.last_month = last_month
        self.last_year = last_year

        self.work_states = work_states

        self.output_path = output_path
        self.output_file_path = output_file_path

        self.addFlag = '#### 2. 学习情况'

        self.fig_type = "activate"

    @property
    @class_func_timer("ActivateAnalyze")
    def Analyze(self):
        """可视化分析"""
        # self.LastDayBar(fig_id=1, fig_name='activate-bar')
        # self.LastWeekWaterfall(fig_id=2, fig_name='activate-waterfall')
        # self.LastMonthBar(fig_id=3, fig_name='activate-bar')
        # self.LastMonthPie(fig_id=4, fig_name='investment-pie')
        # self.LastWeekBroenBarh(fig_id=5, fig_name='activate-brokenbarh')
        # self.LastDayCompBar(fig_id=6, fig_name='activate-predict-bar')
        self.LastYearCalendar(fig_id=7, fig_name='activate-calendar')

    def LastDayBar(self, fig_id, fig_name):
        """画最近1天的投入时间柱形图

        Args:
            fig_id ([type]): 图片编号
            fig_name ([type]): 图片名称
        """
        NdayActivateTime = LastNdayActivateTime(
            self.last_day, self.today_dt, back_days=1)
        self.activate_data = NdayActivateTime[0]

        self.fig_path = generate_fig_path(date_list=GetNDayList(self.today_dt, 1),
                                          root_path=self.output_path,
                                          fig_type=self.fig_type,
                                          fig_id=fig_id, fig_name=fig_name)

        self.PlotDayBar
        InsertFigureToFile(self.fig_path, self.output_file_path, self.addFlag)

    @property
    def PlotDayBar(self):
        """活跃时间柱形图"""
        fig, ax = plt.subplots(figsize=(8, 6))

        hours = np.arange(24)
        # bar
        plt.bar(hours, height=self.activate_data,
                label='activate', color=cm.hsv(0.4), alpha=0.8)

        # params
        fontsize = 20
        plt.legend(fontsize=fontsize-2, loc='upper left')
        plt.xlabel(u"小时", fontsize=fontsize)
        plt.ylabel(u"时长(秒)", fontsize=fontsize)
        plt.xticks(fontsize=fontsize-5)
        plt.yticks(fontsize=fontsize)
        plt.xticks(ticks=range(24), labels=hours)
        sumhours = sum(self.activate_data) / 3600
        plt.title("每小时的投入时长 (当天，%.2f 小时)" % sumhours, fontsize=fontsize+5)

        plt.savefig(self.fig_path, dpi=150, bbox_inches='tight')
        plt.close()

    def LastWeekBroenBarh(self, fig_id, fig_name):
        """画最近1周的投入时间间断图

        Args:
            fig_id ([type]): 图片编号
            fig_name ([type]): 图片名称
        """
        self.activate_data, self.inactivate_data = DataFormatForBrokenBarh(
            self.work_states, self.last_week, self.today_dt, back_days=7)

        self.fig_path = generate_fig_path(date_list=GetNDayList(self.today_dt, 7),
                                          root_path=self.output_path,
                                          fig_type=self.fig_type,
                                          fig_id=fig_id,
                                          fig_name=fig_name)

        self.PlotBrokenBarh
        InsertFigureToFile(self.fig_path, self.output_file_path, self.addFlag)

    @property
    def PlotBrokenBarh(self):
        """活跃时间间断图"""
        task_id = np.arange(len(self.work_states))
        states_work_dic = dict(zip(task_id, self.work_states))
        color_map = dict(zip(self.work_states, task_id))

        n_day = len(self.activate_data)

        fig, ax = plt.subplots(figsize=(8, 6))
        high, y_loc = 0.5, 0.7
        for x in range(n_day):
            x_day_data = self.activate_data[x]
            if len(x_day_data) > 1:
                idx = x_day_data[-1]
                # draw per work
                for work in range(len(idx)):
                    label = states_work_dic[idx[work]]
                    ax.broken_barh([x_day_data[0][work]], [x+y_loc, high],
                                   color=cm.Set3(
                        color_map[label]/len(self.work_states)),
                        label=label)
            # draw inactivate
            ax.broken_barh(self.inactivate_data[x], [x+y_loc, high],
                           color=cm.hsv(0), label='inactivate')

        # params
        interval = 1
        fontsize = 20
        ax.set_xticks(list(range(0, 3600*24+1, 3600*interval)))
        ax.set_xticklabels(list(range(0, 24+1, interval)), fontsize=fontsize-5)
        ax.set_yticks(list(range(1, n_day+1)))
        ax.set_yticklabels(GetNDayList(self.today_dt, 7)
                           [::-1], fontsize=fontsize)
        plt.xlabel(u"小时", fontsize=fontsize)
        # plt.ylabel(u"日期", fontsize=fontsize)
        plt.title(u"24小时任务监控（近7天）", fontsize=fontsize+5)
        plt.grid(linestyle="--", alpha=0.15)

        # drop the redundant of labels via `dict.keys()`
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(),
                   bbox_to_anchor=(0.1, -0.25), loc='center left',
                   ncol=3, fontsize=fontsize-5)

        plt.savefig(self.fig_path, dpi=150, bbox_inches='tight')
        plt.close()

    def LastWeekWaterfall(self, fig_id, fig_name):
        """画最近1周的投入时间瀑布图

        Args:
            fig_id ([type]): 图片编号
            fig_name ([type]): 图片名称
        """
        NdayActivateTime = LastNdayActivateTime(
            self.last_week, self.today_dt, back_days=7)
        self.frequent = GenerateFrequent(
            NdayActivateTime, self.today_dt, self.fast)

        self.fig_path = generate_fig_path(date_list=GetNDayList(self.today_dt, 7),
                                          root_path=self.output_path,
                                          fig_type=self.fig_type,
                                          fig_id=fig_id, fig_name=fig_name)

        # 7.14sec
        self.PlotWaterFall
        InsertFigureToFile(self.fig_path, self.output_file_path, self.addFlag)

    @property
    def PlotWaterFall(self):
        """活跃时间瀑布图"""
        fontsize = 20

        st = time.time()
        fig, axes = joypy.joyplot(
            self.frequent,
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
        plt.title(u"投入时间段概率分布（近7天）", fontsize=fontsize+5)
        plt.grid(linestyle="--", alpha=0.45)

        plt.savefig(self.fig_path, dpi=150, bbox_inches='tight')
        plt.close()

    def LastMonthBar(self, fig_id, fig_name):
        """画最近1月的投入时间柱形图

        Args:
            fig_id ([type]): 图片编号
            fig_name ([type]): 图片名称
        """
        NdayActivateTime = LastNdayActivateTime(
            self.last_month, self.today_dt, back_days=30)
        self.activate = SumTimePerDay(NdayActivateTime)

        self.fig_path = generate_fig_path(date_list=GetNDayList(self.today_dt, 30),
                                          root_path=self.output_path,
                                          fig_type=self.fig_type,
                                          fig_id=fig_id, fig_name=fig_name)

        self.PlotMonthBar
        InsertFigureToFile(self.fig_path, self.output_file_path, self.addFlag)

    @property
    def PlotMonthBar(self):
        """活跃时间柱形图"""
        date_list = GetNDayList(self.today_dt, 30)
        md_list = list(map(ymd2md, date_list))

        fig, ax = plt.subplots(figsize=(8, 6))

        days = np.arange(30)
        plt.bar(days, height=self.activate,
                label='activate', color=cm.hsv(0.6), alpha=0.8)

        avg_hours = self.activate.mean()
        plt.axhline(y=avg_hours, ls=":", lw=4, c=cm.hsv(0))

        # params
        fontsize = 20
        plt.legend(fontsize=fontsize-2, loc='upper left')
        plt.xlabel(u"日期", fontsize=fontsize)
        plt.ylabel(u"时长(小时)", fontsize=fontsize)
        plt.xticks(fontsize=fontsize-5)
        plt.yticks(fontsize=fontsize)
        plt.xticks(ticks=range(0, 30+1, 4), labels=md_list[::4])

        plt.title("每日投入总时长(近30天，平均{0:.2f}小时)".format(avg_hours),
                  fontsize=fontsize+5)

        plt.savefig(self.fig_path, dpi=150, bbox_inches='tight')
        plt.close()

    def LastMonthPie(self, fig_id, fig_name):
        """画最近1月的投入时间饼图

        Args:
            fig_id ([type]): 图片编号
            fig_name ([type]): 图片名称
        """
        data_of_BrokenBarh, _ = DataFormatForBrokenBarh(
            self.work_states, self.last_month, self.today_dt, back_days=30)
        self.data_of_pie = DataFormatForPie(
            data_of_BrokenBarh, self.work_states)

        self.fig_path = generate_fig_path(date_list=GetNDayList(self.today_dt, 30),
                                          root_path=self.output_path,
                                          fig_type=self.fig_type,
                                          fig_id=fig_id,
                                          fig_name=fig_name)
        self.PlotPie
        InsertFigureToFile(self.fig_path, self.output_file_path, self.addFlag)

    @property
    def PlotPie(self):
        """各类别任务投入比例饼图"""
        fig, ax = plt.subplots(figsize=(8, 6))

        data, otherdata, mergeIdx, splitIdx = \
            MergeDataOfBelowThreshold(self.data_of_pie)

        # process color and label
        colors = np.array([cm.Set3(i/len(self.work_states))
                           for i in range(len(self.work_states))])
        work_states = np.array(self.work_states)
        if otherdata > 0:
            colors = list(colors[splitIdx]) + [cm.hsv(0)]
            ohter_labels = '\n'.join(work_states[mergeIdx])
            work_states = list(work_states[splitIdx]) + ['others']
        else:
            colors = list(colors[splitIdx])
            ohter_labels = 'null'
            work_states = list(work_states[splitIdx])

            data = data[:-1]

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
        plt.title(u"各类别任务投入比例（近30天）", fontsize=fontsize+5)
        plt.text(x=1.8, y=-1.2,
                 s="*others(< 10%):\n"+ohter_labels,
                 fontsize=fontsize+5)

        # drop the redundant of labels via `dict.keys()`
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(),
                   bbox_to_anchor=(1.4, 1), loc='upper right',
                   ncol=1, fontsize=fontsize)
        plt.axis('equal')

        plt.savefig(self.fig_path, dpi=150, bbox_inches='tight')
        plt.close()

    def LastDayCompBar(self, fig_id, fig_name):
        """画最近1天的每个label的投入与预计时间的对比柱形图

        Args:
            fig_id ([type]): 图片编号
            fig_name ([type]): 图片名称
        """
        self.compbar, self.labels, self.option = DateFormatForCompBar(
            self.last_day)
        self.fig_path = generate_fig_path(date_list=GetNDayList(self.today_dt, 1),
                                          root_path=self.output_path,
                                          fig_type=self.fig_type,
                                          fig_id=fig_id, fig_name=fig_name)

        self.PlotCompBar
        InsertFigureToFile(self.fig_path, self.output_file_path, self.addFlag)

    @property
    def PlotCompBar(self):
        """投入与预计时间的对比柱形图"""
        fig, ax = plt.subplots(figsize=(8, 6))

        xx = np.arange(self.compbar.shape[1])

        # color
        color_pred = 'w'
        edgecolor_real = 'k'
        edgecolor_pred = 'k'

        # label
        label_pred = 'prediction'

        width = 0.8

        fontsize = 20

        offset = 1.5
        for x_i in xx:
            data_i = self.compbar[:, x_i]
            real, pred = data_i[0], data_i[1]
            gap = abs(real-pred)

            if self.option[x_i]:
                color_real = 'w'
                label_real = 'real(optional)'
            else:
                color_real = cm.hsv(0.4)
                label_real = 'real'

            x = x_i * offset
            if pred >= real:
                plt.bar(x, height=real, label=label_real, width=width,
                        color=color_real, alpha=0.8, hatch='x', edgecolor=edgecolor_real)
                plt.bar(x, height=gap, bottom=real, label=label_pred, width=width,
                        color=color_pred, alpha=0.5, edgecolor=edgecolor_pred)
            else:
                plt.bar(x, height=pred, label=label_pred, width=width,
                        color=color_pred, alpha=0.5, edgecolor=edgecolor_pred)
                plt.bar(x, height=gap, bottom=pred, label=label_real, width=width,
                        color=color_real, alpha=0.8, hatch='x', edgecolor=edgecolor_real)

            y_i = max(pred, real)
            plt.text(x, y_i+0.05, s=self.labels[x_i],
                     ha='center', va='bottom', fontsize=fontsize-5)

        # params
        # drop the redundant of labels via `dict.keys()`
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(),
                   loc='upper right',
                   ncol=1, fontsize=fontsize)

        vmax = self.compbar.max()
        plt.ylim([0, vmax+1.8])
        plt.xlabel(u"任务", fontsize=fontsize)
        plt.ylabel(u"时长(小时)", fontsize=fontsize)
        plt.xticks(fontsize=fontsize)
        plt.yticks(fontsize=fontsize)

        task_labels = ['task%d' % (i+1) for i in xx]
        plt.xticks(ticks=xx*offset, labels=task_labels)
        plt.title("各任务投入与预测时间对比（当天）", fontsize=fontsize+5)

        plt.savefig(self.fig_path, dpi=150, bbox_inches='tight')
        plt.close()

    def LastYearCalendar(self, fig_id, fig_name):
        """画最近1年的投入时间日历图

        Args:
            fig_id ([type]): 图片编号
            fig_name ([type]): 图片名称
        """
        self.YearCalendar = DataFormatForTomato(self.last_year)

        self.fig_path = generate_fig_path(date_list=GetNDayList(self.today_dt, 365),
                                          root_path=self.output_path,
                                          fig_type=self.fig_type,
                                          fig_id=fig_id, fig_name=fig_name)

        self.PlotYearCalendar
        InsertFigureToFile(
            self.fig_path, self.output_file_path, self.addFlag, width=500)

    @property
    def PlotYearCalendar(self):
        """活跃时间柱形图"""
        fig, ax = plt.subplots(figsize=(8, 6))

        ax, pcm = calmap.yearplot(self.YearCalendar,
                                  #   vmin=0,
                                  #   vmax=5,
                                  year=self.today_dt.year,
                                  daylabels=calendar.day_abbr[:],
                                  dayticks=[0, 2, 4, 6],
                                  monthlabels=calendar.month_abbr[1:],
                                  monthticks=True,
                                  #   monthly_border=True,
                                  border_lw=0.1,
                                  cmap=cm.Greens,
                                  )
        cbar = fig.colorbar(mappable=pcm, ax=ax,
                            orientation='horizontal',
                            shrink=0.3,
                            fraction=0.15, pad=0.1,
                            )
        fontsize = 20
        plt.text(x=35, y=-4.7, s=u'有效专注次数', fontsize=fontsize-5)

        # cbar.set_label(u'执行次数', rotation=0, fontsize=fontsize-5)
        plt.title(u"效率统计（近12个月）", fontsize=fontsize-3)
        plt.savefig(self.fig_path, dpi=150, bbox_inches='tight')
        plt.close()


class InformationAnalyze:
    def __init__(self, today_dt, last_day, last_month,
                 output_path, output_file_path):
        """初始化

        Args:
            last_day ([type]): 最近1天的数据（即今天）
            last_week ([type]): 最近7天的数据
            last_month ([type]): 最近30天的数据
            output_path ([type]): 数据分析结果在本项目的保存路径
            output_file_path ([type]): 数据分析结果待插入图片到文件的路径
        """
        self.today_dt = today_dt
        assert len(last_day) > 0, \
            u"今天的信息输入还没填写！请先在文档填写，或把`information`参数值设为False"
        self.last_day = last_day
        self.last_month = last_month

        self.output_path = output_path
        self.output_file_path = output_file_path

        self.addFlag = '#### 3. 信息摄入'

        self.fig_type = "information"

    @property
    @class_func_timer("InformationAnalyze")
    def Analyze(self):
        """可视化分析"""
        self.LastDayPie(fig_id=1, fig_name='dayinformation-pie')
        self.LastDayBar(fig_id=2, fig_name='dayinformation-stackbar')
        self.LastMonthStackBar(fig_id=3, fig_name='monthinformation-stackbar')

    def LastDayPie(self, fig_id, fig_name):
        """画最近1天的信息摄入饼图

        Args:
            fig_id ([type]): 图片编号
            fig_name ([type]): 图片名称
        """
        self.data, self.labels = GetQualityDuration(self.last_day)
        self.fig_path = generate_fig_path(date_list=GetNDayList(self.today_dt, 1),
                                          root_path=self.output_path,
                                          fig_type=self.fig_type,
                                          fig_id=fig_id, fig_name=fig_name)

        self.PlotPieForInformation
        InsertFigureToFile(self.fig_path, self.output_file_path, self.addFlag)

    @property
    def PlotPieForInformation(self):
        """信息饼图"""
        fig, ax = plt.subplots(figsize=(8, 6))

        # process color and label
        colors = [cm.Set3(i/len(self.labels)) for i in range(len(self.labels))]

        # Segment the one with the largest percentage
        explode = [0] * self.data.shape[0]
        explode[np.argmax(self.data)] = 0.1

        # plot pie
        patches, l_text, p_text = \
            plt.pie(x=self.data, explode=explode, labels=self.labels,
                    labeldistance=1.1, colors=colors, autopct='%.0f%%',
                    shadow=True, startangle=90, pctdistance=0.6)

        # params
        fontsize = 20
        list(map(lambda t: t.set_size(fontsize), l_text))
        list(map(lambda t: t.set_size(fontsize), p_text))
        plt.title(u"信息摄入质量比例（当天）", fontsize=fontsize+5)

        # drop the redundant of labels via `dict.keys()`
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(),
                   bbox_to_anchor=(1.4, 1), loc='upper right',
                   ncol=1, fontsize=fontsize+5)
        plt.axis('equal')

        plt.savefig(self.fig_path, dpi=150, bbox_inches='tight')
        plt.close()

    def LastDayBar(self, fig_id, fig_name):
        """画最近1天的信息摄入质量柱形图

        Args:
            fig_id ([type]): 图片编号
            fig_name ([type]): 图片名称
        """
        self.stacked_bar_data = DataFormatForStackBar(self.last_day)

        self.fig_path = generate_fig_path(date_list=GetNDayList(self.today_dt, 1),
                                          root_path=self.output_path,
                                          fig_type=self.fig_type,
                                          fig_id=fig_id, fig_name=fig_name)

        self.PlotBarForInformation
        InsertFigureToFile(self.fig_path, self.output_file_path, self.addFlag)

    @property
    def PlotBarForInformation(self):
        """信息摄入质量柱形图"""
        quality_list = self.stacked_bar_data.quality.values
        columns = list(self.stacked_bar_data.columns)
        columns.remove('quality')
        colors = [cm.Set3(i/len(columns)) for i in range(len(columns))]

        del self.stacked_bar_data['quality']
        stacked_bar_data = self.stacked_bar_data.values
        stacked_bar_data[np.isnan(stacked_bar_data)] = 0

        # plot by stacking
        val = stacked_bar_data[:, 0]
        p1 = plt.bar(np.arange(len(quality_list)), val,
                     width=0.5, color=colors[0], tick_label=quality_list)
        sub_matrix = stacked_bar_data[:, 0:1]
        csum = np.cumsum(sub_matrix, axis=1)[:, -1]
        csum = csum.flatten()

        for i in range(1, len(columns)):
            sub_matrix = stacked_bar_data[:, 0:i]
            csum = np.cumsum(sub_matrix, axis=1)[:, -1]
            csum = csum.flatten()

            val = stacked_bar_data[:, i]
            p3 = plt.bar(np.arange(len(quality_list)), val,
                         width=0.5, bottom=csum, color=colors[i])

        sub_matrix = stacked_bar_data[:, :]
        csum = np.cumsum(sub_matrix, axis=1)[:, -1]
        csum = csum.flatten()

        # params
        fontsize = 20
        plt.legend(fontsize=fontsize-2, loc='upper right', labels=columns)
        plt.xlabel(u"信息质量", fontsize=fontsize)
        plt.ylabel(u"时长(分钟)", fontsize=fontsize)
        plt.xticks(fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        plt.ylim([0, max(csum)*1.2])
        plt.title("信息摄入时长（当天）", fontsize=fontsize+5)

        plt.savefig(self.fig_path, dpi=150, bbox_inches='tight')
        plt.close()

    def LastMonthStackBar(self, fig_id, fig_name):
        """画最近1月的信息柱形堆叠图

        Args:
            fig_id ([type]): 图片编号
            fig_name ([type]): 图片名称
        """
        self.stacked_bar_data = DataFormatForMonthStackBar(
            self.last_month, self.today_dt)

        self.fig_path = generate_fig_path(date_list=GetNDayList(self.today_dt, 30),
                                          root_path=self.output_path,
                                          fig_type=self.fig_type,
                                          fig_id=fig_id, fig_name=fig_name)

        self.PlotMonthStackBarAndCurveForInformation
        InsertFigureToFile(self.fig_path, self.output_file_path, self.addFlag)

    @property
    def PlotMonthStackBarAndCurveForInformation(self):
        """近一个月的信息柱状堆叠图+曲线图（双坐标）"""
        date_list = self.stacked_bar_data['date'].tolist()

        columns = self.stacked_bar_data.columns.tolist()
        columns.remove('date')
        colors = [cm.Set3(i/len(columns)) for i in range(len(columns))]

        fig, ax = plt.subplots(figsize=(8, 6))

        # plot by stacking
        stacked_bar_data = self.stacked_bar_data[columns].values
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
                        label=columns[i],)
            # tick_label=list(map(ymd2md, date_list)))

        sub_matrix = stacked_bar_data[:, :]
        csum = np.cumsum(sub_matrix, axis=1)[:, -1]
        csum = csum.flatten()

        # curve
        ax1 = ax.twinx()
        res_sum = np.sum(stacked_bar_data, axis=1)
        res_sum[res_sum == 0] = 1e-7
        high_rate = stacked_bar_data[:, 0] / res_sum
        ax1.plot(np.arange(len(date_list)), high_rate*100,
                 color='red', label='rate of high',
                 marker='o', markersize=5)

        # params
        fontsize = 20
        plt.xlabel(u"日期", fontsize=fontsize)
        for tick in ax.get_xticklabels():
            tick.set_rotation(30)
        fig.legend(loc="upper right", bbox_to_anchor=(
            1, 1), bbox_transform=ax.transAxes, fontsize=fontsize)
        plt.title(u"信息摄入总体情况（近30天）", fontsize=fontsize+5)
        plt.grid(linestyle='--', alpha=0.9)

        ax.set_label(columns)
        ax.tick_params(labelsize=fontsize)
        ax.set_ylabel(u"时长(分钟)", fontsize=fontsize)
        ax.set_ylim([0, max(csum)*1.2])
        md_list = list(map(ymd2md, date_list))
        ax.set_xticks(range(0, 30, 4))
        ax.set_xticklabels(md_list[::4])

        ax1.set_label("high rate")
        ax1.tick_params(labelsize=fontsize)
        ax1.set_ylabel("%", fontsize=fontsize)
        ax1.set_ylim([0, 120])

        plt.savefig(self.fig_path, dpi=150, bbox_inches='tight')
        plt.close()


class HarvestAnalyze:
    def __init__(self, today_dt, last_year,
                 output_path, output_file_path):
        """初始化

        Args:
            last_month ([type]): 最近30天的数据
            output_path ([type]): 数据分析结果在本项目的保存路径
            output_file_path ([type]): 数据分析结果待插入图片到文件的路径
        """
        self.today_dt = today_dt
        assert len(last_year) > 0, \
            "最近一年的收获还没填写！请先在文档填写，或把`harvest`参数值设为False"
        self.last_year = last_year

        self.output_path = output_path
        self.output_file_path = output_file_path

        self.addFlag = '#### 4. 收获'

        self.fig_type = "harvest"

    @property
    @class_func_timer("HarvestAnalyze")
    def Analyze(self):
        """可视化分析"""
        self.LastMonthCloud(fig_id=1, fig_name='harvest-cloud')
        self.LastMonthBar(fig_id=2, fig_name='harvest-vbar')

    def LastMonthCloud(self, fig_id, fig_name):
        """画最近1月的收获云图

        Args:
            fig_id ([type]): 图片编号
            fig_name ([type]): 图片名称
        """
        self.word_list = MergeWord(self.last_year)

        self.fig_path = generate_fig_path(date_list=GetNDayList(self.today_dt, 365),
                                          root_path=self.output_path,
                                          fig_type=self.fig_type,
                                          fig_id=fig_id, fig_name=fig_name)

        self.PlotWordCloudForHarvest
        InsertFigureToFile(
            self.fig_path, self.output_file_path, self.addFlag, width=300)

    @property
    def PlotWordCloudForHarvest(self):
        """收获云图"""
        text_cut = ' '.join(self.word_list)

        word_cloud = WordCloud(font_path="simsun.ttc",
                               background_color="white",
                               max_font_size=40)
        word_cloud.generate(text_cut)

        plt.subplots(figsize=(8, 6))
        plt.imshow(word_cloud)
        plt.axis("off")

        # params
        fontsize = 30
        plt.title(u"收获概览（近1年）", fontsize=fontsize)

        plt.savefig(self.fig_path, dpi=150, bbox_inches='tight')
        plt.close()

    def LastMonthBar(self, fig_id, fig_name):
        """画最近1月的收获云图

        Args:
            fig_id ([type]): 图片编号
            fig_name ([type]): 图片名称
        """
        self.word_list = MergeWord(self.last_year)

        self.fig_path = generate_fig_path(date_list=GetNDayList(self.today_dt, 365),
                                          root_path=self.output_path,
                                          fig_type=self.fig_type,
                                          fig_id=fig_id, fig_name=fig_name)

        self.PlotMonthvBar
        InsertFigureToFile(
            self.fig_path, self.output_file_path, self.addFlag, width=300)

    @property
    def PlotMonthvBar(self):
        word = pd.value_counts(self.word_list)
        data = word.to_list()
        label = word.index.to_list()
        data.reverse()
        label.reverse()

        fig, ax = plt.subplots(figsize=(8, 6))
        fontsize = 15
        b = ax.barh(range(len(label)), data, color='deeppink', height=0.7)

        # 为横向水平的柱图右侧添加数据标签
        for rect in b:
            w = rect.get_width()
            ax.text(w, rect.get_y()+rect.get_height()/2, '%d' %
                    int(w), ha='left', va='center', fontsize=fontsize)

        ax.set_yticks(range(len(label)))
        ax.set_yticklabels(label, fontsize=fontsize)
        plt.xticks(fontsize=fontsize)
        plt.xlabel("次数", fontsize=fontsize)
        plt.title(u"收获统计（近1年）", fontsize=2*fontsize)

        plt.savefig(self.fig_path, dpi=150, bbox_inches='tight')
        plt.close()

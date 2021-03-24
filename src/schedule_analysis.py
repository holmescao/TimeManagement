'''
Author: Holmescao
Date: 2021-03-16 12:57:18
LastEditors: Holmescao
LastEditTime: 2021-03-24 22:52:24
Description: 自动分析schedule文档信息，用于个人时间分析与管理
RunTime：15 sec
'''

import datetime
from utils.data_analyze import Analyze
from utils.data_process import Schedule
from utils.common_function import GetOutputFilePath
from config import config
import argparse
import warnings

warnings.filterwarnings("ignore")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--activate', type=bool, default=True,
                        help='activate data visualization')
    parser.add_argument('--information', type=bool, default=True,
                        help='activate data visualization')
    parser.add_argument('--harvest', type=bool, default=True,
                        help='activate data visualization')
    parser.add_argument('--fast', type=bool, default=False,
                        help='use fast version to visualization')
    parser.add_argument('--today_dt', default=datetime.date.today()-datetime.timedelta(days=0),
                        help='today datetime format')
    args = parser.parse_args()

    schedule = Schedule(args=args,
                        root_path=config['path']['root_path'],
                        tmp_path=config['path']['tmp_path'],
                        data_columns=config['data_columns'])
    schedule.HandleDailySchedule

    analyze = Analyze(args=args,
                      work_states=config['work_states'],
                      input_path=config['path']['tmp_path'],
                      output_path=config['path']['output_path'],
                      output_file_path=GetOutputFilePath(args.today_dt, root_path=config['path']['root_path']))
    analyze.DataAnalyze

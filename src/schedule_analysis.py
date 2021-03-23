'''
Author: Holmescao
Date: 2021-03-16 12:57:18
LastEditors: Holmescao
LastEditTime: 2021-03-22 16:31:09
Description: 自动分析schedule文档信息，用于个人时间分析与管理
RunTime：15 sec
'''

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
                      output_file_path=GetOutputFilePath(root_path=config['path']['root_path']))
    analyze.DataAnalyze

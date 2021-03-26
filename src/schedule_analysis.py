'''
Author: Holmescao
Date: 2021-03-16 12:57:18
LastEditors: Holmescao
LastEditTime: 2021-03-26 15:32:20
Description: 自动分析schedule文档信息，用于个人时间分析与管理
RunTime：15 sec
'''


import datetime
from utils.data_analyze import Analyze
from utils.data_process import Schedule
from utils.common_function import GetOutputFilePath, mkdir, OpenFile, WriteFile
from config import config
import argparse
import shutil
import warnings
warnings.filterwarnings("ignore")


def DemoSetting(args, config):
    """demo相关设置

    Args:
        args ([type]): 超参数
        config ([type]): 配置参数

    Returns:
        [type]: 超参数和配置参数
    """
    args.activate = True
    args.information = True
    args.harvest = True
    args.fast = False
    args.today_dt = datetime.date.today()

    config['path']['root_path'] = './demo/schedule/'
    config['path']['tmp_path'] = './demo/tmp/'
    config['path']['output_path'] = './demo/output/'
    mkdir(config['path']['root_path'])

    year = str(args.today_dt.year).zfill(4)
    month = str(args.today_dt.month).zfill(2)
    day = str(args.today_dt.day).zfill(2)
    demo_file_path = f'./demo/schedule/{year}年{month}月{day}日.md'
    module_file_path = "../模板/xxxx年xx月xx日.md"
    shutil.copyfile(module_file_path, demo_file_path)

    data = OpenFile(demo_file_path)
    idx = data.index("# xxxx年xx月xx日Schedule\n")
    data[idx] = f"# {year}年{month}月{day}日Schedule\n"
    WriteFile(demo_file_path, data)

    return args, config


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
    parser.add_argument('--demo', type=bool, default=False,
                        help='run demo.')
    args = parser.parse_args()

    if args.demo:
        args, config = DemoSetting(args, config)

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

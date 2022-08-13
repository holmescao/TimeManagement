import platform
import time
import os
import datetime
from utils.data_analyze_year import Analyze
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
    args.fig_cloud = False
    args.schedule_cloud = False

    config['path']['root_path'] = args.script_path + 'demo/schedule/'
    config['path']['tmp_path'] = args.script_path + 'demo/tmp/'
    config['path']['output_path'] = args.script_path + 'demo/output/'
    mkdir(config['path']['root_path'])

    year = str(args.today_dt.year).zfill(4)
    month = str(args.today_dt.month).zfill(2)
    day = str(args.today_dt.day).zfill(2)
    demo_file_path = args.script_path + \
        f'demo/schedule/{year}年{month}月{day}日.md'
    module_file_path = args.script_path + "module/xxxx年xx月xx日.md"
    shutil.copyfile(module_file_path, demo_file_path)

    data = OpenFile(demo_file_path)
    idx = data.index("# xxxx年xx月xx日Schedule\n")
    data[idx] = f"# {year}年{month}月{day}日Schedule\n"
    WriteFile(demo_file_path, data)

    return args, config


def GitFlow(path, commit):
    print('uploading %s to cloud.' % path)

    st = time.time()

    cur_system = platform.system()
    if cur_system == "Windows":
        cd = f"cd /d {path} && "
    else:
        cd = f"cd {path} && "

    os.system(cd+"git add .")
    os.system(cd+"git status")
    os.system(cd+f"git commit -m '{commit}'")
    status = os.system(cd+"git push origin master")

    assert status == 0, "fail: can't upload to cloud!"

    print("git usetime: %.2f sec" % (time.time()-st))


def str_to_bool(str):
    return True if str == 'True' else False


def ParamsProcess(parser):
    args = parser.parse_args()
    parser.add_argument('--today_dt', default=datetime.date.today()-datetime.timedelta(days=args.day),
                        help='today datetime format')
    args = parser.parse_args()

    args.fig_cloud = str_to_bool(args.fig_cloud)
    args.schedule_cloud = str_to_bool(args.schedule_cloud)
    args.demo = str_to_bool(args.demo)

    return args


def run(config):
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=bool, default=True,
                        help='activate data visualization')
    parser.add_argument('--activate', type=bool, default=True,
                        help='activate data visualization')
    parser.add_argument('--information', type=bool, default=True,
                        help='information data visualization')
    parser.add_argument('--harvest', type=bool, default=True,
                        help='harvest data visualization')
    parser.add_argument('--fast', type=bool, default=False,
                        help='use fast version to visualization')

    parser.add_argument('--day', type=int, default=0,
                        help='date to be analyzed')
    parser.add_argument('--fig_cloud', default="False",
                        help='upload figure to cloud')
    parser.add_argument('--schedule_cloud', default="False",
                        help='upload schedule file to cloud')
    parser.add_argument('--demo', default="False",
                        help='run demo.')
    parser.add_argument('--script_path', type=str, default="",
                        help='absolute path of the script.')

    args = ParamsProcess(parser)
    config['path']['root_path'] = args.script_path + \
        config['path']['root_path']
    config['path']['tmp_path'] = args.script_path + \
        config['path']['tmp_path']
    config['path']['output_path'] = args.script_path + \
        config['path']['output_path']

    if args.demo:
        args, config = DemoSetting(args, config)

    analyze = Analyze(args=args,
                      work_states=config['work_states'],
                      input_path=config['path']['tmp_path'],
                      output_path=config['path']['output_path'],
                      output_file_path=GetOutputFilePath(
                          args.today_dt, root_path=config['path']['root_path']),
                      cloud_root_path=config['path']['cloud_root_path'])

    return analyze


if __name__ == '__main__':

    analyze = run(config)

    analyze.YearDataAnalyze

'''
Author: Holmescao
Date: 2021-03-11 21:32:10
LastEditors: Holmescao
LastEditTime: 2021-04-11 17:33:54
Description: 
'''
config = {
    'path': {
        'root_path': './schedule/daily/',
        "tmp_path": './tmp/',
        "output_path": './output/',
        "cloud_root_path": "https://gitee.com/holmescao/figure-bed/raw/master/img/",
    },
    'data_columns': {
        "activate": ["date", "startTime", "endTime", "duration", "label", "taskId", "predTime", "option"],
        "information": ["date", "quality", "duration", "label"],
        "harvest": ["date", "label_l1", "label_l2"],
    },
    'work_states': ['learn', 'paper', 'write', 'think', 'code', 'survey', 'material', 'discussion', 'meeting', 'extra']
}

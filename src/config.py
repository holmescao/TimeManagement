'''
Author: Holmescao
Date: 2021-03-11 21:32:10
LastEditors: Holmescao
LastEditTime: 2021-03-30 10:19:20
Description: 
'''
config = {
    'path': {
        'root_path': './schedule/daily/',
        "tmp_path": './tmp/',
        "output_path": './output/',
    },
    'data_columns': {
        "activate": ["date", "startTime", "endTime", "duration", "label", "taskId", "predTime", "option"],
        "information": ["date", "quality", "duration", "label"],
        "harvest": ["date", "label_l1", "label_l2"],
    },
    'work_states': ['learn', 'paper', 'write', 'think', 'code', 'survey', 'material', 'discussion', 'meeting', 'extra']
}

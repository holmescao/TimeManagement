'''
Author: Holmescao
Date: 2021-04-15 19:34:00
LastEditors: Holmescao
LastEditTime: 2021-04-15 19:34:47
Description: 
'''

import git

with git.Repo.init(path='.') as repo:
    with open('test.file', 'w') as fobj:
        fobj.write('1st line\n')
    repo.index.add(items=['test.file'])
    repo.index.commit('write a line into test.file')

    with open('test.file', 'aw') as fobj:
        fobj.write('2nd line\n')
    repo.index.add(items=['test.file'])
    repo.index.commit('write another line into test.file')

'''
Author: Holmescao
Date: 2021-03-30 10:08:13
LastEditors: Holmescao
LastEditTime: 2021-03-30 14:40:32
Description:
'''
import calendar
from utils import calmap as calmap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

np.random.seed(sum(map(ord, 'calmap')))

all_days = pd.date_range('1/1/2015', periods=700, freq='D')
days = np.random.choice(all_days, 500)
events = pd.Series(np.random.randn(len(days)), index=days)

fig = plt.figure()

ax, pcm = calmap.yearplot(events,
                          vmin=0,
                          vmax=5,
                          year=2015,
                          daylabels=calendar.day_abbr[:],
                          dayticks=[0, 2, 4, 6],
                          monthlabels=calendar.month_abbr[1:],
                          monthticks=True,
                          monthly_border=False,
                          cmap=cm.Reds,
                          label='Less',
                          )

fig.colorbar(mappable=pcm, ax=ax,
            #  location='bottom',
             orientation='horizontal',
             shrink=0.25,
             fraction=0.1, pad=0.1,
             #  anchor=(0.05, 0.1), panchor=(2, 1),
             )
plt.title("2015")
plt.savefig("test.png", dpi=150, bbox_inches='tight')
plt.close()

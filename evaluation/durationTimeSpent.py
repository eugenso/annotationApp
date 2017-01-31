from __future__ import division
from Annotation import Annotation as Annotation
from operator import itemgetter, concat, add
from itertools import groupby
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import copy

import seaborn as sns
sns.set(style="whitegrid", color_codes=True)

A = Annotation('data/exportMedium.json')

dateDurations = sorted([(datetime.strptime(dateString, "%Y-%m-%d %H:%M:%S"),
                         int(durationString),
                         flag)
                        for dateString, durationString, flag
                        in A.ofAll(['dateTime', 'duration', 'proposalFlag'])],
                       key=itemgetter(0))


# discover sessions
# calculate the time between two consecutive
# tmpDates = copy.deepcopy(dates)
# now = datetime.now()
# deltas = reduce(lambda lst, d: lst+[d-lst.pop()]+[d],
#                 tmpDates[1:], [tmpDates[0]])[:-1]+[now-now]

# To create a datetime.delta subtract two datetimes accordingly
threshold = datetime(2016, 12, 1, 13, 5, 0) - datetime(2016, 12, 1, 13, 0, 0)
sessions = reduce(lambda lst, (date, duration, flag):
                       lst+[[(date, duration, flag)]]
                       if (date - lst[-1][-1][0])>threshold
                       else lst+[(lst.pop()+[(date, duration, flag)])],
                       dateDurations[1:], [[dateDurations[0]]])



sesssionDurations = map(lambda s: s[-1][0]-s[0][0], sessions)

secToHour = lambda sec: sec/3600
totalSessionDuration = reduce(add, sesssionDurations).total_seconds()
totalAnnotationDuration = A.durationToSec(sum(map(itemgetter(1), dateDurations)))

fig = plt.Figure()

bar_width = 0.5
label=['Total annotation time', 'Time spent to pick label']

plt.bar(0, secToHour(totalSessionDuration), label=label[0], color='r')
plt.bar(0, secToHour(totalAnnotationDuration), label=label[1], color='b')

plt.ylabel('Hours')
plt.xticks([0 + bar_width/2], ['Annotation time'])
x1,x2,y1,y2 = plt.axis()
plt.axis((0,0.5,y1,y2))
plt.legend(frameon=True, loc='best', fancybox=True, prop={'size':12})

plt.savefig('/home/kai/Dropbox/MA/thesis/img/durationTimeSpent.pdf',
            bbox_inches='tight',
            format='pdf')

plt.show()

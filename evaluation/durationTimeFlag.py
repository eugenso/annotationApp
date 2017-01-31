from __future__ import division
from Annotation import Annotation as Annotation
from operator import itemgetter, concat, add
from itertools import groupby
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import math
import copy

import seaborn as sns
sns.set(style="whitegrid", color_codes=True)


def autolabel(rect, label, ax):
    height = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., 0.94*height,
            label,
            ha='center', va='bottom')

def durationTimeFlag(dateDurations, name):
    # calculate the the difference between two consecutive dateTimes and
    # add it at the end.
    dateDurationDelta = reduce(lambda l, d: l+[d+[d[0]-l[-1][0]]],
                               dateDurations[1:], [dateDurations[0]])

    # Throw away the very first annotation because there is no delta to
    # compute. Than sort them according to the time delta, pick a
    # threshold to throw away the last annotation of a session, because
    # its delta spans across sessions. Finally group annotations according
    # to their proposal flag.
    nullDelta = datetime(1, 1, 1)-datetime(1, 1, 1)
    maxDelta = datetime(2016, 12, 1, 13, 5, 0) - datetime(2016, 12, 1, 13, 0, 0)

    threshold = lambda ddd: True if ddd[3] != nullDelta and ddd[3] < maxDelta else False
    #
    DDD = dict((flag, list(ddd)) for flag, ddd in
               groupby(sorted(filter(threshold, dateDurationDelta[1:]),
                              key=itemgetter(2)), key=itemgetter(2)))

    secToHour = lambda sec: sec/3600

    flags = ['proposal', 'no proposal', 'wrong proposal']

    totalTimes = np.array(map(lambda f: reduce(lambda l, r: l+r[3],
                                               DDD[f][1:],
                                               DDD[f][0][3]).total_seconds(), flags))

    totalDurations = np.array(map(lambda f: A.durationToSec(sum(map(itemgetter(1),
                                                                    DDD[f]))), flags))

    index = np.arange(len(flags))
    bar_width = 0.5

    fig, ax = plt.subplots()

    rects1 = ax.bar(index+(bar_width/2), np.repeat(1, len(flags)), bar_width, color='r')
    durationRatio = totalDurations/totalTimes
    rects2 = ax.bar(index+(bar_width/2), durationRatio,
                    bar_width, color='b')

    ax.set_yticks([])
    ax.set_xticks(index+bar_width)
    ax.set_xticklabels(flags, fontsize=16)
    ax.legend((rects1[0], rects2[0]),
              ('Total annotation time', 'Time spent to pick label'),
              frameon=True,
              loc='center right',
              fancybox=True,
              prop={'size':16})

    totalDurations/totalTimes

    map(lambda i: autolabel(rects1[i], str(int(secToHour(totalTimes[i])))+'h', ax),
        index)
    map(lambda i: autolabel(rects2[i], str(math.floor(durationRatio[i]*100))+'%', ax),
        index)

    plt.savefig('/home/kai/Dropbox/MA/thesis/img/{}.pdf'.format(name),
                bbox_inches='tight',
                format='pdf')

    plt.show()

matplotlib.rcParams.update({'font.size': 15})

A = Annotation('data/exportBig.json')

# sort all annotations chronologically. Use dateTime duration and
# proposalFlag
dateDurations = sorted([[datetime.strptime(dateString, "%Y-%m-%d %H:%M:%S"),
                         int(durationString),
                         flag]
                        for dateString, durationString, flag
                        in A.ofAll(['dateTime', 'duration', 'proposalFlag'])],
                       key=itemgetter(0))

stamp = datetime(2016, 12, 15)

durationTimeFlag(filter(lambda dD: dD[0] < stamp, dateDurations),
                 'durationTimeFlag')
durationTimeFlag(filter(lambda dD: dD[0] >= stamp, dateDurations),
                 'durationTimeFlagNew')

# fig, ax = plt.subplots()

# for i in index:
#     totalTime = reduce(lambda l, r: l+r[3],
#                        DDD[flags[i]][1:],
#                        DDD[flags[i]][0][3]).total_seconds()
#     totalDuration = A.durationToSec(sum(map(itemgetter(1), DDD[flags[i]])))
#     plt.bar(i, 1, label=label[0], color='r')
#     relDuration = secToHour(totalDuration)/secToHour(totalTime)
#     ax.bar(i, relDuration,
#            label=label[1], color='b')
#     rect = ax.patches[0]
#     height = rect.get_height()
#     ax.text(rect.get_x() + rect.get_width()/2, height + 5,
#             relDuration, ha='center', va='bottom')

# plt.ylabel('Hours')
# plt.xticks(index + bar_width/2, flags)
# plt.legend(frameon=True, loc='best', fancybox=True, prop={'size':12})
# plt.show()

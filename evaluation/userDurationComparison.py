from __future__ import division
from Annotation import Annotation
from sklearn.neighbors import KernelDensity

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


A = Annotation('data/exportMedium.json')

perUserDurations = A.perUser('duration')


# this should no longer be here when shiped
perUserDurations = dict((u, d) for u, d in perUserDurations.iteritems()
                        if u != 'chris' and u != 'eugen')


numOfUser = len(perUserDurations)
# Set up the matplotlib figure

bins = np.linspace(0, 300, 60)

f, subs = plt.subplots(numOfUser, figsize=(7, 7),
                       sharex=True, sharey=True)

s=0


# for user, durations in perUserDurations.iteritems():
#     fig = plt.Figure()
#     X = A.durationToSec(durations)
#     plt.hist(X, bins=bins, fc='#AAAAFF', label=user)
#     axes = plt.gca()
#     axes.set_xlim([0,300])
#     axes.set_ylim([0,100])
#     plt.xlabel('Annotation duration in sec')
#     plt.ylabel('Number of annotations')
#     plt.legend()
#     plt.show()

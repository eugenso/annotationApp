from __future__ import division
from Annotation import Annotation
from itertools import groupby
from operator import itemgetter

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

import seaborn as sns
sns.set(style="whitegrid")
sns.set_color_codes()

A = Annotation('data/exportMedium.json')
key = itemgetter('proposalFlag')

g = dict((flag, A.durationToSec(map(itemgetter('duration'), annotations)))
              for flag, annotations in groupby(sorted(A.all, key=key), key=key))

labels=['proposal', 'no proposal', 'wrong proposal']

xPlot = np.linspace(-3, 150, 1000)[:, np.newaxis]

c = {'no proposal': 'g',
     'wrong proposal': 'r',
     'proposal': 'b'}

fig = plt.Figure()

for label in labels:
    fit_alpha, fit_loc, fit_beta = stats.gamma.fit(g[label], floc=0)
    rv = stats.gamma(fit_alpha, loc=fit_loc, scale=fit_beta)
    Y = rv.pdf(xPlot)
    # plt.fill(xPlot[:, 0], Y, fc='#AAAAFF', alpha=0.5)
    plt.plot([rv.mean(), rv.mean()], [0, rv.pdf(rv.mean())], linewidth=3, c=c[label])
    plt.plot(xPlot[:, 0], Y, linewidth=3, c=c[label], label=label)
    print rv.mean(), rv.pdf(rv.mean())



x1,x2,y1,y2 = plt.axis()
plt.axis((0,150,0,y2))

plt.xlabel('Duration in sec', fontsize=12)
plt.ylabel('Density', fontsize=12)
plt.legend()

plt.savefig('/home/kai/Dropbox/MA/thesis/img/flagDurationGamma.png',
            bbox_inches='tight',
            format='png')

plt.show()

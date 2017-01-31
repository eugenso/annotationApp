from Annotation import Annotation
from itertools import groupby
from operator import itemgetter
from scipy.stats import norm

import matplotlib.pyplot as plt
import numpy as np

A = Annotation('data/exportMedium.json')

key = itemgetter('proposalFlag')
g = dict((flag, A.durationToSec(map(itemgetter('duration'), annotations)))
              for flag, annotations in groupby(sorted(A.all, key=key), key=key))

def stats(label):
    return np.mean(g[label]), np.std(g[label]), np.median(g[label])

labels=['no proposal', 'proposal', 'wrong proposal']

#map(stats, labels)

xPlot = np.linspace(-100, 300, 1000)[:, np.newaxis]

c = {'no proposal': 'green',
     'proposal': 'red',
     'wrong proposal': 'blue'}

fig = plt.Figure()

for label in labels:
    mean, std, median = stats(label)
    rv = norm(loc=mean, scale=std)
    Y = rv.pdf(xPlot)
    plt.fill(xPlot[:, 0], Y, fc='#AAAAFF', alpha=0.5)
    plt.plot(xPlot[:, 0], Y, linewidth=3, c=c[label], label=label)
    plt.plot([mean, mean], [0, rv.pdf(mean)], linewidth=3, c=c[label])

x1,x2,y1,y2 = plt.axis()
plt.axis((0,200,0,y2))

plt.xlabel('Duration', fontsize=12)
plt.ylabel('Density', fontsize=12)

plt.legend()
plt.show()

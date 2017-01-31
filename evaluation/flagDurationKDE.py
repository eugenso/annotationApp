from Annotation import Annotation
from itertools import groupby
from operator import itemgetter
from sklearn.neighbors import KernelDensity

import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns; sns.set(color_codes=True, style="whitegrid")


A = Annotation('data/exportMedium.json')

key = itemgetter('proposalFlag')
g = dict((flag, A.durationToSec(map(itemgetter('duration'), annotations)))
              for flag, annotations in groupby(sorted(A.all, key=key), key=key))

def stats(label):
    return np.mean(g[label]), np.std(g[label]), np.median(g[label])

labels=['proposal', 'no proposal', 'wrong proposal']

map(stats, labels)

xPlot = np.linspace(-10, 300, 1000)[:, np.newaxis]

c = {'no proposal': 'g',
     'proposal': 'b',
     'wrong proposal': 'r'}

fig = plt.Figure()

for label in labels:
    mean, std, median = stats(label)
    kde = KernelDensity(kernel='gaussian', bandwidth=std)
    density = kde.fit(np.array(g[label]).reshape(-1, 1)).score_samples(xPlot)
    Y = np.exp(density)
    plt.plot(xPlot[:, 0], Y, linewidth=3, c=c[label], label=label)
#    plt.fill(xPlot[:, 0], Y, fc='#AAAAFF', alpha=0.5)



x1,x2,y1,y2 = plt.axis()
plt.axis((0,150,0,y2))

plt.xlabel('Duration in sec', fontsize=12)
plt.ylabel('Density', fontsize=12)

plt.legend(loc='best', prop={'size':12}, frameon=True)

plt.savefig('/home/kai/Dropbox/MA/thesis/img/flagDurationKDE.pdf',
            bbox_inches='tight',
            format='pdf')

plt.show()


fig = plt.Figure()

for label in labels:
    mean, std, median = stats(label)
    kde = KernelDensity(kernel='gaussian', bandwidth=std)
    density = kde.fit(np.array(g[label]).reshape(-1, 1)).score_samples(xPlot)
    Y = np.exp(density)
    plt.plot(xPlot[:, 0], np.cumsum(Y), linewidth=3, c=c[label], label=label)
#    plt.fill(xPlot[:, 0], Y, fc='#AAAAFF', alpha=0.5)



x1,x2,y1,y2 = plt.axis()
plt.axis((0,200,0,y2))

plt.xlabel('Duration in sec', fontsize=12)
plt.ylabel('Density', fontsize=12)

plt.legend(frameon=True, loc='lower right')

plt.savefig('/home/kai/Dropbox/MA/thesis/img/flagDurationKDEcumsum.png',
            bbox_inches='tight',
            format='png')

plt.show()


# text = ': mean: {}, std: {}, median: {}'.format(np.mean(Y), np.std(Y), np.median(Y))
# plt.plot([np.mean(g[label]), np.mean(g[label])], [0, 0.5], linewidth=3, c=c[label])

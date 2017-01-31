from Annotation import Annotation
from itertools import groupby
from operator import itemgetter

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
sns.set(style="whitegrid")

A = Annotation('data/exportMedium.json')

key = itemgetter('proposalFlag')
g = dict((flag, A.durationToSec(map(itemgetter('duration'), annotations)))
              for flag, annotations in groupby(sorted(A.all, key=key), key=key))

labels=['proposal', 'no proposal', 'wrong proposal']
params = dict(bins=40, range=(0, 150), label=labels)
#sns.distplot(g[labels[0]], kde=False, color="b")
plt.hist((g[labels[0]], g[labels[1]], g[labels[2]]), normed=True, **params)

plt.xlabel('Duration in sec', fontsize=12)
plt.ylabel('Percentage', fontsize=12)

x1,x2,y1,y2 = plt.axis()
plt.axis((0,150,0,y2))

plt.legend(loc='best', prop={'size':12}, frameon=True)

plt.savefig('/home/kai/Dropbox/MA/thesis/img/flagDurationHist.pdf',
            bbox_inches='tight',
            format='pdf')
plt.show()

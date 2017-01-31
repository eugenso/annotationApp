from __future__ import division
from Annotation import Annotation
from nltk import FreqDist
from operator import itemgetter

import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns; sns.set(color_codes=True, style="whitegrid")


A = Annotation('data/exportMedium.json')

allLabels = map(lambda a: a[0][0], A.ofAll(['labels']))

dist =  FreqDist(allLabels)

keys = [u'Neg', u'Neut', u'Pos', u'No Sent', u'Undecided',  u'Irrelevant']

index = np.arange(len(keys))

bar_width = 0.5

fig = plt.Figure()
plt.bar(index,
        map(lambda k: dist[k]/len(allLabels), keys),
        bar_width)

plt.xlabel('Label')
plt.ylabel('% of annotations')
plt.xticks(index + bar_width/2, keys)
plt.legend()

plt.savefig('/home/kai/Dropbox/MA/thesis/img/annotationDist.pdf',
            bbox_inches='tight',
            format='pdf')

plt.show()

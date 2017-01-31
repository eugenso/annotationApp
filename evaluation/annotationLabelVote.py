from __future__ import division
from Annotation import Annotation
from nltk import FreqDist
from operator import itemgetter, attrgetter
from collections import Counter
from itertools import groupby, chain

import matplotlib.pyplot as plt
import numpy as np
import math

import seaborn as sns; sns.set(color_codes=True, style="whitegrid")

def autolabel(rect, label):
    height = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
            label,
            ha='center', va='bottom')


A = Annotation('data/exportMedium.json')

annoPerDocument = map(lambda annos: map(lambda a: a['labels'][0], annos[0]),
                      A.perDocument(3, ['annotations']) )

keys = [u'Neg', u'Neut', u'Pos', u'No Sent', u'Undecided',  u'Irrelevant']

annotations = list(chain(*annoPerDocument))

annoDist = FreqDist(annotations)

labelDist = FreqDist(map(lambda a: Counter(a).most_common()[0][0]
                          if len(set(a))<3 else None,
                         annoPerDocument))

annoCount = np.array(map(lambda k: annoDist[k], keys))
labelCount = np.array(map(lambda k: labelDist[k], keys))

index = np.arange(len(keys))
bar_width = 0.5

fig, ax = plt.subplots()

annoRatio = annoCount/len(annotations)
rects1 = ax.bar(index+(bar_width/2), annoRatio, bar_width, color='r')

labelRatio = labelCount/len(annotations)
labelPercent = labelCount/len(annotations)
rects2 = ax.bar(index+(bar_width/2), labelRatio, bar_width, color='b')


map(lambda i: autolabel(rects1[i], str(math.floor(annoRatio[i]*1000)/10)+'%'), index)
map(lambda i: autolabel(rects2[i], str(math.floor(labelPercent[i]*1000)/10)+'%'), index)

ax.set_xticks(index+bar_width)
ax.set_xticklabels(keys)
ax.legend((rects1[0], rects2[0]),
          ('% of all annotations', '% of labels by majority vote'),
          frameon=True,
          loc='Top right',
          fancybox=True,
          prop={'size':12})

plt.savefig('/home/kai/Dropbox/MA/thesis/img/annotationDist.pdf',
            bbox_inches='tight',
            format='pdf')

plt.show()

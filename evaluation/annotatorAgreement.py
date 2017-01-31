from __future__ import division
from Annotation import Annotation as Annotation
from operator import itemgetter
from itertools import groupby

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns; sns.set(color_codes=True, style="whitegrid")


A = Annotation('data/exportMedium.json')

documents, allAnnotations = zip(*A.perDocument(2, ['document', 'annotations']))

totalByAggrement = [(len(annotations),
                     len(set(map(lambda a: a['labels'][0], annotations))))
                    for annotations in allAnnotations]

rlt = [(length, [(num, len(list(v2))) for num,v2 in groupby(v1, key=itemgetter(1))])
       for length, v1 in groupby(sorted(totalByAggrement), key=itemgetter(0))]

# upper limit for the number of annotations per document
# rlt = rlt[:2]

numOfAnno, x = zip(*rlt)
maxDiff = max(i[0] for l in x for i in l)

fig = plt.Figure()

index = np.arange(len(rlt))
bar_width = (1-0.2)/maxDiff

color = ['g', 'b', 'r', 'm', 'c', 'k']
opacity = 0.6
label = ['full agreement']+map(lambda t: '{} different labels'.format(t), range(2, maxDiff+1))

for i in range(1, maxDiff+1):
    plt.bar(index+(bar_width*(i-1)),
            map(lambda lst: dict(lst).get(i, 0), x),
            bar_width,
            color=color[i-1],
            #alpha=opacity,
            label=label[i-1])


plt.xlabel('Number of annotations per document')
plt.ylabel('Occurrences')

plt.xticks(index + (bar_width*maxDiff)/2, numOfAnno)
plt.legend(loc='best', prop={'size':12}, frameon=True)

plt.savefig('/home/kai/Dropbox/MA/thesis/img/annotatorAgreement.pdf',
            bbox_inches='tight',
            format='pdf')

plt.show()

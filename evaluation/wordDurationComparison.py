from Annotation import Annotation
from nltk import word_tokenize
from itertools import groupby
from operator import itemgetter

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

import seaborn as sns; sns.set(style="white", color_codes=True)


def preprocessing(raw_document):
    urls = r'(http.+?(\s|$))'
    specialchar =  r'|[^A-Za-z\s]'
    doc = raw_document.lower()
    tokens = word_tokenize(re.sub(urls+specialchar, ' ', doc))
    return tokens

A = Annotation('data/exportMedium.json')

docAnnos = A.perDocument(1, ['document', 'annotations'])

# This blob produces a dictionary with the values ['proposal', 'no
# proposal', 'wrong proposal']. Values are tuples (number of word in document, proposalFlag, duration)
blob = dict((k, list(v)) for k, v in
         groupby(sorted([(len(preprocessing(document)),
                          annotation['proposalFlag'],
                          annotation['duration'])
                    for (document, annotations) in docAnnos
                    for annotation in  annotations],
                        key=itemgetter(1)), key=itemgetter(1)))

plotContent = dict((f, map(lambda (count, flag, duration):
                           (count, A.durationToSec(duration)), v))
                   for f, v in blob.iteritems())

smooth = lambda c: filter(lambda (x, s): s<100, c)
plotContent = dict((key, smooth(value)) for key, value in plotContent.iteritems())

labels = ['proposal', 'no proposal', 'wrong proposal']

sns.set(font_scale=1.5)
fig = plt.figure()
fig.set_size_inches(fig.get_size_inches()*1.5)

for label in labels:
    count, sec = zip(*plotContent[label])
    data = pd.DataFrame()
    data['Word count'] = np.array(count)
    data['Duration'] = np.array(sec)
    ax = sns.regplot(x='Word count', y='Duration', data=data, label=label)
    fig.add_axes(ax)


x1,x2,y1,y2 = plt.axis()
plt.axis((0,155,0,y2))
plt.legend(frameon=True)

plt.savefig('/home/kai/Dropbox/MA/thesis/img/wordDurationComparison.pdf',
            bbox_inches='tight',
            format='pdf')
plt.show()


# c={'proposal': 'r', 'no proposal': 'g', 'wrong proposal': 'b'}

# xp = np.linspace(0, 150, 50)

# for label in labels:
#     count, sec = zip(*plotContent[label])
#     plt.plot(count, sec, 'o', label=label, c=c[label])

# for label in labels:
#     count, sec = zip(*plotContent[label])
#     p1 = np.poly1d(np.polyfit(count, sec, 1))
#     plt.plot(xp, p1(xp), linewidth=3, label=label, c=c[label])

# plt.legend()
# plt.xlabel('Word count per document', fontsize=12)
# plt.ylabel('duration in sec', fontsize=12)

# plt.show()
# count, sec = zip(*plotContent['no proposal'])
# plt.plot(count, sec, 'o', label='no proposal')

# count, sec = zip(*plotContent['wrong proposal'])
# plt.plot(count, sec, 'o', label='wrong proposal')

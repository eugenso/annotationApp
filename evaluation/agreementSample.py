from __future__ import division
from Annotation import Annotation as Annotation
from operator import itemgetter
from itertools import groupby

A = Annotation('data/exportMedium.json')

totalByAggrement = [(len(annotations),
                     len(set(map(lambda a: a['labels'][0], annotations))),
                     '\t'.join([document]+map(lambda a: a['labels'][0], annotations)))
                    for document, annotations in A.perDocument(2, ['document', 'annotations'])]

rlt = dict((length, dict((num, map(itemgetter(2), v2))
                         for num,v2 in groupby(v1, key=itemgetter(1))))
           for length, v1 in groupby(sorted(totalByAggrement), key=itemgetter(0)))

c = [rlt[3][1][:20], rlt[3][2][:20], rlt[3][3][:20]]

for i in range(1, 4):
    with open(str(i)+'.tsv', 'w') as f:
        f.write('\n'.join(c[i-1]).encode('utf-8'))

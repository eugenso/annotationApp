from __future__ import division
from Annotation import Annotation as Annotation
from operator import itemgetter, concat
from itertools import groupby
from datetime import datetime
from sklearn.metrics import accuracy_score

import matplotlib.pyplot as plt
import numpy as np


def sortByTime(annotations):
    s = [(datetime.strptime(annotation['dateTime'], "%Y-%m-%d %H:%M:%S"), annotation)
         for annotation in annotations]
    return map(itemgetter(1), sorted(s, key=itemgetter(0)))


def lastHasProposal(annotations):
    if annotations[-1]['proposals'] and annotations[-1]['proposalFlag'] == 'proposal':
        flag = True
    else:
        flag = False
    return flag

def groupAnnotatorAgreement(allAnnotations):
    numDiffLabels = [(len(set(map(lambda a:a['labels'][0], annotations))), annotations)
                     for annotations in allAnnotations]
    k = itemgetter(0)
    return dict((k, map(itemgetter(1), v)) for k,v
                in groupby(sorted(numDiffLabels, key=k), key=k))


A = Annotation('data/exportMedium.json')

sortedAnnotations = [sortByTime(annotations[0]) for annotations
                     in A.perDocument(3, ['annotations'])
                     if len(annotations[0]) == 3]

lastPropAnnotations = filter(lastHasProposal, sortedAnnotations)

annotatorAgreement = groupAnnotatorAgreement(lastPropAnnotations)

print """
The goal is to predict the third annotation based on the two
previously seen annotations. This might enable to reduce the number of
annotations from 3 to 2.

In case all annotators agree, this might indicate that the annotation
for this document is obvious. Let's say we want to reduce the number
of annotations from 3 to 2. Then, if the first two annotators agree
upon the label there is no need to annotate it a third time. This
makes the classifier and its prediction obsolete. But gives an
oportunity to evaluate the system.

Next possible outcome is that two of the three annotators agree. This
can happen in the following ways. The first and second annotator agree
as in the previous case, then the third annotation becomes obsolete
again. If the first and second annotator disagree either all three can
disagree or the third annotator determines the label.

Given that the classifier only observed the first and second
annotation. How accurate does it predict the third label."""

keys = set(map(lambda a: a['labels'][0],
               reduce(concat,
                      reduce(concat, annotatorAgreement.values()))))
labelMap = dict(zip(keys, range(len(keys))))

undecisedAnnos = filter(lambda annos: True if annos[0]['labels'][0] != annos[1]['labels'][0]
                        else False,
                        annotatorAgreement[2])

trueY, predY = zip(*map(lambda a:
                        (labelMap[a[-1]['labels'][0]],
                         labelMap[a[-1]['proposals'][0]]), undecisedAnnos))

print 'acc for undecided annotations: {}'.format(accuracy_score(trueY, predY))

# for key, annotationsPerDoc in annotatorAgreement.iteritems():
#     trueY, predY = zip(*map(lambda a:
#                             (labelMap[a[-1]['labels'][0]],
#                              labelMap[a[-1]['proposals'][0]]), annotationsPerDoc))
#     print 'Number of different labels {}, acc on predicting the last {}'.format(
#         key, accuracy_score(trueY, predY))
    # print 'When all agree the last prediction has {} accuracy. On {} documents.'.format(
    #     accuracy_score(trueY, predY), len(annotationsPerDoc))
    # print zip(trueY, predY)

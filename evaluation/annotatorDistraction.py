from __future__ import division
from Annotation import Annotation as Annotation
from operator import itemgetter
from itertools import groupby

import matplotlib.pyplot as plt
import numpy as np

A = Annotation('data/exportMedium.json')

numAnnos = 3

threeAnnoPerDoc = filter(lambda d: len(d) == numAnnos,
                         map(lambda annos:
                             map(lambda a: (
                                 a['labels'][0],
                                 a['proposalFlag'],
                                 a['user']), annos[0]),
                             A.perDocument(numAnnos, ['annotations'])))

def wrongProposal(pD):
    return True if (pD[0][1] != 'wrong proposal' and
                    pD[1][1] != 'wrong proposal' and
                    pD[2][1] == 'wrong proposal') else False

wP = filter(wrongProposal, map(lambda pD: sorted(pD, key=itemgetter(1)),
                        threeAnnoPerDoc))



# def match(pD):
#     match = []
#     annotations = pD[0]
#     for annotation in annotations:
#         proposal = annotation['proposals'][0] if annotation['proposals'] else ''
#         if proposal == annotation['labels'][0]:
#             match.append((True, annotation))
#         else:
#             match.append((False, annotation))
#     return match

# numOfAnno = 3

# # ¯\_(ツ)_/¯ list of documents [ list of annotations [(do label and
# # proposal match?, annotation)]] these are all sets of annotations per
# # document for which there are 3 annotations.  The proposed label and
# # the annotated label neither match nor differ for all 3 annotations.
# allAnnotations = filter(lambda t: len(set(map(itemgetter(0), t)))>1
#                              and len(t)==numOfAnno,
#                              map(match, A.perDocument(numOfAnno, ['annotations'])))

# def vote(annotations):
#     map(lambda (m, a): a['labels'][0], annotations)

# map(lambda annotations: , allAnnotations)

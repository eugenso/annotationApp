from __future__ import division
from Annotation import Annotation as Annotation
from operator import itemgetter, add
from itertools import groupby, chain, combinations
from nltk import FreqDist
from sklearn.metrics import cohen_kappa_score
from createTable import tableBuilder

import matplotlib.pyplot as plt
import collections
import numpy as np

def fleissKappa(matrix, n):
    # according to wikipedia https://en.wikipedia.org/wiki/Fleiss'_kappa
    N = matrix.shape[0] # total number of fully annotated document
    k = matrix.shape[1] # number of labels
    #
    pj = np.sum(matrix, 0) / (N*n)
    Pi = (np.sum(np.power(matrix, 2), 1) - n) / (n*(n-1))
    Pd = np.sum(Pi) / N
    Pe = np.sum(np.power(pj, 2))
    #
    kappa = (Pd - Pe) / (1 - Pe)
    return kappa


def duplicates(lst):
    return [(item, count) for item, count in collections.Counter(lst).items() if count > 1]


A = Annotation('data/exportMedium.json')

maxAnno = 3

labelsPerDocDist = [FreqDist(map(lambda x: x['labels'][0], pD[0]))
                    for pD in A.perDocument(3, ['annotations'])
                    if len(pD[0]) == maxAnno]

labels = ['Neg', 'Neut', 'Pos', 'No Sent', 'Undecided', 'Irrelevant']

matrix = np.array([map(lambda l: fd[l] if fd.get(l) else 0, labels)
                   for fd in labelsPerDocDist])

fKappa = fleissKappa(matrix, maxAnno)
print " Fleiss' Kappa: {}".format(fKappa)

path = '/home/kai/Dropbox/MA/thesis/const/fleissKappa.tex'
with open(path, 'w+') as file:
            file.write(str(round(fKappa*1000)/1000))

userLabelPerDoc = [map(lambda x: (x['user'], x['labels'][0]), pD[0])
                   for pD in A.perDocument(2, ['annotations'])
                   if len(pD[0]) <= maxAnno]


############### filter test users ########################

meh = ['chris', 'eugen']
userLabelPerDoc = map(lambda x: filter(lambda y: not y[0] in meh, x),
                      userLabelPerDoc)

##########################################################

def filterDuplicates(lst):
    seen = []
    rlt = []
    for l in lst:
        if not l[0] in seen:
            rlt.append(l)
            #
        seen.append(l[0])
    return rlt

# g['chris']['eugen'] returns a list with pairs of labels for each
# document annotated by the two users.
g = dict((u1, dict((u2, map(lambda x: x[-2:], w))
                   for u2, w, in groupby(sorted(v, key=itemgetter(1)), key=itemgetter(1))))
         for u1, v in groupby(sorted(map(lambda ((u1, l1), (u2, l2)):
                                         sorted([u1,u2]) + [l1, l2],
                                         reduce(add, map(lambda l:
                                                         list(combinations(filterDuplicates(l), 2)),
                                                         userLabelPerDoc))),
                                     key=itemgetter(0)), key=itemgetter(0)))

users = sorted(set(list(chain(*map(lambda k: g[k].keys(), g.keys())))+g.keys()))

table = []
for user1 in users:
    row = []
    u1 = g.get(user1, None)
    for user2 in users:
        if u1:
            u2 = u1.get(user2, '')
            if u2:
                y1, y2 = zip(*u2)
                kappa = cohen_kappa_score(y1, y2, labels=labels)
                row.append(round(kappa*1000)/1000)
            else:
                row.append(u2)
                #
        else:
            row.append('')
        #
    table.append(row)


# add caption
table = [[''] + users] + map(lambda i: [users[i]]+table[i], range(len(users)))

tB = tableBuilder()
tB.createSimpleTable(table, True, '/home/kai/Dropbox/MA/thesis/table/iaaTable.tex')

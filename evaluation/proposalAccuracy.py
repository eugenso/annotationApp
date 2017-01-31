from sklearn.metrics import accuracy_score
from Annotation import Annotation
from operator import itemgetter
from itertools import chain

A = Annotation('data/exportMedium.json')

proposalAnnotations = filter(lambda a: a['proposalFlag']=='proposal'
                             and len(a['proposals'])>0
                             and len(a['labels'])>0, A.all)

labels, proposals = zip(*map(itemgetter('labels', 'proposals'), proposalAnnotations))


keys = list(set(chain(*labels+proposals)))
labelToIntMap = dict((keys[i], i) for i in range(len(keys)))

true, pred = zip(*[(labelToIntMap[l[0]], labelToIntMap[p[0]])
                   for (l, p) in zip(labels, proposals)])

print 'Proposal accuracy: ' + str(accuracy_score(true, pred))

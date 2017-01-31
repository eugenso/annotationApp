from Annotation import Annotation
from operator import itemgetter
from itertools import groupby

import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns; sns.set(color_codes=True, style="whitegrid")

def save(name, value):
    path = '/home/kai/Dropbox/MA/thesis/const/{}.tex'.format(name)
    with open(path, 'w+') as file:
        file.write(value)


A = Annotation('data/exportMedium.json')

annotations = A.ofAll(['labels', 'proposalFlag'])

perDocument = A.perDocument(3, ['dateTime'])

save('numberOfAnnotations', str(len(annotations)))
#

save('numberOfDocuments', str(len(perDocument)))
#

flags = dict((k, list(v)) for k, v in
             groupby(sorted(annotations, key=itemgetter(1)), key=itemgetter(1)))

save('numberOfProposals', str(len(flags['proposal'])))
save('numberOfNoProposals', str(len(flags['no proposal'])))
save('numberOfWrongProposals', str(len(flags['wrong proposal'])))

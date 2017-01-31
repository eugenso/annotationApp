from __future__ import division
import numpy as np
import json
from createTable import tableBuilder
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity


def annotationDocIndependent(dump):
    annotations = []

    for doc_id, document in dump.items():
        annotations += document['annotations']
        #

    proposal = []
    no_proposal = []
    wrong_proposal = []
    for annotation in annotations:
        if annotation['proposalFlag'] == 'proposal':
            proposal.append(annotation)
        elif annotation['proposalFlag'] == 'no proposal':
            no_proposal.append(annotation)
        elif annotation['proposalFlag'] == 'wrong proposal':
            wrong_proposal.append(annotation)

    # duration = lambda annos: map(lambda a:int(a['duration']), annos)

    totalMean = durationToSec(np.mean(duration(annotations)))
    propMean = durationToSec(np.mean(duration(proposal)))
    noPropMean = durationToSec(np.mean(duration(no_proposal)))
    wrongPropMean = durationToSec(np.mean(duration(wrong_proposal)))

    totalStd = durationToSec(np.std(duration(annotations)))
    propStd = durationToSec(np.std(duration(proposal)))
    noPropStd = durationToSec(np.std(duration(no_proposal)))
    wrongPropStd = durationToSec(np.std(duration(wrong_proposal)))

    totalMed = durationToSec(np.median(duration(annotations)))
    propMed = durationToSec(np.median(duration(proposal)))
    noPropMed = durationToSec(np.median(duration(no_proposal)))
    wrongPropMed = durationToSec(np.median(duration(wrong_proposal)))

    tableContent = [['Duration in sec', 'Total', 'Proposal', 'No Proposal', 'Wrong Proposal'],
                    ['Mean', totalMean, propMean, noPropMean, wrongPropMean],
                    ['Median', totalMed, propMed, noPropMed, wrongPropMed],
                    ['Std', totalStd, propStd, noPropStd, wrongPropStd]]

    tb = tableBuilder()
    tb.createSimpleTable(tableContent, True)


    print 'Duration in sec:'
    print 'Total mean: ' + str(durationToSec(np.mean(duration(annotations))))
    print 'Proposal mean: ' + str(durationToSec(np.mean(duration(proposal))))
    print 'No proposal mean: ' + str(durationToSec(np.mean(duration(no_proposal))))
    print 'Wrong proposal mean: ' + str(durationToSec(np.mean(duration(wrong_proposal))))
    print ''
    print 'Total std: ' + str(durationToSec(np.std(duration(annotations))))
    print 'Proposal std: ' + str(durationToSec(np.std(duration(proposal))))
    print 'No proposal std: ' + str(durationToSec(np.std(duration(no_proposal))))
    print 'Wrong proposal std: ' + str(durationToSec(np.std(duration(wrong_proposal))))
    print ''
    print 'Total median: ' + str(durationToSec(np.median(duration(annotations))))
    print 'Proposal median: ' + str(durationToSec(np.median(duration(proposal))))
    print 'No proposal median: ' + str(durationToSec(np.median(duration(no_proposal))))
    print 'Wrong proposal median: ' + str(durationToSec(np.median(duration(wrong_proposal))))
    print ''
    print 'Total min: ' + str(durationToSec(min(duration(annotations))))
    print 'Proposal min: ' + str(durationToSec(min(duration(proposal))))
    print 'No proposal min: ' + str(durationToSec(min(duration(no_proposal))))
    print 'Wrong proposal min: ' + str(durationToSec(min(duration(wrong_proposal))))
    print ''
    print 'Total max: ' + str(durationToSec(max(duration(annotations))))
    print 'Proposal max: ' + str(durationToSec(max(duration(proposal))))
    print 'No proposal max: ' + str(durationToSec(max(duration(no_proposal))))
    print 'Wrong proposal max: ' + str(durationToSec(max(duration(wrong_proposal))))
    print ''

    fig = plt.Figure()
    xs = np.array(map(lambda d: durationToSec(d), duration(annotations))).reshape(-1, 1)
    xs_plot = np.linspace(-5, max(xs)+10, 1000)[:, np.newaxis]
    plt.plot(xs, [0]*len(annotations), '*')
    kde = KernelDensity(kernel='gaussian', bandwidth=0.75).fit(xs)
    log_dens = kde.score_samples(xs_plot)
    plt.fill(xs_plot[:, 0], np.exp(log_dens), fc='#AAAAFF')
    x1,x2,y1,y2 = plt.axis()
    plt.axis((x1,x2,y1-0.01,y2))
    # plt.show()
    # fig = plt.Figure()
    # xs = np.array(map(lambda d: durationToSec(d), duration(annotations))).reshape(-1, 1)
    # bins = np.linspace(0, 300, 60)
    # plt.plot(xs, [0]*len(annotations), '*')
    # plt.hist(xs, bins=bins, fc='#AAAAFF')
    plt.show()
    #

def annotationByFlag(dump):
    maxAnno = 2

    fullyAnnoDoc = []

    for doc_id, document in dump.items():
        if len(document['annotations']) >= maxAnno:
            fullyAnnoDoc.append(document)

    proposal = []
    no_proposal = []
    wrong_proposal = []
    other = []
    for doc in fullyAnnoDoc:
        flags = set(map(lambda a: a['proposalFlag'], doc['annotations']))
        if flags - set(['proposal']) == set(['no proposal']):
            no_proposal.append(doc)
        elif flags - set(['proposal']) == set(['wrong proposal']):
            wrong_proposal.append(doc)
        elif flags - set(['proposal']) == set([]):
            proposal.append(doc)
        else:
            other.append(doc)
            #
    return proposal, no_proposal, wrong_proposal, other


def annotationTime(documents, objective):
    annotations = []
    for document in documents:
        annotations += document['annotations']
        print map(lambda a: a['proposalFlag'], document['annotations'])
        #
    proposal = []
    obj_proposal = []
    for annotation in annotations:
        if annotation['proposalFlag'] == 'proposal':
            proposal.append(annotation)
        elif annotation['proposalFlag'] == objective:
            obj_proposal.append(annotation)
            #

    propMean = durationToSec(np.mean(duration(proposal)))
    noPropMean = durationToSec(np.mean(duration(obj_proposal)))

    propStd = durationToSec(np.std(duration(proposal)))
    noPropStd = durationToSec(np.std(duration(obj_proposal)))

    propMed = durationToSec(np.median(duration(proposal)))
    noPropMed = durationToSec(np.median(duration(obj_proposal)))

    print 'Annotation Time for proposal(count: '+str(len(proposal))+')/'+objective+'(count: '+str(len(obj_proposal))+')'
    print 'Proposal mean: ' + str(durationToSec(np.mean(duration(proposal))))
    print objective.capitalize()+' mean: ' + str(durationToSec(np.mean(duration(obj_proposal))))
    print ''
    print 'Proposal std: ' + str(durationToSec(np.std(duration(proposal))))
    print objective.capitalize()+' std: ' + str(durationToSec(np.std(duration(obj_proposal))))
    print ''
    print 'Proposal median: ' + str(durationToSec(np.median(duration(proposal))))
    print objective.capitalize()+' median: ' + str(durationToSec(np.median(duration(obj_proposal))))



# dump = readAnnotationDump('data/exportMini.json')

# annotationDocIndependent(dump)

# proposal, no_proposal, wrong_proposal, other = annotationByFlag(dump)

# annotationTime(no_proposal, 'no proposal')
# annotationTime(wrong_proposal, 'wrong proposal')



# def readAnnotationDump(annotationName):
#     dump = None
#     with open(annotationName) as annotationFile:
#         dump = json.load(annotationFile)
#         #
#     return dump


# def durationToSec(duration):
#     return round(float(duration)/100)/10


# def duration(annotations):
#     return map(lambda a: int(a['duration']), annotations)

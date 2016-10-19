from annotation.models import Document, Label, AnnotationQueue, QueueElement
import annotation.classifier as clf

from random import sample
from operator import itemgetter

import logging

def uncertainty_sampling(documents, trueLabels):
    # the parameter documents should be straight forward. It's list of
    # documents to be sorted according to minimal margin sampling. The
    # parameter trueLabels is added for convenience as association between
    # documents and trueLabels usually is realised via the order in a
    # list.
    if clf.predict(documents[0]):
        # predict the scores for all documents
        pred_scores = map(clf.predict, documents)
        # for every document sort the scores of all trueLabels
        sorted_scores = map(lambda score:
                            sorted(map(lambda val: val['normalized'],
                                       score.values()), reverse=True),
                            pred_scores)
        # calculate the margin between the two most likely trueLabels
        pred_margin = map(lambda scores: scores[0]-scores[1], sorted_scores)
        # associate the margins with their respective documents and sort
        # them
        doc_margin = sorted(zip(documents, trueLabels, pred_margin,
                                map(lambda s: clf.predict_label(None, s),
                                    pred_scores)),
                            key=itemgetter(2))
        # write results to db
        for dm in doc_margin:
            document, trueLabel, margin, predLabel = dm
            doc = Document.objects.get(pk=document.pk)
            doc.active_prediction = predLabel
            logging.info('doc.active_prediction: '+str(doc.active_prediction))
            doc.margin = margin
            logging.info('doc.margin: '+str(doc.margin))
            doc.save()
        # unzip the margins from the documents and return the documents
        return zip(*doc_margin)[:2]
    else:
        return [documents, trueLabels]


def selectDocument(user, startSession=False):
    queue = AnnotationQueue.objects.filter(user=user).first()
    document = Document(document='YOU HAVE NO MORE DOCUMENTS LEFT TO ANNOTATE. THANK YOU FOR YOUR PARTICIPATION!',
                                doc_id='',
                                preprocessed='',
                                trainInstance=True)
    proposal = None

    if queue:
        elements = QueueElement.objects.filter(queue=queue).order_by('rank')
        if elements:
            if not startSession:
                elements.first().delete()
                #
            element = elements.first()
            document = element.document
            proposal = element.proposalFlag
        #
    return document, proposal

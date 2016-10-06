import annotation.classifier as clf

from operator import itemgetter

def uncertainty_sampling(documents, labels):
    if clf.predict(documents[0]):
        # predict the scores for all documents
        pred_scores = map(clf.predict, documents)
        # for every document sort the scores of all labels
        sorted_scores = map(lambda score:
                            sorted(map(lambda val: val['normalized'],
                                       score.values()), reverse=True),
                            pred_scores)
        # calculate the margin between the two most likely labels
        pred_margin = map(lambda scores: scores[0]-scores[1], sorted_scores)
        # associate the margins with their respective documents and sort
        # them
        doc_margin = sorted(zip(documents, labels, pred_margin),
                            key=itemgetter(2))
        print map(lambda t: (t[0].pk, t[1], t[2]), doc_margin)
        # unzip the margins from the documents and return the documents
        return zip(*doc_margin)[:-1]
    else:
        return [documents, labels]

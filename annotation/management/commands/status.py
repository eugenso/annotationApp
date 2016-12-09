# -*- coding: utf-8 -*-
from __future__ import division
from django.core.management.base import BaseCommand, CommandError
from annotation.models import Document, Annotation, Label, NBC_vocabulary, NBC_class_count
from operator import itemgetter, attrgetter
from itertools import groupby
from nltk import FreqDist

import numpy as np

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('maxAnno',
                            type=int,
                            help='The maximum number of annotations per document that was specified when calling <createAnnotaitonQueue>')
        return None

    def fleissKappa(self, matrix, n):
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


    def confusionMatrix(self):
        tp = [(true[0], pred[0]) for true, pred in
              filter(lambda t: True if t[0] and t[1] else False,
                     map(lambda a: (map(attrgetter('label'), a.labels.all()),
                                    map(attrgetter('label'), a.proposals.all())),
                         Annotation.objects.filter(proposalFlag='proposal')))]
        confM = dict((true, dict((pred, len(list(l)))
                                 for pred, l
                                 in groupby(sorted(v, key=itemgetter(1)), key=itemgetter(1))))
                     for true, v
                     in groupby(sorted(tp, key=itemgetter(0)), key=itemgetter(0)))
        labels = map(attrgetter('label'), Label.objects.all())
        leftCol = len(max(labels)) if len(max(labels)) > 17 else 17
        restCol = len(max(labels))+1
        print ''
        print ''.join('{:^{}}'.format(l, restCol)
                      for l in ['{:>{}}'.format('Confusion Matrix', leftCol)]+labels)
        for true in labels:
            line = []
            for pred in labels:
                t = confM.get(true)
                if t:
                    p = t.get(pred)
                    if p:
                        line.append(p)
                    else:
                        line.append(0)
                else:
                    line.append(0)
            print '{:>{}}'.format(true, leftCol) + ''.join('{:^{}}'.format(l, restCol) for l in line)


    def handle(self, *args, **options):
        annotations = Annotation.objects.all()
        documentCount = Document.objects.all().count()
        annotationCount = annotations.count()
        docCol = len(str(documentCount))
        annoCol = len(str(annotationCount))
        key = itemgetter(0)
        annoPerDoc = [(doc, list(annos)) for doc, annos
                      in groupby(sorted(map(lambda a: (a.document.pk, a),
                                            annotations), key=key),key=key)]
        labels = map(attrgetter('label'), Label.objects.all())
        labelWidth = len(max(labels))+1
        print ''
        print 'Documents:'
        print ' There are currently a total of {:{}} documents and {:{}} annotations'.format(
            documentCount, docCol, annotationCount, annoCol)
        for numOfAnnotations, documents in groupby(sorted(map(lambda (d, a):
                                                              len(a), annoPerDoc))):
            docCount = len(list(documents))
            print ' {:>{}} document{} with {:>{}} annotation{}'.format(
                docCount, docCol,
                ' ' if docCount == 1 else 's',
                numOfAnnotations, annoCol,
                ' ' if numOfAnnotations == 1 else 's')
        print ''
        print 'Annotators:'
        userAnno = map(lambda a: (a.user.username, a), annotations)
        userCol = len(max(map(key, userAnno)))
        for name, annotations in groupby(sorted(userAnno, key=key), key=key):
            print ' {:<{}} created {:>{}} annotations.'.format(
                name, userCol, len(list(annotations)), annoCol)
        #
        maxAnno = options['maxAnno'] # number of annotations per document
        labelsPerDocDist = filter(lambda fd: True if sum(fd.values())==maxAnno else False,
                                  map(lambda (k, v):
                                      FreqDist(map(lambda (d, a): a.labels.all()[0].label, v)),
                                      annoPerDoc))
        #
        print ''
        print 'Agreement:'
        annoAgreement = dict((k,len(list(v))) for k,v in groupby(sorted(map(len, labelsPerDocDist))))
        for numDiffLabel in range(1, maxAnno+1):
            numOfDocuments = annoAgreement.get(numDiffLabel, 0)
            print '{:>{}} documents are annotated with {:>{}} distinct label{}'.format(
                numOfDocuments, docCol, numDiffLabel, len(str(maxAnno)),
                ' ' if numDiffLabel == 1 else 's')
        #
        matrix = np.array([map(lambda l: fd[l] if fd.get(l) else 0, labels)
                           for fd in labelsPerDocDist])
        print ''
        print " Fleiss' Kappa: {}".format(self.fleissKappa(matrix, maxAnno))
        #
        print ''
        print 'Naive Bayes Model:'
        wordCount = NBC_vocabulary.objects.all().count()
        wordCol = len(str(wordCount))
        print ' The vocabulary consists of {:{}} words.'.format(wordCount, wordCol)
        for cc in NBC_class_count.objects.all():
            s = ' The label {:<{}} occured {:>{}} times with a total of {:>{}} words'
            print s.format(cc.label, labelWidth, cc.count, wordCol, cc.total_word_count, wordCol)
            #
        self.confusionMatrix()

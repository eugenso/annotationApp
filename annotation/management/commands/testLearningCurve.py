from django.core.management.base import BaseCommand, CommandError
from annotation.models import Document, Label
from sklearn.metrics import accuracy_score
from pprint import pprint

import annotation.classifier as clf
import annotation.document_selection as sel
import numpy as np
import re

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('trainFile',
                            type=str,
                            help='Path to file containing the training examples. It is assumed that each line contains an example.')
        parser.add_argument('testFile',
                            type=str,
                            help='Path to file containing the test examples. It is assumed that each line contains an example.')
        parser.add_argument('--split-abs',
                            nargs='*',
                            type=int,
                            help='Number of training examples for each learning step. Numbers have to add up to the number of training examples.')
        parser.add_argument('--active-learning',
                            dest='active',
                            action='store_true')
        parser.set_defaults(active=False)


    def readTSV(self, filename):
        with open(filename) as trainfile:
            train_content = trainfile.read().decode('utf-8')
            #
        # Extract the raw label representation from the total text.
        # raw_labels = ''.join(re.findall(r'\t[\d\-]+?\n',train_content)).replace('\t', '').splitlines()
        raw_labels = ''.join(re.findall(r'(\t[\-1]{1,2})*?\n',train_content)).split('\t')[1:]
        # Get the Labels from the db.
        relevant = Label.objects.filter(label='relevant').first()
        irrelevant = Label.objects.filter(label='irrelevant').first()
        # Tranform label representation into the true Labels.
        labels = [relevant if label=='1' else irrelevant
                  for label in raw_labels]
        doc_ids = ''.join(re.findall(r'\n.+?\t', train_content)).replace('\t', '').splitlines()
        document_texts = re.findall(r'\t.+?\t', train_content)
        documents = [Document(document=document_texts[idx],
                              doc_id=doc_ids[idx],
                              preprocessed=' '.join(clf.preprocessing(
                                  document_texts[idx])),
                              trainInstance=True)
                     for idx in range(len(document_texts))]
        return (documents, map(lambda l: [l], labels))


    def evaluate(self, testLabels):
        with open('results') as resultFile:
            results = eval(resultFile.read())
            #
        steps =map(lambda step:map(lambda score:[clf.predict_label(None, score)],
                                    step), # map over all scores
                    results) # map over all steps
        transform = lambda x: 1 if x[0].label == 'relevant' else 0
        true = map(transform, testLabels)
        return map(lambda step: accuracy_score(true, map(transform, step)),
                   steps)

    def processSteps(self,
                     trainDocuments, trainLabels,
                     testDocuments, testLabels,
                     split, active):
        trainDoc = trainDocuments
        trainLab = trainLabels
        results  = []
        exampleCtr = 0
        stepCtr = 0
        for step in split:
            stepCtr = stepCtr +1
            if active:
                [trainDoc,trainLab] = sel.uncertainty_sampling(trainDoc,trainLab)
                #
            # train all document for the current step
            for idx in range(step):
                exampleCtr = exampleCtr +1
                print 'Step ' + str(stepCtr) + ' Example ' +str(exampleCtr)
                clf.online_train(trainDoc[idx], trainLab[idx])
                trainDoc[idx].save()
                #
            # drop already trained examples
            trainDoc = trainDoc[step:]
            trainLab = trainLab[step:]
            # make predictions
            preds = [clf.predict(testDocuments[idx])
                     for idx in range(len(testDocuments))]
            results = results + [preds]
            #
        with open('results', 'wt') as resultFile:
            pprint(results, stream=resultFile)
            #
        print self.evaluate(testLabels)


    def handle(self, *args, **options):
        # Read train and test data from files
        (trainDocuments, trainLabels) = self.readTSV(options['trainFile'])
        (testDocuments, testLabels) = self.readTSV(options['testFile'])
        self.processSteps(trainDocuments, trainLabels,
                          testDocuments, testLabels,
                          options['split_abs'], options['active'])

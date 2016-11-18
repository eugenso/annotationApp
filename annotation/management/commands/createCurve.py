# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from sklearn.metrics import accuracy_score
from annotation.models import Document, Label
from django.conf import settings
import annotation.classifier as clf
import annotation.active_selection as sel

import random
import datetime
import csv
import json

import pdb

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('trainFile',
                            type=str,
                            help='Path to file containing the training examples. It is assumed that each line contains an example.')
        parser.add_argument('testFile',
                            type=str,
                            help='Path to file containing the test examples. It is assumed that each line contains an example.')
        parser.add_argument('labelMap',
                            type=str,
                            help='A file that maps label representation from the train/test data to the label representation in the database. One mapping per line "train label rep\tdatabase rep"')
        parser.add_argument('delimiter',
                            type=str,
                            help='Delimiter used in the .csv file')
        parser.add_argument('split',
                            nargs='*',
                            type=int,
                            help='Number of training examples for each learning step.')


    def readFile(self, filename, options):
        with open(filename) as csvfile:
            rows = list(csv.reader(csvfile, delimiter=options['delimiter']))
            #
        texts = map(lambda t: t[1], rows)
        labels = map(lambda t: t[2], rows)
        return texts, labels


    def objectTransformation(self, texts, classes, labelMap):
        documents = [Document(document=texts[i],
                              doc_id=i,
                              preprocessed=' '.join(clf.preprocessing(texts[i])),
                              trainInstance=True)
                     for i in range(len(texts))]
        if not set(classes)-set(labelMap.keys()):
            labels = map(lambda t: Label(label=labelMap[t],
                                         option='radio'), classes)
            return documents, labels
        else:
            print 'Labels found in '+filename+': '+str(set(classes))
            print 'Labels fount in label_mapping: '+str(set(labelMap.keys()))
            return None, None


    def evaluate(self, preds, testLabels):
        testL = map(lambda l: l.label, testLabels)
        labelSet = list(set(testL))
        labelMap = dict((labelSet[i],i) for i in range(len(labelSet)))
        #
        trueLabels = map(lambda l: labelMap[l.label], testLabels)
        predLabels = map(lambda p: labelMap[clf.predict_label(None, p).label], preds)
        #
        return accuracy_score(trueLabels, predLabels)


    def save(self, export, count, active):
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if active:
            mark = 'A'
        else:
            mark = 'R'
            #
        exportName = 'run_'+str(count)+'_'+mark+'_'+dt+'.json'
        jsonExport = json.dumps(export, indent=4)
        with open(settings.BASE_DIR+'/'+exportName, 'w') as exportFile:
            exportFile.write(jsonExport)


    def run(self, trainDocs, trainLabels, testDocs, testLabels, options, active=False):
        trainD = trainDocs
        trainL = trainLabels
        instanceCtr = 0
        stepCtr = 0
        export = {}
        for step in options['split']:
            stepCtr += 1
            if active:
                [trainD, trainL] = sel.uncertainty_sampling(trainD, trainL, saveScores=False)
                #
            for i in range(step):
                instanceCtr += 1
                print 'Step ' + str(stepCtr) + ' Example ' +str(instanceCtr)
                clf.online_train(trainD[i], [trainL[i]])
                #
            preds = map(lambda t: clf.predict(t, saveScores=False), testDocs)
            accuracy = self.evaluate(preds, testLabels)
            #
            export.update({stepCtr: {"step": step,
                                     "preds": preds,
                                     "accuracy": accuracy,
                                     "runOrder": map(lambda i: trainD[i].doc_id, range(step))}})
            # remove preciding training instances
            trainD = trainD[step:]
            trainL = trainL[step:]
            #
        # clear database from all data produced by the run (WARNING: also clears data not produced by the run)
        call_command('wipeDB', 'label')
        return export


    def handle(self, *args, **options):
        if options['delimiter'] == 't':
            options['delimiter'] = '\t'
        # read label mapping
        with open(options['labelMap']) as labelMapping:
            rawMapping = list(csv.reader(labelMapping, delimiter=options['delimiter']))
            #
        labelMap = {}
        for key, value in rawMapping:
            labelMap[key] = value
            #
        trainTexts, trainClasses = self.readFile(options['trainFile'], options)
        testTexts, testClasses = self.readFile(options['testFile'], options)
        trainDocs, trainLabels = self.objectTransformation(trainTexts, trainClasses, labelMap)
        testDocs, testLabels = self.objectTransformation(testTexts, testClasses, labelMap)

        runs = 10

        if trainDocs and trainLabels and testDocs and testLabels:
            trainSetSum = len(trainDocs)
            splitSum = sum(options['split'])
            if splitSum < trainSetSum:
                options['split'] += [trainSetSum-splitSum]
            if splitSum > trainSetSum:
                print 'split sum is greater then sum of training examples'
                return None
                #
            trainSet = zip(trainDocs, trainLabels)
            for i in range(runs):
                randTrainDocs, randTrainLabels = zip(*random.sample(trainSet, len(trainSet)))
                # random set order
                self.save(self.run(randTrainDocs,
                                   randTrainLabels,
                                   testDocs,
                                   testLabels,
                                   options, False), i, False)
                # selected order
                self.save(self.run(randTrainDocs,
                                   randTrainLabels,
                                   testDocs,
                                   testLabels,
                                   options, True), i, True)


# options = {}
# options['trainFile'] = 'data/sentiment_train.tsv'
# options['testFile'] = 'data/sentiment_test.tsv'
# options['delimiter'] = '\t'
# options['labelMap'] = 'data/sentiment_label_mapping.tsv'
# options['split'] = [2,2,2,2,10,10]
# filename='data/sentiment_train.tsv'

#self.run([trainDocs[0], trainDocs[1], trainDocs[31]], [trainLabels[0],trainLabels[1],trainLabels[32]], [testDocs[0], testDocs[13], testDocs[49]], [testLabels[0], testLabels[13], testLabels[49]], options)

from django.core.management.base import BaseCommand, CommandError
from annotation.models import Document, Label
from sklearn.metrics import confusion_matrix, accuracy_score
from pprint import pprint
import annotation.classifier as clf
import re

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('trainFile',
                            type=str,
                            help='Path to file containing the training examples. It is assumed that each line contains an example.')
        parser.add_argument('testFile',
                            type=str,
                            help='Path to file containing the test examples. It is assumed that each line contains an example.')
        parser.add_argument('split',
                            nargs='*',
                            type=float,
                            help='Fractions of training data used for each learning step. Fractions add up in occuring order and have to sum up to one. Example: The sequence 0.1 0.1 0.2 0.3 0.3 creates learning steps with 10, 20, 40, 70, and 100 percent of the training data.')
        # parser.add_argument('--split-abs',
        #                     nargs='*',
        #                     type=int,
        #                     help='')


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
        return (documents, labels)


    def evaluate(self, testLabels):
        with open('results') as resultFile:
            results = eval(resultFile.read())
            #
        steps = map(lambda step:map(lambda score: clf.predict_label(None, score),
                                    step), # map over all scores
                    results) # map over all steps
        transform = lambda x: 1 if x.label == 'relevant' else 0
        true = map(transform, testLabels)
        return map(lambda step: accuracy_score(true, map(transform, step)),
                   steps)

    def handle(self, *args, **options):
        if sum(options['split']) == 1:
            # Read train and test data from files
            (trainDocuments, trainLabels) = self.readTSV(options['trainFile'])
            (testDocuments, testLabels) = self.readTSV(options['testFile'])
            # Divide the training data into learning steps. For N=3300
            # the number of training examples and
            # options['split']=[0.1, 0.1, 0.2, 0.3, 0.3] the resulting
            # stepCount should be [0, 330, 660, 1320, 2310, 3300]
            N = len(trainDocuments)
            stepCount = reduce(lambda seq, step:
                               seq+[int(round(N*step))+seq[-1]],
                               options['split'], [0])[:-1]+[N]
            # Go over every step pair and every example in the step
            # and train the classifier. After every step classify all
            # test examples and calculate their accuracy, precision,
            # etc.
            results = []
            # create the steps
            for (fromStep, toStep) in zip(stepCount[:-1], stepCount[1:]):
                # step over and train
                for idx in range(fromStep, toStep):
                    print str(idx) + ' ' + str((fromStep, toStep))
                    clf.online_train(trainDocuments[idx], [trainLabels[idx]])
                    trainDocuments[idx].save()
                # make predictions and convert to binary vector
                # preds = [1 if clf.predict_label(testDocuments[idx]) == Label(label='relevant') else 0
                #          for idx in range(len(testDocuments))]
                preds = [clf.predict(testDocuments[idx])
                         for idx in range(len(testDocuments))]
                # convert true labels to binary vector and add results
                # to list.
                # true = map(lambda p: 1 if p == Label(label='relevant') else 0, testLabels)
                results = results + [preds]
            with open('results', 'wt') as resultFile:
                pprint(results, stream=resultFile)
            self.evaluate(testLabels)
        else:
            raise Exception('Split arguments have to sum up to 1.')

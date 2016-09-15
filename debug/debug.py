from annotation.models import Document, Label, Annotation
from annotation.models import NBC_class_count, NBC_vocabulary, NBC_word_count_given_class

from django.utils.encoding import python_2_unicode_compatible

import annotation.classifier as clf

from sklearn.metrics import confusion_matrix, accuracy_score
import re



def readTSV(filename):
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

trainFile = 'train.tsv'
testFile = 'test.tsv'

(trainDocuments, trainLabels) = readTSV(trainFile)
(testDocuments, testLabels) = readTSV(testFile)

split = [0.1,0.1,0.2,0.3,0.3]
N = len(trainDocuments)
stepCount = reduce(lambda seq, step:
                   seq+[int(round(N*step))+seq[-1]],
                   split, [0])[:-1]+[N]
rlt = []
rlta = []
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
    pprint(preds)
    # convert true labels to binary vector and add results
    # to list.
    true = map(lambda p: 1 if p == Label(label='relevant') else 0, testLabels)
    rlt = rlt + [confusion_matrix(true, preds)]
    rlta = rlta + [accuracy_score(true, preds)]
print rlt
print rlta


(testDocuments, testLabels) = Command.readTSV(Command(), 'relevance-test.tsv')
rlt = Command.evaluate(Command(), testLabels)

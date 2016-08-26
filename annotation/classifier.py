from __future__ import division

from annotation.models import Document, Label
from annotation.models import NBC_class_count, NBC_word_count_given_class, NBC_vocabulary
from django.db.models import F, FloatField, Sum, IntegerField

from nltk import word_tokenize
from math import log
from operator import itemgetter
import re
import sys

def update_class_count(labels):
    # This function updates the counts for the class prior. If there
    # are existing class count objects, their counts are being
    # updated. Otherwise the objects are initialized with 0.
    if not NBC_class_count.objects.all():
        [NBC_class_count(label=label, count=0).save()
         for label in Label.objects.all()]
    for label in labels:
        for cc in NBC_class_count.objects.filter(label=label):
            cc.count = cc.count +1
            cc.save()


def update_word_count(tokens, labels):
    # To compute the conditional probability of a term given the class
    # this function counts how often each term occurs in each class of
    # the training document.
    for token in tokens:
        for label in labels:
            vocab = NBC_vocabulary.objects.filter(word=token).first()
            if vocab:
                wcgc = NBC_word_count_given_class.objects.filter(
                    word=vocab, label=label).first()
                if wcgc:
                    wcgc.count = wcgc.count +1
                    wcgc.save()
                else:
                    NBC_word_count_given_class(
                        label=label, word=vocab, count=1).save()
            else:
                vocab = NBC_vocabulary(word=token)
                vocab.save()
                NBC_word_count_given_class(
                    label=label, word=vocab, count=1).save()


def relative_term_freq(token, label):
    # Conditional probability P(term|class)
    vocabulary = NBC_vocabulary.objects.all()
    vocab = NBC_vocabulary.objects.filter(word=token).first()
    if vocab:
        wcgc = NBC_word_count_given_class.objects.filter(
            word=vocab, label=label).first()
        if wcgc:
            Tct = wcgc.count
        else:
            Tct = 0
    else:
        Tct = 0
        # All words that are present in the class
    present_words = NBC_word_count_given_class.objects.filter(label=label)
    if present_words:
        # Number of remaining words that are not present in the class but
        # in the vocabulary.
        remaining = vocabulary.count() - present_words.count()
        Tct_sum = remaining + present_words.aggregate(
            sum=Sum(F('count')+1, output_field=IntegerField()))['sum']
    else:
        Tct_sum = vocabulary.count()
    return (Tct + 1) / Tct_sum


def preprocessing(raw_document):
    urls = r'(http.+?(\s|$))'
    specialchar =  r'|[^A-Za-z\s]'
    doc = raw_document.lower()
    tokens = word_tokenize(re.sub(urls+specialchar, '', doc))
    return tokens


def online_train(document, labels):
    update_class_count(labels)
    tokens = preprocessing(document.document)
    update_word_count(tokens, labels)


def predict(document):
    tokens = preprocessing(document)
    scores = {}
    N = Document.objects.count()
    for c in NBC_class_count.objects.all():
        label = c.label.__str__()
        scores[label] = {}
        if c.count:
            prior = log(c.count/N)
        else:
            prior = -sys.maxint -1
            #
        scores[label]['prior'] = prior
        scores[label]['term_given_label'] = 0
        for token in tokens:
            scores[label]['term_given_label'] += log(
                relative_term_freq(token, c.label))
            scores[label]['total'] = scores[label]['prior']+scores[label]['term_given_label']
    return scores


def predict_label(document, scores={}):
    if scores:
        scores = map(lambda l: (l[0], l[1]['total']), scores.items())
    else:
        scores = map(lambda l: (l[0], l[1]['total']),
                     predict(document).items())
    if scores:
        predicted_label = Label.objects.filter(
            label=max(scores,key=itemgetter(1))[0]).first()
    else:
        predicted_label = None
    return predicted_label

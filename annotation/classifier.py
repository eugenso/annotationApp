from __future__ import division

from annotation.models import Document, Label
from annotation.models import NBC_class_count, NBC_word_count_given_class, NBC_vocabulary
from django.db.models import F, FloatField, Sum, IntegerField

from nltk import word_tokenize
from math import log, exp
from operator import itemgetter
from pprint import pprint
import numpy as np
import re
import sys

def update_class_count(labels):
    # This function updates the counts for the class prior. If there
    # are existing class count objects, their counts are being
    # updated. Otherwise the objects are initialized with 0.
    if not NBC_class_count.objects.all():
        [NBC_class_count(label=label, count=0, total_word_count=0).save()
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
            cc = NBC_class_count.objects.filter(label=label).first()
            cc.total_word_count = cc.total_word_count +1
            cc.save()


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
        #
    Tct_sum = NBC_class_count.objects.filter(
        label=label).first().total_word_count + vocabulary.count()
    return (Tct + 1) / Tct_sum


def preprocessing(raw_document):
    urls = r'(http.+?(\s|$))'
    specialchar =  r'|[^A-Za-z\s]'
    doc = raw_document.lower()
    tokens = word_tokenize(re.sub(urls+specialchar, ' ', doc))
    return tokens


def online_train(document, labels):
    update_class_count(labels)
    update_word_count(document.preprocessed.split(' '), labels)


def predict(document):
    # To predict the label of a document first get the preprocessed
    # version.
    tokens = document.preprocessed.split(' ')
    scores = {} # holds the end result
    # Sum over the field 'count' in the table NBC_class_count to know
    # how many documents there are in total.
    N = NBC_class_count.objects.aggregate(Sum('count'))['count__sum']
    # The calculation for each label can be done independently
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
            #
        scores[label]['total'] = scores[label]['prior']+scores[label]['term_given_label']
        #scores[label]['total'] = scores[label]['term_given_label']
        scores[label]['prior'] = exp(scores[label]['prior'])
        #scores[label]['term_given_label'] = exp(scores[label]['term_given_label'])
        scores[label]['total'] = exp(scores[label]['total'])
        #
    # ask eugen again
    for c in NBC_class_count.objects.all():
        label = c.label.__str__()
        scores[label]['normalized'] = np.power(scores[label]['total'], 1/(len(tokens)+1))
    # normalize
    total_sum = 0
    for c in NBC_class_count.objects.all():
        label = c.label.__str__()
        total_sum += scores[label]['normalized']
    for c in NBC_class_count.objects.all():
        label = c.label.__str__()
        if scores[label]['normalized'] != 0:
            scores[label]['normalized'] = scores[label]['normalized'] / total_sum
        else:
            scores[label]['normalized'] = 0.0
    return scores


def predict_label(document, scores={}):
    # This function adds a little abstraction for convenience but more
    # importantly it decides which label is picked based on the
    # probabilities for each label.
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



    # predict the labels for all scores
    # pred_label = map(lambda score: predict_label(None, score), pred_scores)
    # go over all pred_scores and select the normalized score for the
    # predicted label.
    # pred_norm = map(lambda idx:
    #                 pred_scores[idx][pred_label[idx].label]['normalized'],
    #                 range(len(documents)))

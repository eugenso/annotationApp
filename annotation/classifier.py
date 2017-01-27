# -*- coding: utf-8 -*-
from __future__ import division

from annotation.models import Document, Label, Score
from annotation.models import NBC_class_count, NBC_word_count_given_class, NBC_vocabulary
from django.db.models import F, FloatField, Sum, IntegerField

from nltk import word_tokenize
from math import log, exp
from operator import itemgetter, attrgetter
from itertools import groupby
from pprint import pprint
import numpy as np
import re
import sys

import pdb

def update_class_count(labels):
    # This function updates the counts for the class prior. If there
    # are existing class count objects, their counts are being
    # updated. Otherwise the objects are initialized with 0.
    for label in map(lambda l: l.label, labels):
        cc, created = NBC_class_count.objects.get_or_create(label=label)
        if not created:
            cc.count = cc.count +1
            cc.save()


def update_word_count(tokens, labelObjs):
    # To compute the conditional probability of a term given the class
    # this function counts how often each term occurs in each class of
    # the training document.
    labels = map(lambda l: l.label, labelObjs)
    for token in tokens:
        for label in labels:
            try:
                vocab, created_vocab = NBC_vocabulary.objects.get_or_create(word=token)
            except:
                duplicates = NBC_vocabulary.objects.filter(word=token)
                duplicates.delete()
                wcgc = NBC_vocabulary(word=token)
                wcgc.save()
            try:
                wcgc, created_wcgc = NBC_word_count_given_class.objects.get_or_create(
                    word=token, label=label)
            except:
                duplicates = NBC_word_count_given_class.objects.filter(word=token, label=label)
                count = sum(map(attrgetter('count'), duplicates))
                duplicates.delete()
                wcgc = NBC_word_count_given_class(word=token, label=label)
                wcgc.count = count
                wcgc.save()
                #
            if not created_wcgc:
                wcgc.count = wcgc.count +1
                wcgc.save()
                #
    ccs = list(NBC_class_count.objects.filter(label__in=labels))
    for cc in ccs:
        cc.total_word_count = cc.total_word_count + len(tokens)
        cc.save()


# def relative_term_freq(token, label):
#     # Conditional probability P(term|class)
#     vocab = NBC_vocabulary.objects.filter(word=token).first()
#     if vocab:
#         wcgc = NBC_word_count_given_class.objects.filter(
#             word=vocab, label=label).first()
#         if wcgc:
#             Tct = wcgc.count
#         else:
#             Tct = 0
#     else:
#         Tct = 0
#         #
#     Tct_sum = NBC_class_count.objects.filter(
#         label=label).first().total_word_count + NBC_vocabulary.objects.all().count()
#     return (Tct + 1) / Tct_sum


def preprocessing(raw_document):
    urls = r'(http.+?(\s|$))'
    specialchar =  r'|[^A-Za-z\s]'
    doc = raw_document.lower()
    tokens = word_tokenize(re.sub(urls+specialchar, ' ', doc))
    return tokens


def online_train(document, labels):
    update_class_count(labels)
    update_word_count(document.preprocessed.split(' '), labels)


def predict(document, saveScores=True):
    # To predict the label of a document first get the preprocessed
    # version.
    tokens = document.preprocessed.split(' ')
    scores = {} # holds the end result
    vocabulary_count = NBC_vocabulary.objects.all().count()
    # The calculation for each label can be done independently
    ccs = list(NBC_class_count.objects.all())
    labels = map(attrgetter('label'), ccs)
    #
    wcgcObjs = list(NBC_word_count_given_class.objects.filter(word__in=tokens,
                                                              label__in=labels))
    # This is a dict where each key is a label and each value is a
    # dict itself, where the keys are words and the values are the
    # counts of how often the word occured given the label.
    wcgcs = dict((label, dict((word, map(attrgetter('count'), w)[0])
                              for word, w in groupby(sorted(v, key=attrgetter('word')),
                                                     key=attrgetter('word'))))
                 for label, v in groupby(sorted(wcgcObjs, key=attrgetter('label')),
                                         key=attrgetter('label')))
    # Sum over the field 'count' in the table NBC_class_count to know
    # how many documents there are in total.
    N = sum(map(attrgetter('count'), ccs))
    for c in ccs:
        label = c.label
        scores[label] = {}
        if c.count:
            prior = log(c.count/N)
        else:
            prior = -sys.maxint -1
            #
        scores[label]['prior'] = prior
        scores[label]['term_given_label'] = 0
        Tct_tmp = wcgcs.get(label, 0)
        Tct_sum = c.total_word_count + vocabulary_count
        for token in tokens:
            if Tct_tmp:
                Tct = Tct_tmp.get(token, 0)
                    #
            relative_term_freq = (Tct + 1) / Tct_sum
            scores[label]['term_given_label'] += log(relative_term_freq)
            #
        scores[label]['total'] = scores[label]['prior']+scores[label]['term_given_label']
        #scores[label]['total'] = scores[label]['term_given_label']
        scores[label]['prior'] = exp(scores[label]['prior'])
        #scores[label]['term_given_label'] = exp(scores[label]['term_given_label'])
        scores[label]['total'] = exp(scores[label]['total'])
        #
    # ask eugen again
    for c in ccs:
        label = c.label
        scores[label]['normalized'] = np.power(scores[label]['total'], 1/(len(tokens)+1))
    # normalize
    total_sum = 0
    for c in ccs:
        label = c.label
        total_sum += scores[label]['normalized']
    for c in ccs:
        label = c.label
        if scores[label]['normalized'] != 0:
            scores[label]['normalized'] = scores[label]['normalized'] / total_sum
        else:
            scores[label]['normalized'] = 0.0
        # save scores to db
        # if saveScores:
        #     dbScore, created = Score.objects.get_or_create(document=document,
        #                                                    label=Label.objects.filter(label=c.label).first())
        #     dbScore.nbc_normalized = scores[label]['normalized']
        #     dbScore.nbc_prior = scores[label]['prior']
        #     dbScore.nbc_term_given_label = scores[label]['term_given_label']
        #     dbScore.nbc_total = scores[label]['total']
        #     dbScore.save()
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

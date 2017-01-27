# -*- coding: utf-8 -*-
from __future__ import division
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from annotation.management.commands.predictLabel import Command as pL
from operator import attrgetter
from sklearn.metrics import classification_report


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('testfile',
                            type=str,
                            help='Filename of the test file. The test file is assumed to be a csv file with the document id in the first column and the document text in the second column')
        parser.add_argument('delimiter',
                            type=str,
                            help='Delimiter used in the .csv file')

    def handle(self, *args, **options):
        # Management commands are surposed to not return anything or
        # at least only string which are printed in the to stdout. If
        # we want to reuse functionality from the <predictLabel>
        # function and not print the labels to stdout we have to do
        # this.
        doc_ids, texts, preds, trues = pL.predict_labels(pL(), options)
        keys = list(set(map(attrgetter('label'), preds)+list(trues)))
        labelMap = dict((keys[i], i) for i in range(len(keys)))
        print classification_report(map(lambda t: labelMap[t], trues),
                                    map(lambda p: labelMap[p], map(attrgetter('label'), preds)),
                                    target_names=keys,
                                    labels=map(lambda k: labelMap[k], keys))
        return None

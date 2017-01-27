# -*- coding: utf-8 -*-
from __future__ import division
from django.core.management.base import BaseCommand, CommandError
from annotation.models import Document

import annotation.classifier as clf
import csv
import os

import pdb
class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('testfile',
                            type=str,
                            help='Filename of the test file. The test file is assumed to be a csv file with the document id in the first column and the document text in the second column')
        parser.add_argument('delimiter',
                            type=str,
                            help='Delimiter used in the .csv file')
        parser.add_argument('--save',
                            dest='save',
                            action='store_true',
                            help='Save labels to file')
        parser.set_defaults(save=False)

    def predict_labels(self, options):
        if options['delimiter'] == 't':
            options['delimiter'] = '\t'
            #
        # read test instances from file
        with open(options['testfile']) as csvfile:
            rows = list(csv.reader(csvfile, delimiter=options['delimiter']))
            #
        if len(rows[0]) == 2:
            doc_ids, texts = zip(*rows)
            trueLabels = []
        else:
            doc_ids, texts, trueLabels = zip(*rows)
            #
        # convert the file content to Document objects
        documents = map(lambda (doc_id, text):
                        Document(document=text,
                                 doc_id=doc_id,
                                 preprocessed=' '.join(clf.preprocessing(text)),
                                 trainInstance=True), zip(doc_ids, texts))
        # predict labels
        return doc_ids, texts, map(clf.predict_label, documents), trueLabels

    def handle(self, *args, **options):
        # write them to a file
        if options['save']:
            nameParts = os.path.splitext(options['testfile'])
            with open(nameParts[0]+'_labeled'+nameParts[1], 'wb') as csvfile:
                writer = csv.writer(csvfile,
                                    delimiter=options['delimiter'])
                map(lambda (doc_id, text, pred):
                    writer.writerow([doc_id, text, pred]),
                    zip(*(self.predict_labels(options)[:3])))
        return None

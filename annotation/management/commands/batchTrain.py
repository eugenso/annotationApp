# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

import annotation.classifier as clf
import re
from annotation.models import Document, Label

import pdb, traceback, sys

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename',
                            type=str,
                            help='Path to file containing the training examples.')
        parser.add_argument('maxTokenCount',
                            type=str,
                            help='The maximum number of tokens per document (white space tokenization). Additional tokens are being cut off and not saved in the database. Type <all> to use the entire document.')

    def handle(self, *args, **options):
        with open(options['filename']) as trainfile:
            train_content = trainfile.read()
            #
        raw_labels = ''.join(re.findall(r'\t[\d\-]+?\n',train_content)).replace(
            '\t', '').splitlines()
        relevant = Label.objects.filter(label='Pos').first()
        irrelevant = Label.objects.filter(label='Neg').first()
        labels = [relevant if label=='1' else irrelevant
                  for label in raw_labels]
        doc_ids = ''.join(re.findall(r'\n.+?\t',
                                     train_content)).replace(
                                         '\t', '').splitlines()
        document_texts = re.findall(r'\t.+?\t', train_content)
        if options['maxTokenCount'] == 'all':
            maxTokenCount = len(fullTokens)
        else:
            maxTokenCount = int(options['maxTokenCount'])
        document_texts = map(lambda d: ' '.join(d.decode('utf-8').encode('utf-8').split(' ')[:maxTokenCount]), document_texts)
        documents = [Document(document=document_texts[idx],
                              doc_id=doc_ids[idx],
                              preprocessed=' '.join(clf.preprocessing(
                                  document_texts[idx])),
                              trainInstance=True)
                     for idx in range(len(document_texts))]
        #
        for document in documents:
            document.save()
            #
        for idx in range(len(documents)):
            clf.online_train(documents[idx], [labels[idx]])

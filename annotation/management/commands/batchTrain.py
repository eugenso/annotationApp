# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

import annotation.classifier as clf
import re
from annotation.models import Document, Label

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename',
                            type=str,
                            help='Path to file containing the training examples.')

    def handle(self, *args, **options):
        with open(options['filename']) as trainfile:
            train_content = trainfile.read()
            #
        raw_labels = ''.join(re.findall(r'\t[\d\-]+?\n',train_content)).replace(
            '\t', '').splitlines()
        relevant = Label.objects.filter(label='relevant').first()
        irrelevant = Label.objects.filter(label='irrelevant').first()
        labels = [relevant if label=='1' else irrelevant
                  for label in raw_labels]
        doc_ids = ''.join(re.findall(r'\n.+?\t',
                                     train_content)).replace(
                                         '\t', '').splitlines()
        document_texts = re.findall(r'\t.+?\t', train_content)
        documents = [Document(document=document_texts[idx],
                              doc_id=doc_ids[idx],
                              preprocessed=' '.join(clf.preprocessing(
                                  document_texts[idx])),
                              trainInstance=True)
                     for idx in range(len(document_texts))]
        [(clf.online_train(documents[idx], [labels[idx]]), documents[idx].save())
         for idx in range(len(documents))]

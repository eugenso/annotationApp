# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from annotation.models import Document
import annotation.classifier as clf
import codecs
import csv
import sys
import os

#import pdb

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('source',
                            type=str,
                            help='The path to either a .csv file or a directory of .csv files containing the document ids in the first column and the documents in the second column. Note that if <source> is a directory all files inside this directory are tried to process. This is to not be restricted to a file extension.')
        parser.add_argument('delimiter',
                            type=str,
                            help='Delimiter used in the .csv file')
        parser.add_argument('maxTokenCount',
                            type=str,
                            help='The maximum number of tokens per document (white space tokenization). Additional tokens are being cut off and not saved in the database. Type <all> to use the entire document.')
        parser.add_argument('--train-instance',
                            dest='train',
                            action='store_true')
        parser.set_defaults(active=False)
        #

    def processFile(self,filename, options):
        print 'Add documents from ' + filename
        with open(filename) as csvfile:
            rows = csv.reader(csvfile, delimiter=options['delimiter'])
            count = 1
            for row in rows:
                if row:
                    print count
                    count += 1
                    iD   = row[0].decode('utf-8').encode('utf-8')
                    fullTokens = row[1].decode('utf-8').encode('utf-8').split(' ')
                    if options['maxTokenCount'] == 'all':
                        maxTokenCount = len(fullTokens)
                    else:
                        maxTokenCount = int(options['maxTokenCount'])
                    text = ' '.join(fullTokens[:maxTokenCount])
                    trainInstance = False
                    if options['train']:
                        trainInstance = True
                        #
                    document = Document(document=text,
                                        doc_id=iD,
                                        preprocessed=' '.join(clf.preprocessing(text)),
                                        trainInstance=trainInstance)
                    document.save()

    def handle(self, *args, **options):
        if options['delimiter'] == 't':
            options['delimiter'] = '\t'
            #
        if os.path.isdir(options['source']):
            for file in os.listdir(options['source']):
                self.processFile(os.path.join(options['source'], file), options)
        elif os.path.isfile(options['source']):
            self.processFile(options['source'], options)
        else:
            raise IOError(options['source'] + ' is neither a file nor a directory.')
        print "Don't forget to call <createAnnotationQueue> before you start to annotate."

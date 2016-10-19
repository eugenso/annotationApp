from django.core.management.base import BaseCommand, CommandError
from annotation.models import Document
import annotation.classifier as clf
import codecs
import csv

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename',
                            type=str,
                            help='Path to .csv file containing the document ids in the first column and the documents in the second column.')
        parser.add_argument('delimiter',
                            type=str,
                            help='Delimiter used in the .csv file')
        #
    def handle(self, *args, **options):
        with open(options['filename']) as csvfile:
            if options['delimiter']:
                options['delimiter'] = '\t'
            rows = csv.reader(csvfile, delimiter=options['delimiter'])
            count = 1
            for row in rows:
                if row:
                    print count
                    count += 1
                    iD   = row[0].decode('utf-8')
                    text = row[1].decode('utf-8')
                    document = Document(document=text,
                                        doc_id=iD,
                                        preprocessed=' '.join(clf.preprocessing(text)),
                                        trainInstance=False)
                    document.save()

from django.core.management.base import BaseCommand, CommandError
from annotation.models import Document
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
            rows = csv.reader(csvfile, delimiter=options['delimiter'])
            for row in rows:
                document = Document(document=unicode(row[1].decode('utf-8')),
                                    doc_id=unicode(row[0].decode('utf-8')),
                                    trainInstance=False)
                document.save()

# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from annotation.models import Label

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename',
                            type=str,
                            help='Path to file containing a label per line.')
        #
    def handle(self, *args, **options):
        with open(options['filename']) as labelfile:
            for row in labelfile:
                c = unicode(row.replace('\n', '').decode('utf-8')).split('@')
                label = Label(label=c[0], option=c[1])
                label.save()

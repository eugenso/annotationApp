# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from annotation.models import Document, Label, Annotation
from annotation.models import NBC_class_count, NBC_vocabulary, NBC_word_count_given_class
from annotation.models import AnnotationQueue, QueueElement, Score

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('exclude', nargs='*', type=str,
                            help='Tables to exclude from deleting')

    def handle(self, *args, **options):
        excludes = map(lambda e: e.lower(), options['exclude'])
        models = [Document,
                  Label,
                  Annotation,
                  NBC_class_count,
                  NBC_vocabulary,
                  NBC_word_count_given_class,
                  AnnotationQueue,
                  QueueElement,
                  Score]
        for dbO in models:
            if not dbO.__name__.lower() in excludes:
                dbO.objects.all().delete()

        # if not 'document' in excludes:
        #     Document.objects.all().delete()
        # if not 'label' in excludes:
        #     Label.objects.all().delete()
        # if not 'annotation' in excludes:
        #     Annotation.objects.all().delete()
        # if not 'nbc_class_count' in excludes:
        #     NBC_class_count.objects.all().delete()
        # if not 'nbc_vocabulary' in excludes:
        #     NBC_vocabulary.objects.all().delete()
        # if not 'nbc_word_count_given_class' in excludes:
        #     NBC_word_count_given_class.objects.all().delete()

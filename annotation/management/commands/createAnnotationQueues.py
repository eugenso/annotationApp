from django.core.management.base import BaseCommand, CommandError

from annotation.models import Document, Annotation, AnnotationQueue
from django.contrib.auth.models import User, Group
from itertools import chain, repeat
from random import shuffle

import warnings

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('maxAnno',
                            type=int,
                            help='The maximum number of annotations per document. Documents that have at least one annotation but not the maximum number of annotations are being prefered over documents with no annotation.')
        parser.add_argument('proposals',
                            type=str,
                            help='Each document is annotated multiple times (maxAnno). <proposals> defines for how many of these annotations the annotator is presented the proposal label from the classifier. This parameter should be smaller than <maxAnno>.')


    def handle(self, *args, **options):
        annotators = list(Group.objects.get(name='Annotators').user_set.all())
        if options['maxAnno'] > len(annotators):
            maxAnno_too_big = 'The parameter <maxAnno> is bigger than the total number of annotators.'
            warnings.warn(maxAnno_too_big, Warning)
        if not options['maxAnno'] > options['proposals']:
            proposals_too_big = 'The parameter <proposals> is bigger than <maxAnno>.'
            warnings.warn(proposals_too_big, Warning)
        #
        # filter all documents for non training documents and then
        # exclude all documents that already have an annotation.
        empty_doc = Document.objects.filter(trainInstance=False).exclude(
        id__in=map(lambda a: a.document.pk, Annotation.objects.all()))
        # repeat each document <maxAnno> times and store them in one
        # list.
        doc_queue = list(chain.from_iterable(repeat(x, options['maxAnno'])
                                             for x in empty_doc))
        # create a list of lists that only contain False. Each inner
        # list contains <maxAnno> - <proposals> elements.
        a_lot_of_false = repeat(list(repeat(False,
                                            options['maxAnno']-options['proposals'])),
                                len(empty_doc))
        # complement the inner lists with <proposals> Trues.
        neat_true_false = map(lambda x: x+list(repeat(True, options['proposals'])),
                              a_lot_of_false)
        # randomize the order of the inner lists and flatten the
        # entire list. This list might have more elements than
        # doc_queue but zipping them together ignores the additional
        # elements.
        proposals = list(chain(*map(lambda x: sample(x, len(x)), neat_true_false)))
        #
        queueElements = zip(doc_queue, proposals)
        #
        for annotator in annotators:
            queue = AnnotationQueue(user=annotator)
            userIdx = annotators.index(annotator)
            for dp in queue[userIdx::len(annotators)]:

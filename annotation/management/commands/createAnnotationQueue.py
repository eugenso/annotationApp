# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from annotation.models import Document, Annotation, AnnotationQueue, QueueElement
from django.contrib.auth.models import User, Group
from itertools import chain, repeat, groupby
from operator import itemgetter
from random import sample, shuffle

import warnings
import annotation.active_selection as sel
import numpy as np
import logging
import datetime

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('maxAnno',
                            type=int,
                            help='The maximum number of annotations per document. Documents that have at least one annotation but not the maximum number of annotations are being prefered over documents with no annotation.')
        parser.add_argument('no-proposal-num',
                            type=int,
                            help='Number of annotations per document that get no proposal.')
        parser.add_argument('wrong-proposal-num',
                            type=int,
                            help='Number of annotations per document that get a wrong proposal.')
        parser.add_argument('no-proposal-freq',
                            nargs='*',
                            type=float,
                            help='This options expects 3 parameters which represent the frequency of documents that get no proposal, a wrong proposal and full proposal. With the sequence 0.2 0.3 0.5; documents have a 20%% chance to get no annotation proposal where <no-proposal-num> of the annotations have no proposal, a 30%% chance to get a wrong annotation proposal where <wrong-proposal-num> of the annotations get a wrong proposal and a 50%% chance to get all proposals. The three numbers have to sum up to one.')

    def active_document_queue(self, documents):
        return sel.uncertainty_sampling(documents, range(len(documents)))

    def createQueueElements(self, documents, maxAnno, options, usersAlreadyAnno=None):
        if not maxAnno >= options['no-proposal-num']:
            proposals_too_big = 'The parameter <no-proposal-num> is bigger than the maximum number of annotations set per document.'
            warnings.warn(proposals_too_big, Warning)
        if not maxAnno >= options['wrong-proposal-num']:
            proposals_too_big = 'The parameter <wrong-proposal-num> is bigger than the maximum number of annotations set per document.'
            warnings.warn(proposals_too_big, Warning)
        frequences = list(np.random.choice(['no proposal', 'wrong proposal', 'proposal'],
                                           len(documents),
                                           options['no-proposal-freq']))
        proposals = []
        wrong = ['wrong proposal']*options['wrong-proposal-num']
        wrong += ['proposal']*(maxAnno-options['wrong-proposal-num'])
        no = ['no proposal']*options['no-proposal-num']
        no += ['proposal']*(maxAnno-options['no-proposal-num'])
        for freq in frequences:
            if freq == 'proposal':
                proposals += ['proposal']*maxAnno
            elif freq == 'wrong proposal':
                proposals += sample(wrong, len(wrong))
            elif freq == 'no proposal':
                proposals += sample(no, len(no))
                #
            #
        if usersAlreadyAnno:
            doc_user_queue = list(chain.from_iterable(repeat(x, maxAnno)
                                                      for x in zip(documents, usersAlreadyAnno)))
            doc_queue, users = zip(*doc_user_queue)
            rlt = zip(doc_queue, proposals, users)
        else:
            doc_queue = list(chain.from_iterable(repeat(x, maxAnno)
                                                      for x in documents))
            rlt = zip(doc_queue, proposals)
        return rlt


    def handle(self, *args, **options):
        if sum(options['no-proposal-freq']) != 1 or len(options['no-proposal-freq']) != 3:
            raise Exception('<no-proposal-freq> have to sum up to one and be exactly 3 parameters.')
        if not options['maxAnno'] > options['no-proposal-num']:
            print "options['maxAnno']: " + options['maxAnno']
            print "options['no-proposal-num']: " + options['no-proposal-num']
            proposals_too_big = 'The parameter <no-proposal-num> is bigger than <maxAnno>.'
            warnings.warn(proposals_too_big, Warning)
        if not options['maxAnno'] > options['wrong-proposal-num']:
            proposals_too_big = 'The parameter <wrong-proposal-num> is bigger than <maxAnno>.'
            warnings.warn(proposals_too_big, Warning)
        #
        annotators = list(Group.objects.get(name='Annotators').user_set.all())
        if options['maxAnno'] > len(annotators):
            maxAnno_too_big = 'The parameter <maxAnno> is bigger than the total number of annotators.'
            warnings.warn(maxAnno_too_big, Warning)
        #
        annotations = Annotation.objects.all()

        startTime = datetime.datetime.now()
        print 'Started at ' + startTime.strftime("%Y-%m-%d %H:%M")
        if not annotations:
            documents, trash = self.active_document_queue(Document.objects.all())

            queueElements = self.createQueueElements(documents,
                                                     options['maxAnno'],
                                                     options)

            rank = 0
            for annotator in annotators:
                print 'Create queue for user ' + annotator.__str__()
                queue = AnnotationQueue(user=annotator,
                                        max_anno_num=options['maxAnno'])
                queue.save()
                userIdx = annotators.index(annotator)
                for document, proposal in queueElements[userIdx::len(annotators)]:
                    rank += 1
                    print 'Element ' + str(rank) + ': ' + str(document.pk) + ' ' + proposal
                    qE = QueueElement(document=document,
                                      queue=queue,
                                      proposalFlag=proposal,
                                      rank=rank)
                    qE.save()
        elif annotations:
            # This case is is divided into two stages. The first
            # processes documents that already have some annotations
            # but not the required number of options['maxAnno']. The
            # second stage processes documents without any annotation.

            print "Create annotation queue entries for partially annotated documents"
            # Instead of useing the document objects, map them to their
            # primary key to sort them. Their actual ordering does not
            # matter. It only matters that documents with the same pk
            # are consecutive such that groupby puts them in the same
            # group.
            annoDocuments = map(lambda a: a.document.pk, annotations)
            unfinnishedDocuments = list()
            # Tie the annotations together with their respective
            # documents. Then sort them and group them to get all
            # annotations for a single document. key is the pk of a
            # document. annoGroup is a list of all annotation for the
            # current document.
            for key, group in groupby(sorted(zip(annotations, annoDocuments),
                                             key=itemgetter(1)),key=itemgetter(1)):
                annoGroup = map(itemgetter(0), list(group))
                annoNum = len(annoGroup)
                if annoNum < options['maxAnno']:
                    # this creates a list of tuples. Each touple has 3
                    # elements. The first is a document that has not
                    # enough annotations. The second is the number of
                    # missing annotations. The thrid is a list of
                    # users that already annotated the current
                    # document. The fourth is already annotated
                    # proposals.
                    document = Document.objects.get(pk=key)
                    numMissingAnno = options['maxAnno']-annoNum
                    usersAlreadyAnno = map(lambda g: g.user, annoGroup)
                    # this is not needed as long as the default for
                    # unfinnished document proposals is 'proposal' see [1]
                    annoProposals = map(lambda qe: qe.proposalFlag,
                                        QueueElement.objects.filter(document=document))
                    unfinnishedDocuments.append((document, # single document
                                                 numMissingAnno, # integer
                                                 usersAlreadyAnno, # list of users
                                                 annoProposals))
                    #
                #
            touchedQueueElements = []
            # sort unfinnished documents according to the number of
            # missing annotations such that documents that have fewer
            # missing annotations are prioritised.
            for numMissingAnno, group in  groupby(sorted(unfinnishedDocuments,
                                                  key=itemgetter(1)), key=itemgetter(1)):
                uD = list(group)
                documents = map(itemgetter(0), uD)
                usersAlreadyAnno = map(itemgetter(2), uD)
                touchedQueueElements += self.createQueueElements(documents, # list of documents
                                                                 numMissingAnno,
                                                                 options,
                                                                 usersAlreadyAnno) # this is a list of lists of users
                #
            # build a dict that maps user objects (specifically
            # annotators) to their respective AnnotationQueue. Holding
            # them in memory is faster then requesting them from the
            # database for every new QueueElement.
            queues = {}

            for annotator in annotators:
                queue, created = AnnotationQueue.objects.get_or_create(user=annotator)
                logging.info(queue)
                queue.max_anno_num = options['maxAnno']
                queue.save()
                queues[annotator] = queue
                #

            print "Create annotation queue entries for untouched documents"
            untouchedQueueElements = []
            untouchedDocuments = Document.objects.filter(trainInstance=False).exclude(id__in=annoDocuments)
            documents, trash = self.active_document_queue(untouchedDocuments)

            queueElements = self.createQueueElements(documents,
                                                     options['maxAnno'],
                                                     options)
            # Delete all existing QueueElement s.
            QueueElement.objects.all().delete()
            print 'Fill database with queue entries for partially annotated documents'
            # fill database with new QueueElements for unfinnished
            # documents.
            rank = 0
            for document, proposal, usersAlreadyAnno in touchedQueueElements:
                potAnnotators = list(set(annotators)-set(usersAlreadyAnno))
                annotator = sample(potAnnotators, 1)[0] # select a random annotator
                rank += 1
                qE = QueueElement(document=document,
                                  queue=queues[annotator],
                                  proposalFlag=proposal,
                                  rank=rank)
                qE.save()

            # calcultate ranks for untouched documents
            print 'Fill database with queue entries for untouched documents'
            for annotator in annotators:
                userIdx = annotators.index(annotator)
                for document, proposal in queueElements[userIdx::len(annotators)]:
                    rank += 1
                    qE = QueueElement(document=document,
                                      queue=queues[annotator],
                                      proposalFlag=proposal,
                                      rank=rank)
                    qE.save()
                    #
                #
        endTime = datetime.datetime.now()
        print 'Ended at ' + endTime.strftime("%Y-%m-%d %H:%M") + ' and took ' + str(endTime - startTime)


# mock ups
# documents = Document.objects.all()
# options = {}
# options['maxAnno'] = 2
# options['no-proposal-freq'] = [0.25,0.25,0.5]
# options['wrong-proposal-num'] = 1
# options['no-proposal-num'] = 1

# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from annotation.models import Document, Label, Annotation, QueueElement, Score
from itertools import groupby
from operator import itemgetter, attrgetter
from collections import Counter
from django.conf import settings
import datetime
import json
import os

import pdb

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename',
                            type=str,
                            help='Filename of the file to export in. (Without the file extension)')
        parser.add_argument('--incremental',
                            dest='incremental',
                            action='store_true')
        parser.add_argument('--tsv',
                            dest='tsv',
                            type=int,
                            nargs='?',
                            help='(Optional) If used with no additional argument exports a tsv file that contains <doc_id> <document text> <annotations>. If an additional integer argument is passed only documents are exported, where the agreement of the annotators is equal to said number.')
        parser.set_defaults(incremental=False)
        parser.set_defaults(tsv=False)


    # def getScore(self, document):
    #     scores = Score.objects.filter(document=document)
    #     return [{"label": score.label.label,
    #              "nbc_normalized": score.nbc_normalized,
    #              "nbc_prior": score.nbc_prior,
    #              "nbc_term_given_label": score.nbc_term_given_label,
    #              "nbc_total": score.nbc_total}
    #             for score in scores]
        # I might want to change it to this:
        # rlt = {}
        # for score in scores:
        #     rlt.update({score.label.label: {"nbc_normalized": score.nbc_normalized,
        #                                     "nbc_prior": score.nbc_prior,
        #                                     "nbc_term_given_label": score.nbc_term_given_label,
        #                                     "nbc_total": score.nbc_total}})
        # return rlt


    def getAnnotation(self, document, annotations):
        annos = [annotation for annotation in annotations
                 if annotation.document.pk == document.pk]
        return [{"user": anno.user.__str__(),
                 "duration": anno.duration,
                 "dateTime": anno.dateTime.strftime("%Y-%m-%d %H:%M:%S"),
                 "labels": [l.label for l in list(anno.labels.all())],
                 "proposals": [p.label for p in list(anno.proposals.all())],
                 "proposalFlag": anno.proposalFlag}
                for anno in annos]


    def exportAnnotation(self, annotations, options):
        documents = set([annotation.document
                         for annotation in annotations
                         if annotation.document.trainInstance == False])
        export = {}
        for document in documents:
            if document.active_prediction:
                active_prediction = document.active_prediction.label
            else:
                active_prediction = ''
            export.update({document.doc_id: {"document": document.document,
                                             # "scores": self.getScore(document),
                                             "annotations": self.getAnnotation(document, annotations),
                                             "document": document.document,
                                             "active_prediction": active_prediction,
                                             "dateTime": document.dateTime.strftime("%Y-%m-%d %H:%M:%S"),
                                             "margin": document.margin
                                             }})
        exportName = options['filename']
        if options['incremental']:
            exportName += '_' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        exportName = settings.BASE_DIR +'/'+ exportName + '.json'
        #
        jsonExport = json.dumps(export, indent=4)
        with open(exportName, 'w') as exportFile:
            exportFile.write(jsonExport)

    def chooseAnnotation(self, annotations, options):
        document = annotations[0].document
        if options['tsv']:
            labels = map(lambda a: a.labels.all()[0].label, annotations)
            if len(labels) == 3 and len(set(labels)) == options['tsv']:
                label, count = Counter(labels).most_common()[0]
                return (document.doc_id,document.document,label)
            else:
                return None
        else:
            return (document.doc_id,
                    document.document,
                    '\t'.join(map(lambda a: a.labels.all()[0].label,
                                  annotations)))

    def handle(self, *args, **options):
        annotations = list(Annotation.objects.all())
        duplicates = [(item, count) for item, count in Counter(annotations).items() if count > 1]
        if duplicates:
            print 'The ID:'
            for duplicate, count in duplicates:
                print duplicate + ' apears ' + str(count) + ' times'
            print 'Duplicate IDs mess up the json export file. Please remove duplicates and try to export again.'
        else:
            if options['incremental']:
                # This branch should export all Annotation that have
                # not been exported during a previous increment. The
                # IDs of already exported annotations are stored in
                # the file 'incrementalRegister.csv'.
                registerName = settings.BASE_DIR + '/incrementalRegister.csv'
                if not os.path.isfile(registerName):
                    with open(registerName, 'w') as register:
                        register.write('Exported Annotation\n')
                        #
                    #
                with open(registerName, 'r') as register:
                    oldAnnotations = register.readlines()[1:]
                    #
                newAnnotations = Annotation.objects.exclude(id__in=oldAnnotations)
                self.exportAnnotation(newAnnotations, options)
                registerOutput = ''
                for pk in map(lambda a: a.pk, newAnnotations):
                    registerOutput += str(pk) + '\n'
                with open(registerName, 'a') as register:
                    register.write(registerOutput)
                    #
            # This looks weird but != False is crutial to make it
            # work. --tsv is supposed to be an optional argument and
            # an optional parameter.
            #
            # python manage.py exportAnnotation exportFile
            # will execute the else banch and not bother about tsv at
            # all
            #
            # python manage.py exportAnnotation exportFile --tsv
            # exports all annotations to a tsv file in the format
            # <doc_id>\t<document>\t<annotation>\t<annotation>...
            #
            # python manage.py exportAnnotation exportFile --tsv int
            # exports only one annotation to a tsv file. The
            # annotation is choosen by majority vote.
            elif options['tsv'] != False:
                annotations = list(Annotation.objects.all())
                annoPerDoc = [self.chooseAnnotation(list(annos), options)
                              for pk, annos in groupby(sorted(annotations,
                                                   key=lambda a: a.document.pk),
                                            key=lambda a: a.document.pk)]
                #
                annoPerDoc = filter(lambda x: x != None, annoPerDoc)
                exportName = settings.BASE_DIR +'/'+ options['filename'] + '.tsv'
                export = '\n'.join(map(lambda tpl: '\t'.join(tpl), annoPerDoc))
                with open(exportName, 'w') as exportFile:
                    exportFile.write(export.encode('utf-8'))
                    #
            else:
                # This branch exports all existing annotations
                self.exportAnnotation(annotations, options)


# options = {}
# options['filename'] = 'export.json'

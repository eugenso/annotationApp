from django.core.management.base import BaseCommand, CommandError
from annotation.models import Document, Label, Annotation
import json

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename',
                            type=str,
                            help='Filename of the file to export in.')

    def handle(self, *args, **options):
        documents = Document.objects.filter(trainInstance=False)
        export = {}
        [export.update({doc.doc_id: {"document": doc.document.encode('utf8'),
                                     "prediction": doc.active_prediction.label if
                                     doc.active_prediction else "",
                                     "margin": doc.margin,
                                     "annotations": self.getAnnotations(doc)}})
         for doc in documents]
        json_export = json.dumps(export)
        with open(options['filename'], 'w') as exportfile:
            exportfile.write(json_export)


    def getAnnotations(self, doc):
        return [{"user": anno.user.username,
                 "user_pk": str(anno.user.pk),
                 "labels": map(lambda l: l.label, Label.objects.filter(annotation=anno)),
                 "duration": anno.duration}
                for anno in Annotation.objects.filter(document=doc)]

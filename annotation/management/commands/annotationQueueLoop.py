# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings

from annotation.models import Annotation

import os

class Command(BaseCommand):
    def handle(self, *args, **options):
        registerName = settings.BASE_DIR + '/annotationRegister.csv'
        if not os.path.isfile(registerName):
            with open(registerName, 'w') as register:
                output = 'Annotations:' + str(Annotation.objects.all().count()) + '\n'
                output += 'Runs:0'
                register.write(output)
        else:
            oldAnnoNum = 0
            with open(registerName, 'r') as register:
                content = register.readlines()
                oldAnnoNum = int(content[0].split(':')[1])
                runs = int(content[1].split(':')[1])
            newAnnoNum = Annotation.objects.all().count()
            if oldAnnoNum != newAnnoNum:
                with open(registerName, 'w') as register:
                    output = 'Annotations:' + str(newAnnoNum) + '\n'
                    output += 'Runs:' + str(runs+1)
                    register.write(output)
                call_command('createAnnotationQueue', '3', '1', '1', '0.2', '0.2', '0.6')

# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Document, Label, Annotation, NBC_class_count, NBC_word_count_given_class, NBC_vocabulary, QueueElement, AnnotationQueue, Score

admin.site.register(Document)
admin.site.register(Label)
admin.site.register(Annotation)
admin.site.register(QueueElement)
admin.site.register(AnnotationQueue)
admin.site.register(NBC_class_count)
admin.site.register(NBC_word_count_given_class)
admin.site.register(NBC_vocabulary)

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User

@python_2_unicode_compatible
class Document(models.Model):
    document = models.CharField(max_length=10000)
    doc_id = models.CharField(max_length=1000)
    preprocessed = models.CharField(max_length=10000)
    trainInstance = models.BooleanField()
    #
    def __str__(self):
        return self.document[:100]


@python_2_unicode_compatible
class Label(models.Model):
    label = models.CharField(max_length=100)
    option = models.CharField(max_length=5)
    #
    def __str__(self):
        return self.label


@python_2_unicode_compatible
class Annotation(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    user = models.ForeignKey(User)
    labels = models.ManyToManyField(Label)
    duration = models.CharField(max_length=100)
    #
    def __str__(self):
        user = 'User: ' + self.user.__str__()
        duration = ', duration: ' + str(round(float(self.duration)/100)/10) + ' secs, '
        labels = 'labels: ' + ', '.join([l.label for l in self.labels.all()])
        docs = ', doc: ' + self.document.__str__().decode('utf-8')
        return user + duration + labels + docs


@python_2_unicode_compatible
class NBC_class_count(models.Model):
    label = models.ForeignKey(Label)
    count = models.IntegerField()
    total_word_count = models.IntegerField()
    #
    def __str__(self):
        count = 'Class count: ' + str(self.count)
        label = ' of label: ' + self.label.__str__()
        words = ' with a total of ' + str(self.total_word_count) + ' words'
        return count + label + words


@python_2_unicode_compatible
class NBC_vocabulary(models.Model):
    word = models.CharField(max_length=100)
    #
    def __str__(self):
        return self.word


@python_2_unicode_compatible
class NBC_word_count_given_class(models.Model):
    label = models.ForeignKey(Label)
    word = models.ForeignKey(NBC_vocabulary) # models.CharField(max_length=100)
    count = models.IntegerField()
    def __str__(self):
        w = '"' + self.word.__str__() + '"' + ' occured '
        c = str(self.count) + ' times in class '
        return w + c + self.label.__str__()

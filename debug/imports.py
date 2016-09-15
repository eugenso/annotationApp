from annotation.models import Document, Label, Annotation
from annotation.models import NBC_class_count, NBC_vocabulary, NBC_word_count_given_class

from django.utils.encoding import python_2_unicode_compatible

import annotation.classifier as clf

from sklearn.metrics import confusion_matrix, accuracy_score
import re

from pprint import pprint

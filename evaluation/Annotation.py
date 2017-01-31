from __future__ import division

import itertools as it
import json

from operator import itemgetter
from copy import deepcopy

class Annotation:
    """
    This class accepts JSON files and offers easier dealing with
    annotations.

    """

    def __init__(self, annotationFileName):
        """
        annotationFileName -> string: path to JSON file containing
        annotations.

        """
        with open(annotationFileName) as annotationFile:
            self.rawAnnotations = json.load(annotationFile)
            #
            # all annotations independent of their corresponding document.
        self.all = reduce(lambda l, r: l+r,
                          [document['annotations']
                           for (doc_id, document) in self.rawAnnotations.items()])

        k = itemgetter('user')
        # sort annotations by user names as preparation. Then group
        # them by user names. Iterate over the result and realize the
        # generator objects. Feed the result to a dictionary.
        self.user = dict(map(lambda (user, annotations):(user, list(annotations)),
                             it.groupby(sorted(self.all, key=k), key=k)))

        self.document = [document for doc_id, document in self.rawAnnotations.iteritems()]


    def ofAll(self, attributes):
        return map(lambda a:
                   map(lambda att: a[att], attributes),
                   self.all)


    def perDocument(self, minAnno, attributes):
        return [map(lambda a:d[a], attributes) for d in self.document
                if len(d['annotations']) >= minAnno]


    def perUser(self, attribute):
        """
        perUser returns a dictionary in which a key is a user name and a
        value is a list of annotation attributes specified by <attribute>.

        attribute -> string: the following values are supported
        labels, proposals, dateTime, proposalFlag, duration.

        """
        return dict((user, map(itemgetter(attribute), annotation))
                    for (user, annotation) in self.user.iteritems())


    def durationToSec(self, duration):
        convert = lambda d: float(d)/1000
        if hasattr(duration, '__iter__'):
            return map(convert, duration)
        else:
            return convert(duration)

from operator import attrgetter
from itertools import groupby

all = NBC_word_count_given_class.objects.all()
word = attrgetter('word')
label=  attrgetter('label')
sortWord = sorted(all, key=word)
gWord = dict((k, list(v)) for (k, v) in groupby(sortWord, key=word))
gSmallWord = dict((w,v) for (w, v) in gWord.iteritems() if len(v) >1)
#
wordSortLabel = dict((w, dict((l, list(o)) for (l, o) in groupby(sorted(v, key=label), key=label))) for (w, v) in gSmallWord.iteritems())

# print all NBC_word_count_given_class instances that appear more than
# once:
for word, v in wordSortLabel.iteritems():
    for label, o in v.iteritems():
        if len(o) > 1:
            print o

# [<NBC_word_count_given_class: "london" occured 1 times in class No Sent>, <NBC_word_count_given_class: "london" occured 1 times in class No Sent>]
# [<NBC_word_count_given_class: "fehler" occured 1 times in class No Sent>, <NBC_word_count_given_class: "fehler" occured 1 times in class No Sent>]
# [<NBC_word_count_given_class: "meistens" occured 1 times in class No Sent>, <NBC_word_count_given_class: "meistens" occured 1 times in class No Sent>]
# [<NBC_word_count_given_class: "nstiger" occured 1 times in class No Sent>, <NBC_word_count_given_class: "nstiger" occured 1 times in class No Sent>]

# find the documents that are potential sources
noSent=Label.objects.filter(label='No Sent').first()
Annotation.objects.filter(labels=noSent)


def fn(token, label):
    try:
        wcgc, created_wcgc = NBC_word_count_given_class.objects.get_or_create(
            word=token, label=label)
    except:
        duplicates = NBC_word_count_given_class.objects.filter(word=token, label=label)
        count = sum(map(attrgetter('count'), duplicates))
        duplicates.delete()
        wcgc = NBC_word_count_given_class(word=token, label=label)
        wcgc.count = count
        wcgc.save()

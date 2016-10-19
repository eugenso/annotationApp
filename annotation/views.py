import datetime
import random
import re

from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from annotation.models import Document, Label, Annotation

from annotation.forms import AnnotationForm, TrainingForm

import annotation.classifier as clf
import annotation.active_selection as sel
import logging

# def selectDocument():
#     empty_doc = Document.objects.filter(trainInstance=False).exclude(
#         id__in=map(lambda a: a.document.pk, Annotation.objects.all())).first()
#     # empty_doc = Document.objects.exclude(
#     #     id__in=map(lambda a: a.document.pk ,Annotation.objects.all()),
#     #     trainInstance=True).first()
#     if empty_doc:
#         document = empty_doc
#     else:
#         document = Document(document='ALL DOCUMENTS HAVE BEEN ANNOTATED. THANK YOU FOR YOUR PARTICIPATION!',
#                             doc_id='',
#                             preprocessed='',
#                             trainInstance=True)
#     return document

def selectProposal(document, proposalFlag):
    if proposalFlag == 'proposal':
        if document.active_prediction:
            proposal = [document.active_prediction.pk]
        else:
            proposal = []
    elif proposalFlag == 'wrong proposal':
        predicted_label = document.active_prediction.pk
        wrongLabels = list(set(Label.objects.all())-set(predicted_label))
        proposal = [sample(wrongLabels, 1)[0].pk]
    else:
        proposal = []
    return proposal

@login_required(login_url='/annotation/login/') #user_login
def index(request):
    context = {} # a dict with content used in the template
    labels = Label.objects.all()
    context['labels'] = labels
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        logging.info(request.POST)
        # create a form instance and populate it with data from the request:
        form = AnnotationForm(labels, request.POST)
        # check whether it's valid:
        if form.is_valid():
            # create the new annotation
            old_pk = int(form.data['old_pk'])
            old_doc = Document.objects.get(pk=old_pk)
            annotation = Annotation(document=old_doc,
                                    user=request.user,
                                    duration=form.data['duration'])

            annotation.save() # save the annotation to the DB
            #
            annotation.labels.add(*form.cleaned_data['labels'])
            old_proposals = map(int, re.findall(r'\d+', form.data['old_proposal']))
            annotation.proposals.add(*old_proposals)
            #
            clf.online_train(old_doc, form.cleaned_data['labels'])

            document, proposalFlag = sel.selectDocument(request.user)
            context['proposals'] = selectProposal(document, proposalFlag)
            context['document'] = document
            form = AnnotationForm(labels)
            context['form'] = form

            return render(request, 'annotation/index.html', context)
    else:
        document, proposalFlag = sel.selectDocument(request.user, True)
        context['proposals'] = selectProposal(document, proposalFlag)
        context['document'] = document
        form = AnnotationForm(labels)
        context['form'] = form

        return render(request, 'annotation/index.html', context)


@login_required(login_url='/annotation/login/')
def training(request):
    context = {} # a dict with content used in the template
    labels = Label.objects.all()
    context['labels'] = labels
    if request.method == 'POST':
        form = TrainingForm(labels, request.POST)
        # check whether it's valid:
        if form.is_valid():
            # depending on whether the classify button
            # (classifySubmit) or the train button (trainSubmit) was
            # pressed diffent actions are performed
            if 'classifySubmit' in form.data:
                document = Document(document=form.data['trainDocument'],
                                    doc_id='doc to be classified',
                                    preprocessed=' '.join(clf.preprocessing(
                                        form.data['trainDocument'])),
                                    trainInstance=True)
                # only is there is a document and it contains words it
                # will be classified
                scores = clf.predict(document)
                if scores:
                    context['scores'] = scores
                    proposals = clf.predict_label(document, scores=scores)
                    if proposals:
                        context['proposals'] = map(lambda l: l.pk, [proposals])
                    else:
                        raise ValidationError(
                            'There is no predictive model yet. Please train at least one document before classifing',
                            code='invalid',
                        )
                    context['classifiedDocument'] = document.document

            #elif 'trainSubmit' in form.data:
            else:
                document = Document(document=form.data['trainDocument'],
                                    doc_id=str(datetime.datetime.now()),
                                    preprocessed=' '.join(clf.preprocessing(
                                        form.data['trainDocument'])),
                                    trainInstance=True)
                document.save()
                annotation = Annotation(document=document,
                                        user=request.user,
                                        duration=-1)
                annotation.save()
                [annotation.labels.add(label)
                 for label in form.cleaned_data['labels']]
                clf.online_train(document, form.cleaned_data['labels'])
            # else:
            #     raise Http404("Ups something went wrong.")

            return render(request,
                          'annotation/training.html',
                          context)
        else:
            raise Http404("Ups something went wrong.")
    else:
        return render(request,
                      'annotation/training.html',
                      context)

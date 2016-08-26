from django import forms
from annotation.models import Annotation

#from django.forms import ModelForm, Form, HiddenInput

class AnnotationForm(forms.Form):
    # duration = forms.CharField(
    #     max_length=100,
    #     widget=forms.HiddenInput(attrs={'id':'duration'}))
    def __init__(self, labels=None, *args, **kwargs):
        super(AnnotationForm, self).__init__(*args, **kwargs)
        if labels:
            self.fields['labels'] = forms.ModelMultipleChoiceField(
                queryset=labels,
                widget=forms.CheckboxSelectMultiple())

class TrainingForm(forms.Form):
    def __init__(self, labels=None, *args, **kwargs):
        super(TrainingForm, self).__init__(*args, **kwargs)
        if labels:
            self.fields['labels'] = forms.ModelMultipleChoiceField(
                queryset=labels,
                required=False,
                widget=forms.CheckboxSelectMultiple())








# LEGACY CODE
# class AnnotationForm(ModelForm):
#     class Meta:
#         model = Annotation
#         fields = ['labels', 'duration', 'user', 'document']
#         widgets = {'duration': HiddenInput(),
#                    'user': HiddenInput(),
#                    'document': HiddenInput()}

# from django.forms import forms
# from .models import Annotation

# class AnnotationForm(forms.Form):

#     def __init__(self, *args, **kwargs):
#         print kwargs.pop('labels',None)
#         #self.user = kwargs.pop('user',None)
# #        self.labels = forms.SelectMultiple(choices=kwargs.pop('labels',None))
#         super(AnnotationForm, self).__init__(*args, **kwargs)

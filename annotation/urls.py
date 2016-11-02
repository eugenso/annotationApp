# -*- coding: utf-8 -*-
from django.conf.urls import url

from annotation import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^guidelines/$', views.guidelines, name='guidelines'),
    url(r'^training/$', views.training, name='training'),
]

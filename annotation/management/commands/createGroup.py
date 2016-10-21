# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    def handle(self, *args, **options):
        annotators = Group.objects.create(name='Annotators')
        add = lambda permission: annotators.permissions.add(permission)
        add(Permission.objects.get(name='Can add annotation'))
        add(Permission.objects.get(name='Can change annotation'))
        add(Permission.objects.get(name='Can delete annotation'))
        add(Permission.objects.get(name='Can add annotation queue'))
        add(Permission.objects.get(name='Can change annotation queue'))
        add(Permission.objects.get(name='Can delete annotation queue'))
        add(Permission.objects.get(name='Can add document'))
        add(Permission.objects.get(name='Can change document'))
        add(Permission.objects.get(name='Can delete document'))
        add(Permission.objects.get(name='Can add label'))
        add(Permission.objects.get(name='Can change label'))
        add(Permission.objects.get(name='Can delete label'))
        add(Permission.objects.get(name='Can add nb c_class_count'))
        add(Permission.objects.get(name='Can change nb c_class_count'))
        add(Permission.objects.get(name='Can delete nb c_class_count'))
        add(Permission.objects.get(name='Can add nb c_vocabulary'))
        add(Permission.objects.get(name='Can change nb c_vocabulary'))
        add(Permission.objects.get(name='Can delete nb c_vocabulary'))
        add(Permission.objects.get(name='Can add nb c_word_count_given_class'))
        add(Permission.objects.get(name='Can change nb c_word_count_given_class'))
        add(Permission.objects.get(name='Can delete nb c_word_count_given_class'))
        annotators.save()

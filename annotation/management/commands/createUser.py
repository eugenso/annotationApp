# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, Permission

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('username',
                            type=str,
                            help='Username has to be unique.')
        parser.add_argument('password',
                            type=str,
                            help='User password.')

    def handle(self, *args, **options):
        user = User.objects.create_user(options['username'],
                                        password=options['password'])
        user.groups.add(Group.objects.get(name='Annotators'))
        user.save()

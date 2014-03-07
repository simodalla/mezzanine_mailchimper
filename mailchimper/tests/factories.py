# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from copy import deepcopy

from mezzanine.utils.models import get_user_model
User = get_user_model()

import factory

from ..models import List

LIST_RESULT = {
    "total": 2,
    "data": [{"id": "example id 1", "web_id": 41, "name": "example name 1"},
             {"id": "example id 2", "web_id": 42, "name": "example name 2"}],
    "errors": []}
LIST_RESULT_WITH_ERROR = deepcopy(LIST_RESULT)
LIST_RESULT_WITH_ERROR['errors'].append(
    {"param": "example param", "code": 42, "error": 42})
RESPONSE_ERROR = {
    "status": "error",
    "code": -99,
    "name": "Unknown_Exception",
    "error": "An unknown error occurred processing your request. "
             "Please try again later."}
MEMBERS_RESULT = {
    "total": 2,
    "data": [{"id": "member_id_1", "email": "member1@example.com",
             'merges': {'EMAIL': 'member1@example.com', 'FNAME': 'Simon',
                        'GROUPINGS': [], 'LNAME': 'Giveit'}},
             {"id": "member_id_2", "email": "member2@example.com",
              'merges': {'EMAIL': 'member2@example.com', 'FNAME': 'John',
                         'GROUPINGS': [], 'LNAME': 'Red'}}]}


class UserF(factory.DjangoModelFactory):
    FACTORY_FOR = User
    FACTORY_DJANGO_GET_OR_CREATE = ('username',)

    username = factory.Sequence(lambda n: 'user_%s' % n)
    password = factory.PostGenerationMethodCall('set_password', 'default')
    first_name = factory.Sequence(lambda n: "first_name_%s" % n)
    last_name = factory.Sequence(lambda n: "last_name_%s" % n)
    email = factory.LazyAttribute(
        lambda a: '{}@example.come'.format(a.username))
    is_staff = True
    is_active = True

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for group in extracted:
                self.groups.add(group)


class AdminF(UserF):
    username = 'admin'
    first_name = 'admin'
    last_name = 'admin'
    is_superuser = True


class ListF(factory.DjangoModelFactory):
    FACTORY_FOR = List
    FACTORY_DJANGO_GET_OR_CREATE = ('id',)

    id = factory.Sequence(lambda n: 'abcd%s' % n)
    name = factory.Sequence(lambda n: 'list %s' % n)
    selectable = True

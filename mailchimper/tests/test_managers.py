# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from copy import deepcopy
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.db import models
from django.core.exceptions import ImproperlyConfigured

from mezzanine.utils.models import get_user_model

from mailchimp import Mailchimp

from ..managers import ContentObjectMemberManager, MailchimperManager, ListManager, UserMemberManager
from ..models import List, UserMember
from .factories import LIST_RESULT, MEMBERS_RESULT

User = get_user_model()


class DemoMailchimperModel(models.Model):
    objects = MailchimperManager()


class WrongDemoContentObjectMemberModel(models.Model):
    mailchimper = ContentObjectMemberManager()


class DemoContentObjectMemberModel(models.Model):
    pass


@patch('mailchimper.managers.settings')
class MailchimperManagerTest(unittest.TestCase):

    def test_mailchimper_is_mailchimp_instance(self, mock_settings):
        mock_settings.MAILCHIMP_API_KEY = '000000000000000000000000-us3'
        mailchimp = DemoMailchimperModel.objects.mailchimper
        self.assertIsInstance(mailchimp, Mailchimp)
        mock_settings.use_editable.assert_called_once_with()

    def test_mailchimper_raise_improperly_configured(self, mock_settings):
        mock_settings.MAILCHIMP_API_KEY = None
        self.assertRaises(ImproperlyConfigured,
                          DemoMailchimperModel.objects.__getattribute__,
                          'mailchimper')
        mock_settings.use_editable.assert_called_once_with()


class ListManagerTest(unittest.TestCase):

    @patch('mailchimper.models.ListManager.mailchimper')
    def test_make_import_new_lists(self, mock_mailchimper):
        mock_mailchimper.lists.list.return_value = deepcopy(LIST_RESULT)
        lists_created, result = List.objects.import_lists()
        self.assertIsInstance(lists_created, list)
        self.assertIsInstance(result, dict)
        mock_mailchimper.lists.list.assert_is_called_once_with(filters=None)
        self.assertEqual(len(lists_created), 2)
        self.assertEqual(List.objects.count(), 2)
        for data in LIST_RESULT['data']:
            list_obj = List.objects.get(id=data['id'])
            for field in List._meta.get_all_field_names():
                if field in data:
                    self.assertEqual(getattr(list_obj, field), data[field])


class ContentObjectMemberManagerTest(unittest.TestCase):

    def test_call_map_data(self):
        data = deepcopy(MEMBERS_RESULT['data'][0])
        map_data = WrongDemoContentObjectMemberModel.mailchimper.map_data(
            data)
        self.assertEqual(map_data['email'], data['email'])

    def test_call_get_or_create_from_mailchimp_without_overriding(self):
        model = WrongDemoContentObjectMemberModel
        self.assertRaises(NotImplementedError,
                          model.mailchimper.get_or_create_from_mailchimp, {})


class UserMemeberManagerTest(unittest.TestCase):
    def test_call_map_data(self):
        data = deepcopy(MEMBERS_RESULT['data'][0])
        map_data = UserMember.mailchimper.map_data(data)
        self.assertEqual(map_data['first_name'], data['merges']['FNAME'])
        self.assertEqual(map_data['last_name'], data['merges']['LNAME'])

    @patch('mailchimper.managers.UserMemberManager.map_data')
    def test_get_or_create_from_mailchimp_create_user(self, mock_map_data):
        data = deepcopy(MEMBERS_RESULT['data'][0])
        mock_map_data.return_value = {'last_name': 'Red',
                                      'first_name': 'Simon'}
        user, created = UserMember.mailchimper.get_or_create_for_member(data)
        mock_map_data.assert_called_once_with(data)
        # import ipdb
        # ipdb.set_trace()

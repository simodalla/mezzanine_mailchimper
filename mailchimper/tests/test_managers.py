# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from copy import deepcopy
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured

from mailchimp import Mailchimp

from ..managers import MailchimperManager, ListManager
from ..models import List
from .factories import LIST_RESULT


class DemoMailchimperModel(models.Model):
    objects = MailchimperManager()


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

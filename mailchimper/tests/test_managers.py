# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.db import models
from django.core.exceptions import ImproperlyConfigured

from mailchimp import Mailchimp

from ..managers import MailchimperManager


class DemoMailchimperModel(models.Model):
    objects = MailchimperManager()


@patch('mailchimper.managers.settings')
class MailchimperModelTest(unittest.TestCase):

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

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

from ..utils import MailchimperModel


class DemoMailchimperModel(MailchimperModel, models.Model):
    pass


class MailchimperModelTest(unittest.TestCase):
    def setUp(self):
        self.dmm = DemoMailchimperModel()

    @patch('mailchimper.utils.settings')
    def test_mailchimper_is_mailchimp_instance(self, mock_settings):
        mock_settings.MAILCHIMP_API_KEY = '000000000000000000000000-us3'
        mailchimp = self.dmm.mailchimper
        self.assertIsInstance(mailchimp, Mailchimp)
        mock_settings.use_editable.assert_called_once_with()

    @patch('mailchimper.utils.settings')
    def test_mailchimper_raise_improperly_configured(self, mock_settings):
        mock_settings.MAILCHIMP_API_KEY = None
        self.assertRaises(ImproperlyConfigured,
                          self.dmm.__getattribute__, 'mailchimper')
        mock_settings.use_editable.assert_called_once_with()

# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.exceptions import ImproperlyConfigured
from django.db import models

from mezzanine.conf import settings

from mailchimp import Mailchimp


class MailchimperManager(models.Manager):

    @property
    def mailchimper(self):
        settings.use_editable()
        if not getattr(settings, 'MAILCHIMP_API_KEY', None):
            raise ImproperlyConfigured("The MAILCHIMP_API_KEY setting must "
                                       "not be empty.")
        return Mailchimp(settings.MAILCHIMP_API_KEY)

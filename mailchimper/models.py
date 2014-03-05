# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.models import TimeStamped

from .utils import MailchimperModel


@python_2_unicode_compatible
class List(MailchimperModel, TimeStamped):
    id = models.CharField(_('mailchimp id'), max_length=15, unique=True,
                          editable=False, primary_key=True)
    webid = models.IntegerField(_('mailchimp webid'), unique=True,
                                editable=False, null=True)
    name = models.CharField(_('name'), max_length=300, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('list')
        verbose_name_plural = _('lists')

    def __str__(self):
        return self.name

    @classmethod
    def make_import(cls, request=None, filters=None):
        mailchimper = cls().mailchimper
        result = mailchimper.lists.list(filters=filters)
        model_fields = cls._meta.get_all_field_names()
        try:
            for data in result['data']:
                id = data.pop('id')
                list_obj, _ = cls.objects.get_or_create(id=id)
                for field in data:
                    if field in model_fields:
                        setattr(list_obj, field, data[field])
                list_obj.save()
        except AttributeError as e:
            pass
        return result


class Member(MailchimperModel, models.Model):
    pass

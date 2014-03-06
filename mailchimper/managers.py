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


class MemberManager(MailchimperManager):

    def get_or_create_content_type(self, pk, email, content_type,
                                   force_update_member=False, **kwargs):
        model_type = content_type.model_class()
        instance, i_created = model_type.objects.get_or_create(email=email)
        member, m_created = self.get_or_create(
            id=pk, defaults={'email': email, 'content_object': instance})
        if force_update_member and not m_created:
            member.email = email
            member.content_object = instance
            member.save()
        return member, m_created, i_created


class ListManager(MailchimperManager):

    def import_lists(self, filters=None, request=None):
        result = self.mailchimper.lists.list(filters=filters)
        model_fields = self.model._meta.get_all_field_names()
        lists_created = []
        for data in result['data']:
            list_id = data.pop('id')
            list_obj, _ = self.model.objects.get_or_create(pk=list_id)
            for field in data:
                if field in model_fields:
                    setattr(list_obj, field, data[field])
            list_obj.save()
            lists_created.append(list_obj.pk)
        return lists_created, result

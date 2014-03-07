# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from copy import deepcopy

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
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


class ContentObjectMemberManager(models.Manager):

    def map_data(self, data):
        result = {'email': data['email']}
        return result

    def get_or_create_from_mailchimp(self, data, force_update=True):
        raise NotImplementedError("Implement get_or_create_from_mailchimp"
                                  " method for your manager.")


class UserMemberManager(ContentObjectMemberManager):

    def map_data(self, data):
        return {'first_name': data['merges']['FNAME'],
                'last_name': data['merges']['LNAME']}

    def get_or_create_for_member(self, data, force_update=True):
        email = data['email']
        try:
            raise ObjectDoesNotExist()
        except ObjectDoesNotExist:
            user = self.model.objects.create_user(
                email, email, **self.map_data(data))
            created = True
            return user, created


class MemberManager(MailchimperManager):
    def get_or_create_by_content_type(self, pk, email, content_type,
                                      force_update_member=False, **kwargs):
        model_type = content_type.model_class()
        try:
            instance = model_type.mailchimper.create_from_mailchimp(
                email, **kwargs)
        except NotImplemented:
            instance = None
        member, m_created = self.get_or_create(
            id=pk, defaults={'email': email, 'content_object': instance})
        if force_update_member and not m_created:
            member.email = email
            member.content_object = instance
            member.save()
        return member, m_created


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

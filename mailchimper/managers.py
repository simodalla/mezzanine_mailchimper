# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import sys

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import (ImproperlyConfigured, ObjectDoesNotExist,
                                    MultipleObjectsReturned)
from django.db import models
from django.db import Error

from mezzanine.conf import settings

from mailchimp import Mailchimp


class MailchimperManager(models.Manager):

    @property
    def mailchimper(self):
        """
        Property for get an Mailchimp object
        """
        settings.use_editable()
        if not getattr(settings, 'MAILCHIMP_API_KEY', None):
            raise ImproperlyConfigured("The MAILCHIMP_API_KEY setting must "
                                       "not be empty.")
        return Mailchimp(settings.MAILCHIMP_API_KEY)


class ContentObjectMemberManager(models.Manager):

    def map_data(self, data):
        result = {'email': data['email']}
        return result

    def get_or_create_for_member(self, data, force_update=False):
        raise NotImplementedError("Implement get_or_create_from_mailchimp"
                                  " method for your manager.")


class UserMemberManager(ContentObjectMemberManager):

    def map_data(self, data):
        """
        Return a dict in format {'model_field': mailchimp_data}

        :param data: data of Mailchimp.lists.[memebers/member_info] response
        :type data: dict
        """
        return {'first_name': data['merges']['FNAME'],
                'last_name': data['merges']['LNAME']}

    def get_or_create_for_member(self, data, force_update=False):
        """
        Return a tuple of two elements, the first is an instance of self.model
        and the second is True if a new instance of self.model or is False if
        a instance of self.model is alredy in db.

        :param data: data of Mailchimp.lists.[memebers/member_info] response
        :type data: dict
        :param force_update:
        :type force_update: Bool
        :rtype: tuple
        :raise: MultipleObjectsReturned
        """
        email = data['email']
        try:
            user = self.model.objects.get(models.Q(username=email) |
                                          models.Q(email=email))
            return user, False
        except ObjectDoesNotExist:
            user = self.model.objects.create_user(
                email, email, **self.map_data(data))
            return user, True
        except MultipleObjectsReturned as e:
            raise e


class MemberManager(MailchimperManager):
    def get_or_create_for_model(self, data, model, force_update=False,
                                force_update_model=False):
        """
        Get or create an Member object (and his content_object object)
        with data from  Mailchimp.lists.[memebers/member_info] response.

        :param data: data of Mailchimp.lists.[memebers/member_info] response
        :type data: dict
        :param model: django.models.Model with attribute mailchamper that is
                     a manager child of ContentObjectMemberManager
        :type model: django.models.Model
        :param force_update_model:
        :type force_update_model: Bool
        :param force_update_model:
        :type force_update_model: Bool
        :return: tuple with Member object selected or create an a boolean
                 indicate if object is selected or created
        :rtype: (Member object, Bool) or None
        """
        from .models import Log
        email = data['email']
        member_id = data['id']
        model_instance = None
        try:
            model_instance, _ = (
                model.mailchimper.get_or_create_for_member(
                    data, force_update=force_update_model))
        except Exception:
            type_, value_, traceback_ = sys.exc_info()
            Log.log(data, value_, traceback_, model=model)
        try:
            member, created = self.model.objects.get_or_create(
                id=member_id,
                content_type=ContentType.objects.get_for_model(model),
                defaults={'email': email, 'content_object': model_instance})
            if not created and force_update:
                member.email = email
                member.content_object = model_instance
                member.save()
            return member, created
        except Error:
            type_, value_, traceback_ = sys.exc_info()
            Log.log(data, value_, traceback_, model=self.model)


class ListManager(MailchimperManager):

    def import_lists(self, filters=None, request=None):
        """

        """
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

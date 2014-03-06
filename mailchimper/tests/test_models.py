# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from copy import deepcopy
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from ..models import List, Member


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


class MemberModelTest(TestCase):
    def setUp(self):
        email = 'mamber1@example.com'
        self.user = User.objects.create_user('member1', email=email)
        self.member = Member(email=self.user.email, content_object=self.user)
        self.member.save()

    def test_str(self):
        member = Member()
        member.email = 'member@example.com'
        self.assertEqual(member.__str__(), member.email)

    def test_get_object_link(self):
        url = '/fake-url/'
        self.assertEqual(
            self.member.get_object_link(url),
            '<a href="{url}">{member.content_type.name}: {member.'
            'content_object}</a>'.format(url=url, member=self.member))

    @patch('mailchimper.models.Member.get_object_link')
    @patch('mailchimper.models.reverse')
    @patch('mailchimper.models.admin_urlname')
    def test_object_admin_link(
            self, mock_admin_urlname, mock_reverse, mock_get_object_link):
        view = 'changelist'
        url = '%s%s' % ('admin:app_model_', view)
        object_link = '<a>fake</a>'
        mock_admin_urlname.return_value = url
        mock_reverse.return_value = url
        mock_get_object_link.return_value = object_link
        self.assertEqual(self.member.get_object_admin_link(), object_link)
        mock_admin_urlname.assert_is_called_once_with(
            self.member.content_object._meta, view)
        mock_get_object_link.assert_called_once_with(
            '%s?id=%s' % (url, self.member.object_id))

    @patch('mailchimper.models.Member.get_object_link')
    @patch('django.contrib.auth.models.User.get_absolute_url')
    def test_object_site_url(self, mock_absolute_url, mock_get_object_link):
        url = '/fake-absolute_url'
        object_link = '<a>fake</a>'
        mock_absolute_url.return_value = url
        mock_get_object_link.return_value = object_link
        self.assertEqual(self.member.get_object_site_link(), object_link)
        mock_absolute_url.assert_called_once_with()
        mock_get_object_link.assert_called_once_with(url)

    @patch('mailchimper.models.Member.get_object_link')
    @patch('django.contrib.auth.models.User.get_absolute_url')
    def test_object_site_url_return_empty_string(
            self, mock_absolute_url, mock_get_object_link):
        mock_absolute_url.side_effect = AttributeError('Boom!')
        self.assertEqual(self.member.get_object_site_link(), '')
        mock_absolute_url.assert_called_once_with()
        self.assertEqual(len(mock_get_object_link.mock_calls), 0)


class ListModelTest(TestCase):

    # def setUp(self):
    #     self.list_obj = List.objects.create(id='abc', name='abc',
    #                                         selectable=True)
    #     self.user_content_type = ContentType.objects.get_for_model(User)
    #     self.list_obj.content_types.add(self.user_content_type)
    def test_str(self):
        list_obj = List()
        list_obj.name = 'list 1'
        self.assertEqual(list_obj.__str__(), list_obj.name)

    @patch('mailchimper.models.List.mailchimper')
    def test_make_import_new_lists(self, mock_mailchimper):
        mock_mailchimper.lists.list.return_value = deepcopy(LIST_RESULT)
        lists_created, result = List.make_import()
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

    def test_import_members_called_with_wrong_ct_raise_exception(self):
        """
        Test if calling memmber_called with ContentType that not in
        self.content_type raise an ValueError
        """
        list_obj = List(id='abc', name='abc', selectable=True)
        list_obj.save()
        user_content_type = ContentType.objects.get_for_model(User)
        list_obj.content_types.add(user_content_type)
        self.assertRaises(ValueError,
                          list_obj.import_members,
                          ContentType.objects.get_for_model(Group))

# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.test import TestCase, RequestFactory, SimpleTestCase

from .factories import LIST_RESULT
from ..views import ImportListView


@patch('mailchimper.views.List.objects.import_list')
class ImportListViewTest(SimpleTestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = '/mailchimper/list/import/'
        self.view = ImportListView.as_view()

    def test_import_lists_method_is_called(self, mock_import_list):
        mock_import_list.return_value = ([1, 2], LIST_RESULT)
        request = self.factory.get(self.url)
        self.view(request)
        mock_import_list.assert_called_once_with(request=request,
                                                 filters={})

    def test_call_view_with_wrong_get_key(self, mock_import_list):
        """
        Test that if in query_dict is passed one key that not in filters of
        http://apidocs.mailchimp.com/api/2.0/lists/list.php,
        List.objects.import_list is called without filters.
        """
        mock_import_list.return_value = ([1, 2], LIST_RESULT)
        request = self.factory.get(self.url + '?wrong_key=wrong_value')
        self.view(request)
        mock_import_list.assert_called_once_with(request=request, filters={})

    def test_call_view_with_rigth_get_key(self, mock_import_list):
        """
        Test that if in query_dict is passed one key that is in filters of
        http://apidocs.mailchimp.com/api/2.0/lists/list.php,
        List.objects.import_list is called without filters.
        """
        mock_import_list.return_value = ([1, 2], LIST_RESULT)
        request = self.factory.get(self.url + '?list_name=list_1')
        self.view(request)
        mock_import_list.assert_called_once_with(
            request=request, filters={'list_name': 'list_1'})

    def test_default_url_redirect(self, mock_import_list):
        mock_import_list.return_value = ([1, 2], LIST_RESULT)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, '/admin/mailchimper/list/')

    def test_url_redirect_to_next(self, mock_import_list):
        mock_import_list.return_value = ([1, 2], LIST_RESULT)
        response = self.client.get(self.url + '?next=/redirect_here/',
                                   follow=True)
        self.assertRedirects(response, '/redirect_here/',
                             target_status_code=404)





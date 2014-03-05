# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from copy import deepcopy
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.test import TestCase

from ..models import List


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



class ListModelTest(TestCase):
    def setUp(self):
        pass

    def test_str(self):
        list = List()
        list.name = 'list 1'
        self.assertEqual(list.__str__(), list.name)

    @patch('mailchimper.models.List.mailchimper')
    def test_make_import_new_lists(self, mock_mailchimper):
        mock_mailchimper.lists.list.return_value = deepcopy(LIST_RESULT)
        result = List.make_import()
        self.assertIsInstance(result, dict)
        mock_mailchimper.lists.list.assert_is_called_once_with(filters=None)
        self.assertEqual(List.objects.count(), 2)
        for data in LIST_RESULT['data']:
            list_obj = List.objects.get(id=data['id'])
            for field in List._meta.get_all_field_names():
                if field in data:
                    self.assertEqual(getattr(list_obj, field), data[field])








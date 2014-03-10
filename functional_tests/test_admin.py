# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.admin.templatetags.admin_urls import admin_urlname

from mailchimper.tests.factories import AdminF, ListF
from mailchimper.models import List

from .base import FunctionalTest


class ListAdminTest(FunctionalTest):
    def setUp(self):
        self.admin = AdminF()
        self.create_pre_authenticated_session(self.admin)
        self.changelist_url = self.get_url(
            admin_urlname(List._meta, 'changelist'))

    def test_changelist_view(self):
        lists = [ListF() for i in range(0, 2)]
        print(lists)
        self.browser.get(self.changelist_url)
        import ipdb
        ipdb.set_trace()

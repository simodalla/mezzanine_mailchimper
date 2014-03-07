# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.admin import AdminSite
from django.test import TestCase

from ..admin import (ListAdmin, MemberAdmin)
from ..models import (List, Member)


class MemberAdminTest(TestCase):
    def test_for_test(self):
        MemberAdmin(Member, AdminSite)


class ListAdminTest(TestCase):
    def test_for_test(self):
        ListAdmin(List, AdminSite)

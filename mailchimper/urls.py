# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import patterns, url

from .views import ImportListView


urlpatterns = patterns(
    'mailchimper.views',
    url(r'^list/import/$', ImportListView.as_view(), name='import_list'),
)

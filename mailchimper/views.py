# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.views.generic import RedirectView

from .models import List


MAILCHIMP_LIST_FILTERS = ['list_id', 'list_name', 'from_name', 'from_email',
                          'from_subject', 'created_before', 'created_after',
                          'exact']


class ImportListView(RedirectView):
    # url = reverse(admin_urlname(List._meta, 'changelist'))
    # url = '/'
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        url = reverse(admin_urlname(List._meta, 'changelist'))
        if 'next' in self.request.GET:
            url = self.request.GET['next']
        filters = {key: self.request.GET[key]
                   for key in self.request.GET
                   if key in MAILCHIMP_LIST_FILTERS}
        List.objects.import_list(request=self.request, filters=filters)
        return url


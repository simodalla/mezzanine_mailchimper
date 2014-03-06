# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pprint

from django.core.management.base import BaseCommand

from mezzanine.conf import settings

from mailchimp import Mailchimp


class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *apps, **options):
        settings.use_editable()
        mc = Mailchimp(settings.MAILCHIMP_API_KEY)
        result_list = mc.lists.list()
        print(result_list)
        for mc_list in result_list['data']:
            result_members = mc.lists.members(mc_list['id'])
            pprint.pprint(result_members)

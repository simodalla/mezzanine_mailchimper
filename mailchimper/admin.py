# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib import admin

from .models import Member


class MemberAdmin(admin.ModelAdmin):
    list_display = ('email', 'get_object_site_link', 'get_object_admin_link',)


admin.site.register(Member, MemberAdmin)

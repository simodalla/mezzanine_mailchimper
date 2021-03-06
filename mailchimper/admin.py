# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib import admin

from .models import List, Member


class MemberAdmin(admin.ModelAdmin):
    list_display = ('email', 'get_object_site_link', 'get_object_admin_link',)


class ListAdmin(admin.ModelAdmin):
    list_display = ('id', 'webid', 'name', 'selectable')
    list_editable = ('selectable',)
    search_fields = ('id', 'name')
    list_filter = ('selectable',)


admin.site.register(List, ListAdmin)
admin.site.register(Member, MemberAdmin)

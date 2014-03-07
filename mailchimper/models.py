# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.models import TimeStamped
from mezzanine.utils.models import get_user_model
User = get_user_model()

from .managers import MemberManager, ListManager, UserMemberManager


class UserMember(User):
    mailchimper = UserMemberManager()

    class Meta:
        proxy = True


@python_2_unicode_compatible
class Member(TimeStamped):
    id = models.CharField(max_length=20, primary_key=True, editable=False)
    email = models.EmailField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = MemberManager()

    class Meta:
        verbose_name = _('member')
        verbose_name_plural = _('members')

    def __str__(self):
        return self.id

    def get_object_link(self, url):
        return ('<a href="{url}">{member.content_type.name}: {member.'
                'content_object}</a>'.format(url=url, member=self))

    def get_object_site_link(self):
        try:
            url = self.content_object.get_absolute_url()
            return self.get_object_link(url)
        except AttributeError:
            return ''
    get_object_site_link.short_description = _('site link')
    get_object_site_link.allow_tags = True

    def get_object_admin_link(self):
        url_name = admin_urlname(self.content_object._meta, 'changelist')
        url = '{url}?id={pk}'.format(url=reverse(url_name), pk=self.object_id)
        return self.get_object_link(url)
    get_object_admin_link.short_description = _('admin link')
    get_object_admin_link.allow_tags = True


@python_2_unicode_compatible
class List(TimeStamped):
    id = models.CharField(_('mailchimp id'), max_length=15, unique=True,
                          editable=False, primary_key=True)
    webid = models.IntegerField(_('mailchimp webid'), unique=True,
                                editable=False, null=True)
    name = models.CharField(_('name'), max_length=300, unique=True)
    selectable = models.BooleanField(default=False)
    members = models.ManyToManyField(Member, blank=True, null=True,
                                     verbose_name=_('members'))
    content_types = models.ManyToManyField(ContentType, blank=True, null=True)

    objects = ListManager()

    class Meta:
        ordering = ['name']
        verbose_name = _('list')
        verbose_name_plural = _('lists')

    def __str__(self):
        return self.name

    def import_members(self, content_type):
        if content_type not in self.content_types.all():
            raise ValueError('Content type {content_type} not in '
                             'content_types'.format(content_type=content_type))
        result = List.objects.mailchimper.lists.members(self.id)
        for data in result['data']:
            member, m_created, i_created = (
                Member.objects.get_or_create_by_content_type(
                    data['id'], data['email'], content_type))
        return result

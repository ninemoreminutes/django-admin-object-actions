# -*- coding: utf-8 -*-

# Python
from __future__ import unicode_literals

# Six
import six

# Django
from django.contrib import admin
from django.utils.timezone import now

# Django-Admin-Object-Actions
from admin_object_actions.admin import ModelAdminObjectActionsMixin

# Test App
from .models import TestModel
from .forms import AdminTestModelEnableForm, AdminTestModelDisableForm

if six.PY3:
    from django.utils.translation import gettext_lazy as _
else:
    from django.utils.translation import ugettext_lazy as _


def do_fail(obj, form):
    raise NotImplementedError('this action is not yet implemented')


@admin.register(TestModel)
class TestModelAdmin(ModelAdminObjectActionsMixin, admin.ModelAdmin):

    list_display = (
        'name',
        'enabled',
        'refreshed',
        'display_object_actions_list',
    )
    fields = (
        'name',
        'enabled',
        'refreshed',
        'display_object_actions_detail',
    )
    readonly_fields = (
        'enabled',
        'refreshed',
        'display_object_actions_detail',
    )
    object_actions = [
        {
            'slug': 'enable',
            'verbose_name': _('enable ✓'),
            'verbose_name_past': _('enabled ✓'),
            'form_class': AdminTestModelEnableForm,
            'fields': ('name', 'enabled', 'confirm'),
            'readonly_fields': ('name', 'enabled',),
            'permission': 'enable',
            'detail_only': True,
        },
        {
            'slug': 'disable',
            'verbose_name': _('disable'),
            'verbose_name_past': _('disabled'),
            'form_class': AdminTestModelDisableForm,
            'fieldsets': [(None, {'fields': ('name', 'enabled', 'confirm')})],
            'readonly_fields': ('name', 'enabled'),
            'permission': 'disable',
            'detail_only': True,
        },
        {
            'slug': 'refresh',
            'verbose_name': _('refresh'),
            'verbose_name_past': _('refreshed'),
            'form_method': 'GET',
            'function': 'do_refresh',
            'list_only': True,
        },
        {
            'slug': 'check',
            'verbose_name': _('check'),
            'verbose_name_past': _('checked'),
            'form_method': 'GET',
            'view': 'check_view',
            'detail_only': True,
        },
        {
            'slug': 'fail',
            'verbose_name': _('fail'),
            'verbose_name_past': _('failed'),
            'form_method': 'GET',
            'function': do_fail,
            'detail_only': True,
        },
        {
            'slug': 'restrict',
            'verbose_name': _('restrict'),
            'verbose_name_past': _('restricted'),
            'form_method': 'GET',
            'permission': 'restrict',
            'detail_only': True,
        },
    ]

    def do_refresh(self, obj, form):
        obj.refreshed = now()
        obj.save(update_fields=['refreshed'])

    def check_view(self, request, object_id, form_url='', extra_context=None, action=None):
        return self.object_action_view(request, object_id, form_url, extra_context, action)

    def has_restrict_permission(self, request, obj=None):
        return False

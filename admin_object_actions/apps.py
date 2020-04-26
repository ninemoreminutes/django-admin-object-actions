# Python
from __future__ import unicode_literals

# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AdminObjectActionsConfig(AppConfig):

    name = 'admin_object_actions'
    verbose_name = _('Admin Object Actions')

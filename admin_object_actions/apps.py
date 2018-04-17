# Django
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AdminObjectActionsConfig(AppConfig):

    name = 'admin_object_actions'
    verbose_name = _('Admin Object Actions')

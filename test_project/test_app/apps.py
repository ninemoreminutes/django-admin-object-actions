# Django
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TestAppConfig(AppConfig):

    name = 'test_project.test_app'
    verbose_name = _('Test App')

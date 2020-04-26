# Python
from __future__ import unicode_literals

# Django
from django import forms

# Django-Admin-Object-Actions
from admin_object_actions.forms import AdminObjectActionForm

# Test App
from .models import TestModel


class AdminTestModelEnableForm(AdminObjectActionForm):

    confirm = forms.BooleanField(
        required=True,
    )

    class Meta:
        model = TestModel
        fields = ()

    def do_object_action(self):
        self.instance.enabled = True
        self.instance.save(update_fields=['enabled'])


class AdminTestModelDisableForm(AdminObjectActionForm):

    confirm = forms.BooleanField(
        required=True,
    )

    class Meta:
        model = TestModel
        fields = ()

    def do_object_action(self):
        self.instance.enabled = False
        self.instance.save(update_fields=['enabled'])

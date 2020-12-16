# Python
from __future__ import unicode_literals

# Django
from django import forms


class AdminObjectActionForm(forms.ModelForm):

    def do_object_action(self):
        raise NotImplementedError('do_object_action has not been implemented')

    def save(self, commit=True):
        try:
            if hasattr(self, 'do_object_action_callable'):
                self.object_action_result = self.do_object_action_callable(self.instance, self)
            else:
                self.object_action_result = self.do_object_action()
        except Exception as e:
            self.add_error(None, str(e))
            raise
        return self.instance

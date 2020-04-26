# Python
from __future__ import unicode_literals

# Django
from django.db import models


class TestModel(models.Model):

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'enable', 'disable')

    name = models.CharField(
        max_length=100,
        unique=True,
    )
    enabled = models.BooleanField(
        default=False,
        editable=False,
    )
    refreshed = models.DateTimeField(
        null=True,
        default=None,
        editable=False,
    )

    def __str__(self):
        return self.name

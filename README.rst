|Build Status| |PyPI Version| |PyPI License| |Python Versions| |Django Versions| |Read the Docs|

Django-Admin-Object-Actions
===========================

**Django-Admin-Object-Actions** provides object-level actions in the Django
admin interface.

In contrast to the built-in admin actions, which are only applied to a list of
objects from the change list, object actions apply to a single object and can be
accessed from either the change list view or the change form view.

Each action is defined declaratively on the ``ModelAdmin`` instance and may
provide a form for additional input or validation before executing the action.

Inspired by `This Article <https://medium.com/@hakibenita/how-to-add-custom-action-buttons-to-django-admin-8d266f5b0d41>`_.

Documentation can be found at `RTFD <http://django-admin-object-actions.readthedocs.io/>`_.

It is tested against:
 * Django 1.11 (Python 2.7, 3.4, 3.5 and 3.6)
 * Django 2.0 (Python 3.4, 3.5, 3.6 and 3.7)
 * Django 2.1 (Python 3.5, 3.6 and 3.7)
 * Django 2.2 (Python 3.5, 3.6, 3.7 and 3.8)
 * Django 3.0 (Python 3.6, 3.7 and 3.8)
 * Django master/3.1 (Python 3.6, 3.7 and 3.8)


.. |Build Status| image:: http://img.shields.io/travis/ninemoreminutes/django-admin-object-actions.svg
   :target: https://travis-ci.org/ninemoreminutes/django-admin-object-actions
.. |PyPI Version| image:: https://img.shields.io/pypi/v/django-admin-object-actions.svg
   :target: https://pypi.org/project/django-admin-object-actions/
.. |PyPI License| image:: https://img.shields.io/pypi/l/django-admin-object-actions.svg
   :target: https://pypi.org/project/django-admin-object-actions/
.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/django-admin-object-actions.svg
   :target: https://pypi.org/project/django-admin-object-actions/
.. |Django Versions| image:: https://img.shields.io/pypi/djversions/django-admin-object-actions.svg
   :target: https://pypi.org/project/django-admin-object-actions/
.. |Read the Docs| image:: https://img.shields.io/readthedocs/django-admin-object-actions.svg
   :target: http://django-admin-object-actions.readthedocs.io/

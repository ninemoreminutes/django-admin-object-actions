# Python
from __future__ import unicode_literals
import functools

# Six
import six

# Django
from django.contrib.admin import helpers
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.admin.utils import unquote
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.auth import get_permission_codename
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import router, transaction
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html, format_html_join
try:
    from django.utils.http import url_has_allowed_host_and_scheme
except ImportError:
    from django.utils.http import is_safe_url as url_has_allowed_host_and_scheme
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path

# Django-CRUM
from crum import get_current_request

# Django-Admin-Object-Actions
from .forms import AdminObjectActionForm


class ModelAdminObjectActionsMixin(object):

    object_actions = []
    object_action_form_class = AdminObjectActionForm

    def get_object_actions(self, obj=None):
        object_actions = []
        for object_action in self.object_actions:
            assert isinstance(object_action, dict)
            assert object_action.get('slug')
            object_actions.append(object_action)
        return object_actions

    def get_object_action_option(self, action, option, default=None):
        for object_action in self.get_object_actions():
            if action == object_action['slug'] and option in object_action:
                return object_action[option]
        return default

    def get_object_action_view_name(self, action):
        opts = self.model._meta
        return '{}_{}_{}'.format(opts.app_label, opts.model_name, action)

    def get_object_action_verbose_name(self, request, obj, action):
        return self.get_object_action_option(action, 'verbose_name', action.title())

    def get_object_action_verbose_name_title(self, request, obj, action):
        return self.get_object_action_option(action, 'verbose_name_title', self.get_object_action_verbose_name(request, obj, action))

    def get_object_action_form(self, request, obj, action):
        form_class = self.get_object_action_option(action, 'form_class')
        if form_class is not None:
            return form_class
        fields = self.get_object_action_option(action, 'fields') or ()
        readonly_fields = self.get_object_action_readonly_fields(request, obj, action)
        fields = tuple(f for f in fields if f not in readonly_fields)
        defaults = {
            'form': self.object_action_form_class,
            'fields': fields,
            'exclude': None,
            'formfield_callback': functools.partial(self.formfield_for_dbfield, request=request),
        }
        form_class = modelform_factory(self.model, **defaults)
        callable_function = self.get_object_action_option(action, 'function', None)
        if callable_function:
            if isinstance(callable_function, six.string_types):
                callable_function = getattr(self, callable_function, getattr(obj, callable_function, None))
                assert callable_function
            setattr(form_class, 'do_object_action_callable', callable_function)
        return form_class

    def get_object_action_readonly_fields(self, request, obj, action):
        readonly_fields = self.get_object_action_option(action, 'readonly_fields')
        if readonly_fields is not None:
            return readonly_fields
        return ()

    def get_object_action_fields(self, request, obj, form, action):
        fields = self.get_object_action_option(action, 'fields')
        if fields is not None:
            return fields
        fields = list(form.base_fields)
        for field in self.get_object_action_readonly_fields(request, obj, action):
            if field not in fields:
                fields.append(field)
        return fields

    def get_object_action_fieldsets(self, request, obj, form, action):
        fieldsets = self.get_object_action_option(action, 'fieldsets')
        if fieldsets is not None:
            return fieldsets
        return [(None, {'fields': self.get_object_action_fields(request, obj, form, action)})]

    def get_object_action_form_template(self, request, obj, action):
        return self.get_object_action_option(action, 'form_template')

    def has_object_action_permission(self, request, obj, action):
        permission = self.get_object_action_option(action, 'permission', 'change')
        assert permission != 'object_action'
        has_perm_method = getattr(self, 'has_{}_permission'.format(permission), None)
        if has_perm_method:
            return has_perm_method(request, obj)
        opts = self.opts
        codename = get_permission_codename(permission, opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename), obj)

    def get_object_action_display(self, request, obj, action):
        verbose_name = self.get_object_action_verbose_name(request, obj, action)
        verbose_name = verbose_name[0].upper() + verbose_name[1:]
        view_name = self.get_object_action_view_name(action)
        href = reverse('admin:{}'.format(view_name), args=[obj.pk], current_app=self.admin_site.name)
        next_url = request.get_full_path()
        return format_html('<a class="button" href="{}?next={}">{}</a>', href, next_url, verbose_name)

    def display_object_actions(self, obj=None, list_only=False, detail_only=False):
        empty_value_display = self.get_empty_value_display()
        if not obj or not obj.pk:
            return empty_value_display
        request = get_current_request()
        actions_display = []
        for object_action in self.get_object_actions(obj):
            if list_only and object_action.get('detail_only', False):
                continue
            if detail_only and object_action.get('list_only', False):
                continue
            action = object_action['slug']
            if not self.has_object_action_permission(request, obj, action):
                continue
            actions_display.append(self.get_object_action_display(request, obj, action))
        return format_html_join(mark_safe('&nbsp;'), '{}', [(x,) for x in actions_display])
    display_object_actions.short_description = _('Object Actions')

    def display_object_actions_list(self, obj=None):
        return self.display_object_actions(obj, list_only=True)
    display_object_actions_list.short_description = _('Object Actions')

    def display_object_actions_detail(self, obj=None):
        return self.display_object_actions(obj, detail_only=True)
    display_object_actions_detail.short_description = _('Object Actions')

    def get_urls(self):
        urls = super(ModelAdminObjectActionsMixin, self).get_urls()
        object_action_urls = []
        for object_action in self.get_object_actions():
            action = object_action['slug']
            view = self.get_object_action_option(action, 'view', self.object_action_view)
            if isinstance(view, six.string_types):
                view = getattr(self, view)
            wrapped_view = functools.partial(view, action=action)
            wrapped_view = functools.update_wrapper(wrapped_view, view)
            object_action_urls.append(
                re_path(
                    r'^(?P<object_id>\S+)/{}/$'.format(action),
                    self.admin_site.admin_view(wrapped_view),
                    name=self.get_object_action_view_name(action),
                )
            )
        return object_action_urls + urls

    def get_object_action_redirect_url(self, request, obj, action, redirect_field_name='next'):
        opts = self.model._meta
        preserved_filters = self.get_preserved_filters(request)
        url = request.POST.get(redirect_field_name, request.GET.get(redirect_field_name, ''))
        if not url_has_allowed_host_and_scheme(url=url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            url = ''
        if not url:
            url = reverse('admin:{}_{}_changelist'.format(opts.app_label, opts.model_name), current_app=self.admin_site.name)
        url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, url)
        return url

    def construct_object_action_log_message(self, request, obj, form, action):
        verbose_name = self.get_object_action_verbose_name(request, obj, action)
        verbose_name_past = self.get_object_action_option(action, 'verbose_name_past', None) or verbose_name
        return '{}.'.format(verbose_name_past[0].upper() + verbose_name_past[1:])

    def construct_object_action_message(self, request, obj, form, action, exception=None):
        opts = self.model._meta
        verbose_name_past = self.get_object_action_option(action, 'verbose_name_past', _('acted upon'))
        msg_dict = {
            'name': opts.verbose_name,
            'obj': obj,
            'verbose_name_past': verbose_name_past,
            'exception': exception,
        }
        if exception:
            return format_html(
                _('The {name} "{obj}" was not {verbose_name_past}: {exception}.'),
                **msg_dict
            )
        else:
            return format_html(
                _('The {name} "{obj}" was {verbose_name_past} successfully.'),
                **msg_dict
            )

    def log_object_action(self, request, obj, message, action):
        return self.log_change(request, obj, message)

    def response_object_action(self, request, obj, form, action, exception=None):
        msg = self.construct_object_action_message(request, obj, form, action, exception)
        if exception:
            self.message_user(request, msg, messages.ERROR)
        else:
            self.message_user(request, msg, messages.SUCCESS)
        redirect_url = self.get_object_action_redirect_url(request, obj, action)
        return HttpResponseRedirect(redirect_url)

    def object_action_view(self, request, object_id, form_url='', extra_context=None, action=None):
        return self.object_action_form_view(request, object_id, form_url, extra_context, action)

    def object_action_form_view(self, request, object_id, form_url='', extra_context=None, action=None):
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._object_action_form_view(request, object_id, form_url, extra_context, action)

    def _object_action_form_view(self, request, object_id, form_url, extra_context, action):
        opts = self.model._meta
        obj = self.get_object(request, unquote(object_id))
        if not self.has_object_action_permission(request, obj, action):
            raise PermissionDenied

        if obj is None:
            return self._get_obj_does_not_exist_redirect(request, opts, object_id)

        form_class = self.get_object_action_form(request, obj, action)
        form_method = self.get_object_action_option(action, 'form_method', 'POST')
        if request.method == 'POST' or request.method == form_method:
            if form_method == 'POST':
                form = form_class(request.POST, request.FILES, instance=obj)
            else:
                form = form_class(request.GET, instance=obj)
            if form.is_valid():
                try:
                    new_object = self.save_form(request, form, change=True)
                except Exception as e:
                    return self.response_object_action(request, obj, form, action, exception=e)
                else:
                    msg = self.construct_object_action_log_message(request, obj, form, action)
                    self.log_object_action(request, new_object, msg, action)
                    return self.response_object_action(request, new_object, form, action)
        else:
            form = form_class(instance=obj)

        context = self.get_object_action_form_context(request, obj, form, action)
        context.update(extra_context or {})

        return self.render_object_action_form(request, context, obj=obj, form_url=form_url, action=action)

    def get_object_action_form_context(self, request, obj, form, action):
        opts = self.model._meta
        admin_form = helpers.AdminForm(
            form,
            self.get_object_action_fieldsets(request, obj, form, action),
            {},
            self.get_object_action_readonly_fields(request, obj, action),
            model_admin=self,
        )
        media = self.media + admin_form.media

        verbose_name = self.get_object_action_verbose_name(request, obj, action)
        verbose_name_title = self.get_object_action_verbose_name_title(request, obj, action)
        title = '{} {}'.format(verbose_name_title[0].upper() + verbose_name_title[1:], opts.verbose_name)
        return dict(
            self.admin_site.each_context(request),
            title=title,
            adminform=admin_form,
            object_id=obj.pk,
            original=obj,
            object=obj,
            is_popup=False,
            to_field=None,
            media=media,
            inline_admin_formsets=[],
            errors=helpers.AdminErrorList(form, []),
            preserved_filters=self.get_preserved_filters(request),
            object_action_slug=action,
            object_action_verbose_name=verbose_name,
        )

    def render_object_action_form(self, request, context, form_url='', obj=None, action=None):
        opts = self.model._meta
        preserved_filters = self.get_preserved_filters(request)
        form_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, form_url)
        view_on_site_url = self.get_view_on_site_url(obj)
        context.update({
            'add': False,
            'change': True,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True,  # FIXME - this should check if form or formsets have a FileField,
            'has_absolute_url': view_on_site_url is not None,
            'absolute_url': view_on_site_url,
            'form_url': form_url,
            'opts': opts,
            'content_type_id': get_content_type_for_model(self.model).pk,
            'save_as': False,
            'save_on_top': self.save_on_top,
            'to_field_var': None,
            'is_popup_var': None,
            'app_label': opts.app_label,
        })
        form_template = self.get_object_action_form_template(request, obj, action)

        request.current_app = self.admin_site.name

        return TemplateResponse(request, form_template or [
            'admin/{}/{}/object_action_form.html'.format(opts.app_label, opts.model_name),
            'admin/{}/object_action_form.html'.format(opts.app_label),
            'admin/object_action_form.html',
        ], context)

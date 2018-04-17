# Python
from __future__ import with_statement
from __future__ import unicode_literals

# Django
from django.contrib.admin.models import LogEntry
from django.contrib import messages
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


def test_object_actions_on_changelist(admin_client, test_model_instance):
    changelist_url = reverse('admin:test_app_testmodel_changelist')
    enable_url = reverse('admin:test_app_testmodel_enable', args=[test_model_instance.pk])
    disable_url = reverse('admin:test_app_testmodel_disable', args=[test_model_instance.pk])
    refresh_url = reverse('admin:test_app_testmodel_refresh', args=[test_model_instance.pk])
    response = admin_client.get(changelist_url)
    assert response.status_code == 200
    assert enable_url not in response.content.decode('utf-8')
    assert disable_url not in response.content.decode('utf-8')
    assert refresh_url in response.content.decode('utf-8')


def test_object_actions_on_changeform(admin_client, test_model_instance):
    change_url = reverse('admin:test_app_testmodel_change', args=[test_model_instance.pk])
    enable_url = reverse('admin:test_app_testmodel_enable', args=[test_model_instance.pk])
    disable_url = reverse('admin:test_app_testmodel_disable', args=[test_model_instance.pk])
    refresh_url = reverse('admin:test_app_testmodel_refresh', args=[test_model_instance.pk])
    response = admin_client.get(change_url)
    assert response.status_code == 200
    assert enable_url in response.content.decode('utf-8')
    assert disable_url in response.content.decode('utf-8')
    assert refresh_url not in response.content.decode('utf-8')


def test_object_actions_on_addform(admin_client, test_model_instance):
    add_url = reverse('admin:test_app_testmodel_add')
    response = admin_client.get(add_url)
    assert response.status_code == 200


def test_object_action_does_not_exist(admin_client):
    admin_url = reverse('admin:index')
    enable_url = reverse('admin:test_app_testmodel_enable', args=[0])
    response = admin_client.get(enable_url, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[0][0] == admin_url
    message_list = list(response.context['messages'])
    assert message_list[0].level == messages.WARNING
    assert 'doesn\'t exist' in message_list[0].message


def test_object_action_enable(admin_client, test_model_instance):
    assert LogEntry.objects.count() == 0
    assert not test_model_instance.enabled
    changelist_url = reverse('admin:test_app_testmodel_changelist')
    enable_url = reverse('admin:test_app_testmodel_enable', args=[test_model_instance.pk])
    response = admin_client.get(enable_url, follow=True)
    assert response.status_code == 200
    assert not response.redirect_chain
    response = admin_client.post(enable_url, {'confirm': 'on'}, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[0][0] == changelist_url
    message_list = list(response.context['messages'])
    assert message_list[0].level == messages.SUCCESS
    assert 'enabled' in message_list[0].message
    test_model_instance.refresh_from_db()
    assert test_model_instance.enabled
    assert LogEntry.objects.count() == 1
    log_entry = LogEntry.objects.first()
    assert 'enabled' in log_entry.change_message.lower()


def test_object_action_disable(admin_client, test_model_instance):
    assert LogEntry.objects.count() == 0
    test_model_instance.enabled = True
    test_model_instance.save(update_fields=['enabled'])
    assert test_model_instance.enabled
    change_url = reverse('admin:test_app_testmodel_change', args=[test_model_instance.pk])
    disable_url = reverse('admin:test_app_testmodel_disable', args=[test_model_instance.pk])
    disable_url = '{}?next={}'.format(disable_url, change_url)
    response = admin_client.get(disable_url, follow=True)
    assert response.status_code == 200
    assert not response.redirect_chain
    response = admin_client.post(disable_url, {}, follow=True)
    assert response.status_code == 200
    assert not response.redirect_chain
    test_model_instance.refresh_from_db()
    assert test_model_instance.enabled
    response = admin_client.post(disable_url, {'confirm': 'on'}, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[0][0] == change_url
    message_list = list(response.context['messages'])
    assert message_list[0].level == messages.SUCCESS
    assert 'disabled' in message_list[0].message
    test_model_instance.refresh_from_db()
    assert not test_model_instance.enabled
    assert LogEntry.objects.count() == 1
    log_entry = LogEntry.objects.first()
    assert 'disabled' in log_entry.change_message.lower()


def test_object_action_refresh(admin_client, test_model_instance):
    assert LogEntry.objects.count() == 0
    assert not test_model_instance.refreshed
    changelist_url = reverse('admin:test_app_testmodel_changelist')
    refresh_url = reverse('admin:test_app_testmodel_refresh', args=[test_model_instance.pk])
    response = admin_client.get(refresh_url, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[0][0] == changelist_url
    message_list = list(response.context['messages'])
    assert message_list[0].level == messages.SUCCESS
    assert 'refreshed' in message_list[0].message
    test_model_instance.refresh_from_db()
    assert test_model_instance.refreshed
    assert LogEntry.objects.count() == 1
    log_entry = LogEntry.objects.first()
    assert 'refreshed' in log_entry.change_message.lower()


def test_object_action_check(admin_client, test_model_instance):
    assert LogEntry.objects.count() == 0
    assert not test_model_instance.refreshed
    changelist_url = reverse('admin:test_app_testmodel_changelist')
    check_url = reverse('admin:test_app_testmodel_check', args=[test_model_instance.pk])
    response = admin_client.get(check_url, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[0][0] == changelist_url
    message_list = list(response.context['messages'])
    assert message_list[0].level == messages.ERROR
    assert 'not checked' in message_list[0].message
    assert LogEntry.objects.count() == 0


def test_object_action_fail(admin_client, test_model_instance):
    assert LogEntry.objects.count() == 0
    assert not test_model_instance.refreshed
    changelist_url = reverse('admin:test_app_testmodel_changelist')
    fail_url = reverse('admin:test_app_testmodel_fail', args=[test_model_instance.pk])
    response = admin_client.get(fail_url, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[0][0] == changelist_url
    message_list = list(response.context['messages'])
    assert message_list[0].level == messages.ERROR
    assert 'not failed' in message_list[0].message
    assert LogEntry.objects.count() == 0

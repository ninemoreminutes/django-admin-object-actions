# py.test
import pytest


@pytest.fixture
def apps(request, db):
    from django.apps import apps
    return apps


@pytest.fixture
def test_model(apps):
    return apps.get_model('test_app', 'TestModel')


@pytest.fixture
def test_model_instance(test_model):
    return test_model.objects.create(name='test')

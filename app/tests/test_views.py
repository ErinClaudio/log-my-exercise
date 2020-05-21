import pytest

from app import create_app

@pytest.fixture(scope='module')
def test_client():
    testing_app = create_app('testing')
    testing_client = testing_app.test_client()

    ctx = testing_app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()

def test_homepage_view(test_client):
    response = test_client.get('/')
    assert response.status_code == 302

def test_login_view(test_client):
    response = test_client.get('/auth/login')
    assert response.status_code == 200

def test_register_view(test_client):
    response = test_client.get('/auth/register')
    assert response.status_code == 200

def test_logout_view(test_client):
    response = test_client.get('/auth/logout')
    assert response.status_code == 302

def test_regular_activity_view(test_client):
    response = test_client.get('regular_activities')
    assert response.status_code == 302

def test_add_regular_activity_view(test_client):
    response = test_client.get('add_regular_activities')
    assert response.status_code == 302

def test_edit_regular_activity_view(test_client):
    response = test_client.get('/edit_regular_activity/1')
    assert response.status_code == 302

def test_delete_regular_activity_view(test_client):
    response = test_client.get('/delete_regular_activity/1')
    assert response.status_code == 302

def test_log_activity_view(test_client):
    response = test_client.get('/log_activity/1')
    assert response.status_code == 302

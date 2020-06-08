

def test_homepage_view(test_client):
    response = test_client.get('/')
    assert response.status_code == 200


def test_welcome_view(test_client):
    response = test_client.get('/welcome')
    assert response.status_code == 200


def test_index_view(test_client):
    response = test_client.get('/index')
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


def test_login_new_view(test_client):
    response = test_client.get('/auth/login_new')
    assert response.status_code == 200


def test_logout_new_view(test_client):
    response = test_client.get('/auth/logout_new')
    assert response.status_code == 302


def test_edit_profile_view(test_client):
    response = test_client.get('/edit_profile')
    assert response.status_code == 302


def test_view_profile_view(test_client):
    response = test_client.get('/user')
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


def test_delete_regular_activity_view(test_client):
    response = test_client.get('/delete_activity/1')
    assert response.status_code == 302


def test_view_all_logs(test_client):
    response = test_client.get('exercise_log')
    assert response.status_code == 302


def test_view_privacy(test_client):
    response = test_client.get('/privacy')
    assert response.status_code == 200


def test_view_privacy(test_client):
    response = test_client.get('/disclaimer')
    assert response.status_code == 200

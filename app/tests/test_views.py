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


def test_logout_view(test_client):
    response = test_client.get('/auth/logout')
    assert response.status_code == 302


def test_login_new_view(test_client):
    response = test_client.get('/auth/login_new')
    assert response.status_code == 200


def test_logout_new_view(test_client):
    response = test_client.get('/auth/logout_new')
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


def test_delete_activity_view(test_client):
    response = test_client.get('/delete_activity/1')
    assert response.status_code == 302


def test_view_all_logs(test_client):
    response = test_client.get('/exercise_log/')
    assert response.status_code == 302


def test_view_privacy(test_client):
    response = test_client.get('/support/privacy')
    assert response.status_code == 200


def test_view_disclaimer(test_client):
    response = test_client.get('/support/disclaimer')
    assert response.status_code == 200


def test_view_cookies(test_client):
    response = test_client.get('/support/cookies')
    assert response.status_code == 200


def test_view_contact_us(test_client):
    response = test_client.get('/support/contact_us')
    assert response.status_code == 200


def test_view_site_logo(test_client):
    response = test_client.get('/static/img/Titlewithlogo.png')
    assert response.status_code == 200


def test_view_about(test_client):
    response = test_client.get('/about')
    assert response.status_code == 200


def test_view_set_goal(test_client):
    response = test_client.get('/goal/set_goal')
    assert response.status_code == 302


def test_view_add_inspiration(test_client):
    response = test_client.get('/inspires/add_inspiration')
    assert response.status_code == 302


def test_view_all_inspirations(test_client):
    response = test_client.get('/inspires/inspires_list')
    assert response.status_code == 302


def test_view_edit_inspiration(test_client):
    response = test_client.get('/inspires/edit_inspiration/1')
    assert response.status_code == 302


def test_view_delete_inspiration(test_client):
    response = test_client.get('/inspires/delete_inspiration/1')
    assert response.status_code == 302


def test_view_likes_inspiration(test_client):
    response = test_client.get('/inspires/like_inspiration/1')
    assert response.status_code == 302


def test_view_detailed_inspiration(test_client):
    response = test_client.get('/inspires/detail_inspiration/1')
    assert response.status_code == 302
from unittest.mock import patch

from app.models import User
from app.tests import conftest


def test_contact_us_logged_in_user(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id
        params = dict(
            name="Bobby Chariot",
            email="bobby@chariot.email",
            description="Hello to you all",
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/support/contact_us', data=params)

        assert response.status_code == 302


def test_contact_us_anon(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    params = dict(
            name="Bobby Chariot",
            email="bobby@chariot.email",
            description="Hello to you all",
            csrf_token=test_client_csrf.csrf_token)

    response = test_client_csrf.post('/support/contact_us', data=params)

    assert response.status_code == 302


def test_contact_us_missing_email(test_client_csrf):

    params = dict(
            name="Bobby Chariot",
            email="",
            description="Hello to you all",
            csrf_token=test_client_csrf.csrf_token)

    response = test_client_csrf.post('/support/contact_us', data=params)

    assert response.status_code == 200
    assert "This field is required" in str(response.data)


def test_contact_us_missing_name(test_client_csrf):

    params = dict(
            name="",
            email="bobby@chariot.email",
            description="Hello to you all",
            csrf_token=test_client_csrf.csrf_token)

    response = test_client_csrf.post('/support/contact_us', data=params)

    assert response.status_code == 200
    assert "This field is required" in str(response.data)


def test_contact_us_missing_description(test_client_csrf):

    params = dict(
            name="Bobby Chariot",
            email="bobby@chariot.email",
            description="",
            csrf_token=test_client_csrf.csrf_token)

    response = test_client_csrf.post('/support/contact_us', data=params)

    assert response.status_code == 200
    assert "This field is required" in str(response.data)

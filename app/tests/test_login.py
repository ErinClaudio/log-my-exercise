from unittest.mock import Mock, patch

import pytest

from app import create_app, db
from app.models import User

@pytest.fixture(scope='module')
def test_client():
    testing_app = create_app('testing')
    testing_client = testing_app.test_client(use_cookies=True)

    ctx = testing_app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


@pytest.fixture(scope='module')
def init_database():
    db.drop_all()
    db.create_all()
    user = User(username="test_user")
    user.set_password("test_user")
    db.session.add(user)
    db.session.commit()

    yield db

    db.drop_all()

@patch('app.oauth')
def test_login(mock_auth0, test_client, init_database):
    mock_auth0.auth0.authorize_redirect.return_value = 200

    response = test_client.get('/auth/authorize')
    assert response.status_code == 302

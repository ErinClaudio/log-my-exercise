import pytest

from flask import abort

from app import create_app

@pytest.fixture(scope='module')
def test_client():
    testing_app = create_app('testing')

    # set-up some error routes
    @testing_app.route('/403')
    def forbidden_error():
        abort(403)

    @testing_app.route('/500')
    def internal_server_error():
        abort(500)

    testing_client = testing_app.test_client()

    ctx = testing_app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()



def test_403_forbidden(test_client):
    response = test_client.get('/403')
    assert response.status_code == 403


def test_404_not_found(test_client):
    response = test_client.get('/nothinghere')
    assert response.status_code == 404


def test_500_internal_server_error(test_client):
    response = test_client.get('/500')
    assert response.status_code == 500

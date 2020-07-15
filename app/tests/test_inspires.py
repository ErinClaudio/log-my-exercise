
from unittest.mock import patch

from app.models import User, Inspiration
from app.tests import conftest
from app import db


def test_inspiration_valid(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = dict(
            title="My Inspiration",
            url="http://youtube.com",
            instructor="Bobby Chariot",
            instructor_sex=0,
            description="A fun-filled all body workout",
            why_inspires="Run by a cheeky chappy who makes it fun",
            duration=25,
            type='1',
            likes=1,
            user_id=u.id,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/inspires/add_inspiration', data=params)
        assert response.status_code == 302
        inspires = Inspiration.query.filter_by(user_id=u.id).first()

        assert inspires is not None
        assert inspires.title == "My Inspiration"
        assert inspires.url == "http://youtube.com"
        assert inspires.instructor == "Bobby Chariot"
        assert inspires.instructor_sex == 0
        assert inspires.description == "A fun-filled all body workout"
        assert inspires.why_loved == "Run by a cheeky chappy who makes it fun"
        assert inspires.duration == 25
        assert inspires.workout_type == 1
        assert inspires.likes == 1
        assert inspires.timestamp is not None
        assert inspires.last_updated is not None


def test_inspiration_invalid(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = dict(
            url="http://youtube.com",
            instructor="Bobby Chariot",
            instructor_sex=0,
            description="A fun-filled all body workout",
            why_inspires="Run by a cheeky chappy who makes it fun",
            duration=25,
            type='1',
            likes=1,
            user_id=u.id,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/inspires/add_inspiration', data=params)
        assert response.status_code == 200
        inspires = Inspiration.query.filter_by(user_id=u.id).first()
        assert inspires is None
        #assert "Please enter a title" in str(response.data)


def test_inspiration_edit_valid(test_client_csrf, init_database, add_inspiration):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    inspiration = Inspiration.query.filter_by(user_id=u.id).first()

    assert inspiration is not None

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = dict(
            title="My Inspiration123",
            url="http://youtube.com/hello",
            instructor="Bobby Chariot12",
            instructor_sex=0,
            description="A fun-filled all body workout12",
            why_inspires="Run by a cheeky chappy who makes it funasd",
            duration=35,
            type='2',
            user_id=u.id,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.get('/inspires/edit_inspiration/{}'.format(inspiration.id))
        assert response.status_code == 200

        response = test_client_csrf.post('/inspires/edit_inspiration/{}'.format(inspiration.id), data=params)
        assert response.status_code == 302

        inspiration = Inspiration.query.filter_by(id=inspiration.id).first()
        assert inspiration is not None
        assert inspiration.title == "My Inspiration123"
        assert inspiration.url == "http://youtube.com/hello"
        assert inspiration.instructor == "Bobby Chariot12"
        assert inspiration.instructor_sex == 0
        assert inspiration.description == "A fun-filled all body workout12"
        assert inspiration.why_loved == "Run by a cheeky chappy who makes it funasd"
        assert inspiration.duration == 35
        assert inspiration.workout_type == 2
        assert inspiration.likes == 1
        assert inspiration.timestamp is not None
        assert inspiration.last_updated is not None


def test_inspiration_edit_invalid_id(test_client_csrf, init_database, add_inspiration):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    inspiration = Inspiration.query.filter_by(user_id=u.id).first()

    assert inspiration is not None

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id


        response = test_client_csrf.get('/inspires/edit_inspiration/{}'.format(123))
        assert response.status_code == 404

        inspiration = Inspiration.query.filter_by(id=inspiration.id).first()
        assert inspiration is not None


def test_inspiration_edit_invalid(test_client_csrf, init_database, add_inspiration):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    inspiration = Inspiration.query.filter_by(user_id=u.id).first()

    assert inspiration is not None

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = dict(
            title="",
            url="http://youtube.com/hello",
            instructor="Bobby Chariot12",
            instructor_sex=0,
            description="A fun-filled all body workout12",
            why_inspires="Run by a cheeky chappy who makes it funasd",
            duration=35,
            type='2',
            user_id=u.id,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.get('/inspires/edit_inspiration/{}'.format(inspiration.id))
        assert response.status_code == 200

        response = test_client_csrf.post('/inspires/edit_inspiration/{}'.format(inspiration.id), data=params)
        assert response.status_code == 200


def test_inspiration_delete_valid(test_client_csrf, init_database, add_inspiration):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    inspiration = Inspiration.query.filter_by(user_id=u.id).first()

    assert inspiration is not None

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id


        response = test_client_csrf.get('/inspires/delete_inspiration/{}'.format(inspiration.id))
        assert response.status_code == 302

        inspiration = Inspiration.query.filter_by(id=inspiration.id).first()
        assert inspiration is None


def test_inspiration_delete_invalid_id(test_client_csrf, init_database, add_inspiration):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.get('/inspires/delete_inspiration/{}'.format(123))
        assert response.status_code == 404


def test_likes_own_inspiration(test_client_csrf, init_database, add_inspiration):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    inspiration = Inspiration.query.filter_by(user_id=u.id).first()

    assert inspiration is not None
    assert inspiration.likes == 1

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.get('/inspires/like_inspiration/{}'.format(inspiration.id))
        assert response.status_code == 302

        inspiration = Inspiration.query.filter_by(id=inspiration.id).first()
        assert inspiration is not None
        assert inspiration.likes == 1  # cannot like an inspiration you have created


def test_likes_different_inspiration_(test_client_csrf, init_database, add_inspiration):
    user2 = User(username="USER_2", email="USER_2@email.com")
    user2.set_password("PASSWORD")
    db.session.add(user2)
    db.session.commit()
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    inspiration = Inspiration.query.filter_by(user_id=u.id).first()

    assert inspiration is not None
    assert inspiration.likes == 1

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = user2.id
        current_user.return_value.get_id.return_value = user2.id

        response = test_client_csrf.get('/inspires/like_inspiration/{}'.format(inspiration.id))
        assert response.status_code == 302

        inspiration = Inspiration.query.filter_by(id=inspiration.id).first()
        assert inspiration is not None
        assert inspiration.likes == 2


def test_likes_inspiration_invalid_id(test_client_csrf, init_database, add_inspiration):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.get('/inspires/like_inspiration/{}'.format(123))
        assert response.status_code == 404


def test_inspires_list(test_client_csrf, init_database, add_inspiration):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.get('/inspires/inspires_list')
        assert response.status_code == 200


def test_detailed_inspiration_valid(test_client_csrf, init_database, add_inspiration):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    inspiration = Inspiration.query.filter_by(user_id=u.id).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.get('/inspires/detail_inspiration/{}'.format(inspiration.id))
        assert response.status_code == 200

        assert inspiration.description in str(response.data)
        assert inspiration.url in str(response.data)
        assert str(inspiration.duration) in str(response.data)
        assert "edit_inspiration_link" in str(response.data)
        assert "delete_inspiration_link" in str(response.data)


def test_detailed_inspiration_invalid(test_client_csrf, init_database, add_inspiration):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.get('/inspires/detail_inspiration/{}'.format(123))
        assert response.status_code == 404

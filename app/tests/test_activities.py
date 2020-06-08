from datetime import datetime

from unittest.mock import patch

from app.models import User, Activity, RegularActivity
from app.tests import conftest


def test_create_activity_no_local_time(test_client_csrf, init_database, add_regular_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.get('/log_activity/'+str(regular_activity.id))
        assert response.status_code == 302
        activity = Activity.query.filter_by(user_id=u.id).first()
        assert activity is not None
        assert activity.type == regular_activity.type
        assert activity.title == regular_activity.title
        assert activity.description == regular_activity.description
        assert activity.duration == regular_activity.duration
        assert activity.local_timestamp == activity.timestamp


def test_create_activity_local_time(test_client_csrf, init_database, add_regular_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        local_time = datetime.utcnow()
        params = {'local_time': int(local_time.timestamp())}
        response = test_client_csrf.get('/log_activity/'+str(regular_activity.id), query_string=params)
        assert response.status_code == 302
        activity = Activity.query.filter_by(user_id=u.id).first()
        assert activity is not None
        assert activity.type == regular_activity.type
        assert activity.title == regular_activity.title
        assert activity.description == regular_activity.description
        assert activity.duration == regular_activity.duration
        assert (local_time - activity.local_timestamp).total_seconds() < 1


def test_create_activity_invalid_id(test_client_csrf, init_database, add_regular_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        local_time = datetime.utcnow()
        params = {'local_time': int(local_time.timestamp())}
        response = test_client_csrf.get('/log_activity/' + str(102), query_string=params)
        assert response.status_code == 404


def test_delete_activity(test_client_csrf, init_database, add_regular_activity, add_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    activity = Activity.query.filter_by(user_id=u.id).first()

    assert activity is not None

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.get('/delete_activity/' + str(activity.id))
        assert response.status_code == 200
        assert "Deleted" in str(response.data)
        activity = Activity.query.filter_by(user_id=u.id).first()
        assert activity is None


def test_delete_activity_invalid_id(test_client_csrf, init_database, add_regular_activity, add_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    activity = Activity.query.filter_by(user_id=u.id).first()

    assert activity is not None

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.get('/delete_activity/' + str(102))
        assert response.status_code == 404
        activity = Activity.query.filter_by(user_id=u.id).first()
        assert activity is not None


def test_create_regular_activity(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id
        params = dict(
            title="Some Exercise",
            description="A description",
            activity_type=1,
            duration=29,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/add_regular_activities', data=params)

        assert response.status_code == 302

        activity = RegularActivity.query.filter_by(user_id=u.id).first()

        assert activity is not None
        assert activity.duration == params['duration']
        assert activity.title == params['title']
        assert activity.type == params['activity_type']
        assert activity.description == params['description']
        assert activity.time is not None


def test_edit_regular_activity(test_client_csrf, init_database, add_regular_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id
        params = dict(
            title="A new Exercise",
            description="A new description",
            activity_type=2,
            duration=100,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/edit_regular_activity/'+str(regular_activity.id), data=params)

        assert response.status_code == 302

        load_regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()

        assert load_regular_activity is not None
        assert load_regular_activity.duration == params['duration']
        assert load_regular_activity.title == params['title']
        assert load_regular_activity.type == params['activity_type']
        assert load_regular_activity.description == params['description']
        assert load_regular_activity.time is not None


def test_edit_regular_activity_load(test_client_csrf, init_database, add_regular_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.get('/edit_regular_activity/' + str(regular_activity.id))

        assert response.status_code == 200
        assert "Regular Activity" in str(response.data)
        assert "23" in str(response.data)


def test_add_regular_activity_invalid_title(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id
        params = dict(
            title="",
            description="A description",
            activity_type=1,
            duration=29,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/add_regular_activities', data=params)

        assert response.status_code == 200
        regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()
        assert regular_activity is None


def test_add_regular_activity_invalid_exercise_type(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id
        params = dict(
            title="a title",
            description="A description",
            duration=29,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/add_regular_activities', data=params)

        assert response.status_code == 200
        regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()
        assert regular_activity is None


def test_add_regular_activity_invalid_duration(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id
        params = dict(
            title="a title",
            description="A description",
            activity_type=1,
            duration=-1,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/add_regular_activities', data=params)

        assert response.status_code == 200
        regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()
        assert regular_activity is None


def test_delete_regular_activity(test_client_csrf, init_database, add_regular_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.get('/delete_regular_activity/' + str(regular_activity.id))

        assert response.status_code == 302
        regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()
        assert regular_activity is None


def test_regular_activities(test_client_csrf, init_database, add_regular_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.get('regular_activities')

        assert response.status_code == 200
        assert "Regular Activity" in str(response.data)
        assert "23" in str(response.data)


def test_exercise_log(test_client_csrf, init_database, add_regular_activity, add_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.get('exercise_log')

        assert response.status_code == 200
        assert "Regular Activity" in str(response.data)
        assert "23" in str(response.data)

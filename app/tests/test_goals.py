import time

from unittest.mock import patch

from app.models import User, Goal
from app.tests import conftest


def test_goal_valid_frequency(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        # duration_activity_type = form.duration_activity_type.data, duration = form.duration.data,
        # distance_activity_type = form.distance_activity_type.data, distance = form.distance.data,

        params = dict(
            title="My Exercise",
            motivation="Why am i motivated to do this",
            acceptance_criteria="My acceptance criteria",
            reward="how will i reward myself",
            frequency=5,
            frequency_activity_type=1,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/goal/set_goal', data=params)
        assert response.status_code == 302
        goal = Goal.query.filter_by(user_id=u.id).first()

        assert goal is not None
        assert goal.title == "My Exercise"
        assert goal.motivation == "Why am i motivated to do this"
        assert goal.acceptance_criteria == "My acceptance criteria"
        assert goal.reward == "how will i reward myself"
        assert goal.frequency == 5
        assert goal.frequency_activity_type == 1
        assert goal.duration is None
        assert goal.duration_activity_type is None
        assert goal.distance is None
        assert goal.distance_activity_type is None
        assert goal.timestamp is not None
        assert goal.last_updated is not None
        assert goal.completed is None


def test_goal_valid_duration(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        # distance_activity_type = form.distance_activity_type.data, distance = form.distance.data,

        params = dict(
            title="My Exercise",
            motivation="Why am i motivated to do this",
            acceptance_criteria="My acceptance criteria",
            reward="how will i reward myself",
            duration=55,
            duration_activity_type=3,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/goal/set_goal', data=params)
        assert response.status_code == 302
        goal = Goal.query.filter_by(user_id=u.id).first()

        assert goal is not None
        assert goal.title == "My Exercise"
        assert goal.motivation == "Why am i motivated to do this"
        assert goal.acceptance_criteria == "My acceptance criteria"
        assert goal.reward == "how will i reward myself"
        assert goal.duration == 55
        assert goal.duration_activity_type == 3
        assert goal.frequency is None
        assert goal.frequency_activity_type is None
        assert goal.distance is None
        assert goal.distance_activity_type is None
        assert goal.timestamp is not None
        assert goal.last_updated is not None
        assert goal.completed is None


def test_goal_valid_distance(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = dict(
            title="My Exercise",
            motivation="Why am i motivated to do this",
            acceptance_criteria="My acceptance criteria",
            reward="how will i reward myself",
            distance=20,
            distance_activity_type=4,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/goal/set_goal', data=params)
        assert response.status_code == 302
        goal = Goal.query.filter_by(user_id=u.id).first()

        assert goal is not None
        assert goal.title == "My Exercise"
        assert goal.motivation == "Why am i motivated to do this"
        assert goal.acceptance_criteria == "My acceptance criteria"
        assert goal.reward == "how will i reward myself"
        assert goal.distance == 20
        assert goal.distance_activity_type == 4
        assert goal.frequency is None
        assert goal.frequency_activity_type is None
        assert goal.duration is None
        assert goal.duration_activity_type is None
        assert goal.timestamp is not None
        assert goal.last_updated is not None
        assert goal.completed is None


def test_goal_valid_twoentries(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = dict(
            title="My Exercise",
            motivation="Why am i motivated to do this",
            acceptance_criteria="My acceptance criteria",
            reward="how will i reward myself",
            distance=20,
            distance_activity_type=4,
            duration=120,
            duration_activity_type=-1,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/goal/set_goal', data=params)
        assert response.status_code == 302
        goal = Goal.query.filter_by(user_id=u.id).first()

        assert goal is not None
        assert goal.title == "My Exercise"
        assert goal.motivation == "Why am i motivated to do this"
        assert goal.acceptance_criteria == "My acceptance criteria"
        assert goal.reward == "how will i reward myself"
        assert goal.distance == 20
        assert goal.distance_activity_type == 4
        assert goal.frequency is None
        assert goal.frequency_activity_type is None
        assert goal.duration == 120
        assert goal.duration_activity_type == -1
        assert goal.timestamp is not None
        assert goal.last_updated is not None
        assert goal.completed is None


def test_goal_invalid_no_frequency(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = dict(
            title="My Exercise",
            motivation="Why am i motivated to do this",
            acceptance_criteria="My acceptance criteria",
            reward="how will i reward myself",
            distance_activity_type=4,
            frequency_activity_type=-1,
            duration_activity_type=-1,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/goal/set_goal', data=params)
        assert response.status_code == 200
        goal = Goal.query.filter_by(user_id=u.id).first()

        assert goal is None
        assert "Please enter a frequency, duration or distance" in str(response.data)


def test_goal_invalid_frequency(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = dict(
            title="My Exercise",
            motivation="Why am i motivated to do this",
            acceptance_criteria="My acceptance criteria",
            reward="how will i reward myself",
            frequency=2.3,  # only integers are valid
            distance_activity_type=4,
            frequency_activity_type=-1,
            duration_activity_type=-1,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/goal/set_goal', data=params)
        assert response.status_code == 200
        goal = Goal.query.filter_by(user_id=u.id).first()

        assert goal is None
        assert "Not a valid integer value" in str(response.data)


def test_goal_invalid_duration(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = dict(
            title="My Exercise",
            motivation="Why am i motivated to do this",
            acceptance_criteria="My acceptance criteria",
            reward="how will i reward myself",
            duration=2.3,  # only integers are valid
            distance_activity_type=4,
            frequency_activity_type=-1,
            duration_activity_type=-1,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/goal/set_goal', data=params)
        assert response.status_code == 200
        goal = Goal.query.filter_by(user_id=u.id).first()

        assert goal is None
        assert "Not a valid integer value" in str(response.data)


def test_goal_invalid_distance(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = dict(
            title="My Exercise",
            motivation="Why am i motivated to do this",
            acceptance_criteria="My acceptance criteria",
            reward="how will i reward myself",
            distance=2.3,  # only integers are valid
            distance_activity_type=4,
            frequency_activity_type=-1,
            duration_activity_type=-1,
            csrf_token=test_client_csrf.csrf_token)

        response = test_client_csrf.post('/goal/set_goal', data=params)
        assert response.status_code == 200
        goal = Goal.query.filter_by(user_id=u.id).first()

        assert goal is None
        assert "Not a valid integer value" in str(response.data)


def test_edit_goal(test_client_csrf, init_database, add_goal):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = dict(
            title="My Exercise 1",
            motivation="Why am i motivated to do this 1",
            acceptance_criteria="My acceptance criteria 1",
            reward="how will i reward myself 1",
            distance=23,
            frequency="",
            distance_activity_type=3,
            frequency_activity_type=-1,
            duration_activity_type=-1,
            csrf_token=test_client_csrf.csrf_token)

        goal = Goal.query.filter_by(user_id=u.id).first()
        assert goal is not None

        response = test_client_csrf.get('/goal/edit_goal/{}'.format(goal.id))
        assert response.status_code == 200
        # make the changes to this goal and check the data saved is as expected
        time.sleep(1)
        response = test_client_csrf.post('/goal/edit_goal/{}'.format(goal.id), data=params)
        assert response.status_code == 302
        goal = Goal.query.filter_by(id=goal.id).first()

        assert goal is not None
        assert goal.title == "My Exercise 1"
        assert goal.motivation == "Why am i motivated to do this 1"
        assert goal.acceptance_criteria == "My acceptance criteria 1"
        assert goal.reward == "how will i reward myself 1"
        assert goal.distance == 23
        assert goal.distance_activity_type == 3
        assert goal.frequency is None
        assert goal.frequency_activity_type == -1
        assert goal.duration is None
        assert goal.duration_activity_type == -1
        assert goal.timestamp is not None
        assert goal.last_updated is not None
        assert goal.timestamp != goal.last_updated
        assert goal.completed is None


def test_delete_goal(test_client_csrf, init_database, add_goal):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        goal = Goal.query.filter_by(user_id=u.id).first()
        assert goal is not None

        response = test_client_csrf.get('/goal/delete_goal/{}'.format(goal.id))

        assert response.status_code == 302
        goal = Goal.query.filter_by(user_id=u.id).first()
        assert goal is None

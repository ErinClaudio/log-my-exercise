import pytest

from flask import abort

from app import create_app, db
from app.models import User, RegularActivity, Activity


# define some test data to be used in tests
TEST_USER_USERNAME='test_user'
TEST_USER_PASSWORD='test_password'

TEST_REGULAR_ACTIVITY1 = RegularActivity(
    type=1,
    title='Regular Activity',
    description="Some description",
    duration=23)


@pytest.fixture(scope='module')
def test_client():
    """
    sets up a client to use in the tests
    :return:
    :rtype:
    """
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


@pytest.fixture(scope='module')
def init_database():
    """
    sets up the database ready for the tests
    creates an initial test user
    :return:
    :rtype:
    """
    db.drop_all()
    db.create_all()
    user = User(username=TEST_USER_USERNAME)
    user.set_password(TEST_USER_PASSWORD)
    db.session.add(user)
    db.session.commit()

    yield db

    db.drop_all()


@pytest.fixture(scope='function')
def add_regular_activity():
    """
    adds a regular activity to the database linked to the test user
    :return:
    :rtype:
    """
    u = User.query.filter_by(username='test_user').first()
    activity = RegularActivity(type=1,
                               title='Regular Activity',
                               user_id=u.id,
                               description="Some description",
                               duration=23)
    db.session.add(activity)
    db.session.commit()

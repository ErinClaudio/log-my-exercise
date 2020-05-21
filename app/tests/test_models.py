import pytest

from app import create_app, db
from app.models import User, Activity, RegularActivity

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


def test_user_model(test_client, init_database):
    assert User.query.count() == 1


def test_regular_activity(test_client, init_database):
    u = User.query.filter_by(username='test_user').first()
    activity = RegularActivity(type=1,
                               title='Regular Activity',
                               user_id=u.id,
                               description="Some description",
                               duration=23)
    db.session.add(activity)
    db.session.commit()

    load_activity = RegularActivity.query.filter_by(user_id=u.id).first()
    assert activity.type == load_activity.type
    assert activity.title == load_activity.title
    assert activity.description == load_activity.description
    assert activity.duration == load_activity.duration

    assert RegularActivity.query.filter_by(user_id=u.id).count() == 1


def test_daily_activity(test_client, init_database):
    # create a regular activity and use this to
    # create the new activity
    # link to the test user created
    u = User.query.filter_by(username='test_user').first()
    regular_activity = RegularActivity(type=1,
                                       title='Regular Activity',
                                       user_id=u.id,
                                       description="Some description",
                                       duration=23)
    db.session.add(regular_activity)
    activity = regular_activity.create_activity()
    db.session.add(activity)
    db.session.commit()
    assert activity.type == regular_activity.type
    assert activity.title == regular_activity.title
    assert activity.description == regular_activity.description
    assert activity.duration == regular_activity.duration
    assert activity.user_id == regular_activity.user_id

    assert Activity.query.filter_by(user_id=u.id).count() == 1

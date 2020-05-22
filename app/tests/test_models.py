

from app import db
from app.models import User, Activity, RegularActivity
from app.tests import conftest


def test_user_model(test_client, init_database):
    assert User.query.count() == 1


def test_user_repr(test_client, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    assert "User" in repr(u)


def test_regular_activity(test_client, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
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


def test_regular_activity_repr(test_client, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    load_activity = RegularActivity.query.filter_by(user_id=u.id).first()
    assert "Activity" in repr(load_activity)


def test_daily_activity(test_client, init_database, add_regular_activity):
    # create a regular activity and use this to
    # create the new activity
    # link to the test user created
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()
    activity = regular_activity.create_activity()
    db.session.add(activity)
    db.session.commit()
    assert activity.type == regular_activity.type
    assert activity.title == regular_activity.title
    assert activity.description == regular_activity.description
    assert activity.duration == regular_activity.duration
    assert activity.user_id == regular_activity.user_id

    assert Activity.query.filter_by(user_id=u.id).count() == 1

    assert "Regular Activity" in repr(activity)

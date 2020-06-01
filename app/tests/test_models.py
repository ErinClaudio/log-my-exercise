from datetime import datetime, timedelta

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
    assert "Activity" in repr(load_activity)


def test_daily_activity_local_time(test_client, init_database, add_regular_activity):
    # create a regular activity and use this to
    # create the new activity
    # link to the test user created
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()
    activity = regular_activity.create_activity()
    local_time = datetime.utcnow() - timedelta(hours=3)
    activity.local_timestamp = local_time

    db.session.add(activity)
    db.session.commit()

    load_activity = Activity.query.filter_by(user_id=u.id).first()
    assert Activity.query.filter_by(user_id=u.id).count() == 1

    assert activity.type == load_activity.type
    assert activity.title == load_activity.title
    assert activity.description == load_activity.description
    assert activity.duration == load_activity.duration
    assert activity.user_id == load_activity.user_id
    assert activity.local_timestamp == load_activity.local_timestamp
    assert activity.timestamp == load_activity.timestamp

    assert "Regular Activity" in repr(activity)


from datetime import datetime, timedelta

from app import db
from app.models import User, Activity, RegularActivity, StravaAthlete
from app.tests import conftest


def test_user_model(test_client, init_database):
    assert User.query.count() == 1


def test_user_repr(test_client, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    assert "User" in repr(u)
    assert "User" in str(u)


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
    assert "Activity" in str(load_activity)


def test_daily_activity_local_time_present(test_client, init_database, add_regular_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()
    activity = regular_activity.create_activity()
    local_time = datetime.utcnow() - timedelta(hours=3)
    activity.set_local_time(local_time.timestamp(), 'America/Chicago')

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
    assert load_activity.iso_timestamp is not None
    assert activity.timestamp == load_activity.timestamp

    assert "Regular Activity" in repr(activity)
    assert "Regular Activity" in str(activity)


def test_daily_activity_no_local_time_present(test_client, init_database, add_regular_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()
    activity = regular_activity.create_activity()
    activity.set_local_time(tz='America/Chicago')

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
    assert load_activity.iso_timestamp is not None
    assert activity.timestamp == load_activity.timestamp
    assert load_activity.local_timestamp == load_activity.timestamp # timestamps are the same as none provided

    assert "Regular Activity" in repr(activity)
    assert "Regular Activity" in str(activity)


def test_daily_activity_no_tz_present(test_client, init_database, add_regular_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()
    activity = regular_activity.create_activity()
    activity.set_local_time()

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
    assert load_activity.iso_timestamp is not None
    assert activity.timestamp == load_activity.timestamp
    assert load_activity.local_timestamp == load_activity.timestamp # timestampes are the same as none provided

    assert "Regular Activity" in repr(activity)
    assert "Regular Activity" in str(activity)


def test_strava_athlete(test_client, init_database):
    # create a strava athlete
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    current_time = datetime.utcnow()
    strava_athlete = StravaAthlete(user_id=u.id,
                                   athlete_id=123,
                                   scope="read",
                                   access_token="ABCDEF",
                                   access_token_expires_at=100000,
                                   access_token_expires_in=100,
                                   refresh_token="ZXCVB",
                                   created_date=current_time,
                                   last_updated=current_time,
                                   is_active=1)
    db.session.add(strava_athlete)
    db.session.commit()

    load_strava_athlete = StravaAthlete.query.filter_by(user_id=u.id).first()
    assert StravaAthlete.query.filter_by(user_id=u.id).count() == 1

    assert load_strava_athlete.athlete_id == strava_athlete.athlete_id
    assert load_strava_athlete.scope == strava_athlete.scope
    assert load_strava_athlete.access_token == strava_athlete.access_token
    assert load_strava_athlete.access_token_expires_at == strava_athlete.access_token_expires_at
    assert load_strava_athlete.access_token_expires_in == strava_athlete.access_token_expires_in
    assert load_strava_athlete.refresh_token == strava_athlete.refresh_token
    assert load_strava_athlete.created_date == strava_athlete.created_date
    assert load_strava_athlete.last_updated == strava_athlete.last_updated
    assert load_strava_athlete.is_active == strava_athlete.is_active

    assert "StravaAthlete" in repr(load_strava_athlete)
    assert "StravaAthlete" in str(load_strava_athlete)

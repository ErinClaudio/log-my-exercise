from datetime import datetime, timedelta

from app import db
from app.models import User, Activity, RegularActivity, StravaAthlete, Goal, Inspiration
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
                               distance=2,
                               duration=23)
    db.session.add(activity)
    db.session.commit()

    load_activity = RegularActivity.query.filter_by(user_id=u.id).first()
    assert activity.type == load_activity.type
    assert activity.title == load_activity.title
    assert activity.description == load_activity.description
    assert activity.duration == load_activity.duration
    assert activity.distance == load_activity.distance

    assert RegularActivity.query.filter_by(user_id=u.id).count() == 1
    assert "Activity" in repr(load_activity)
    assert "Activity" in str(load_activity)


def test_daily_activity_local_time_present(test_client, init_database, add_regular_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    regular_activity = RegularActivity.query.filter_by(user_id=u.id).first()
    activity = regular_activity.create_activity()
    local_time = datetime.utcnow() - timedelta(hours=3)
    activity.set_local_time(local_time, 'America/Chicago')

    db.session.add(activity)
    db.session.commit()

    load_activity = Activity.query.filter_by(user_id=u.id).first()
    assert Activity.query.filter_by(user_id=u.id).count() == 1

    assert activity.type == load_activity.type
    assert activity.title == load_activity.title
    assert activity.description == load_activity.description
    assert activity.duration == load_activity.duration
    assert activity.distance == load_activity.distance
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
    assert load_activity.local_timestamp is not None

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
    assert load_activity.local_timestamp == load_activity.timestamp  # timestampes are the same as none provided

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


def test_goal(test_client, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    current_time = datetime.utcnow()
    goal = Goal(title="My Exercise",
                motivation="Why am i motivated to do this",
                acceptance_criteria="My acceptance criteria",
                reward="how will i reward myself",
                frequency=5,
                frequency_activity_type=1,
                timestamp=current_time,
                last_updated=current_time,
                user_id=u.id)

    db.session.add(goal)
    db.session.commit()

    load_goal = Goal.query.filter_by(user_id=u.id).first()
    assert Goal.query.filter_by(user_id=u.id).count() == 1

    assert load_goal.title == goal.title
    assert load_goal.motivation == goal.motivation
    assert load_goal.acceptance_criteria == goal.acceptance_criteria
    assert load_goal.reward == goal.reward
    assert load_goal.frequency == goal.frequency
    assert load_goal.frequency_activity_type == goal.frequency_activity_type
    # ignore microseconds when comparing the timestamps

    assert "Goal" in repr(load_goal)
    assert "Goal" in str(load_goal)


def test_inspirations(test_client, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    inspiration = Inspiration(title='My Inspiration',
                              workout_type=1,
                              url='http://youtube.com',
                              instructor='Bobby Chariot',
                              instructor_sex=0,
                              description='My favourite workout. Brings up a sweat. Fun too as the instructor is funny and makes me smile',
                              duration=25,
                              why_loved='The isntructor has so much energy and enthusiasm. It lifts my spirits',
                              likes=1,
                              user_id=u.id)

    db.session.add(inspiration)
    db.session.commit()

    load_inspiration = Inspiration.query.filter_by(user_id=u.id).first()
    assert Inspiration.query.filter_by(user_id=u.id).count() == 1

    assert load_inspiration.title == inspiration.title
    assert load_inspiration.workout_type == inspiration.workout_type
    assert load_inspiration.url == inspiration.url
    assert load_inspiration.instructor == inspiration.instructor
    assert load_inspiration.instructor_sex == inspiration.instructor_sex
    assert load_inspiration.description == inspiration.description
    assert load_inspiration.duration == inspiration.duration
    assert load_inspiration.why_loved == inspiration.why_loved
    assert load_inspiration.likes == inspiration.likes

    assert "Inspiration" in repr(load_inspiration)
    assert "Inspiration" in str(load_inspiration)

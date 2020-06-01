import json
from datetime import datetime

from app import db
from app.models import User, StravaAthlete
from app.tests import conftest
from app.auth import strava
from app.services import strava as ss


def test_strava_athlete_create(test_client, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    authorize_details = json.loads(conftest.STRAVA_RESPONSE_EXAMPLE)
    scope = 'activity:write'
    strava_athlete = ss.create_strava_athlete(authorize_details, u.id, scope)

    assert strava_athlete.athlete_id == 123456
    assert strava_athlete.scope == scope
    assert strava_athlete.access_token == 'd188074a'
    assert strava_athlete.access_token_expires_at == conftest.EXPIRES_AT_SECS
    assert strava_athlete.access_token_expires_in == 21390
    assert strava_athlete.refresh_token == '767bdc6899'


def test_strava_athlete_model(test_client, init_database):
    # create a regular activity and use this to
    # create the new activity
    # link to the test user created
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    strava_athlete = StravaAthlete.query.filter_by(user_id=u.id).first()
    assert strava_athlete is None
    authorize_details = json.loads(conftest.STRAVA_RESPONSE_EXAMPLE)
    scope = 'activity:write'
    strava_athlete = ss.create_strava_athlete(authorize_details, u.id, scope)
    print(type(strava_athlete.access_token_expires_at))

    db.session.add(strava_athlete)
    db.session.commit()

    load_strava_athlete = StravaAthlete.query.filter_by(user_id=u.id).first()
    assert strava_athlete.user_id == load_strava_athlete.user_id
    assert strava_athlete.athlete_id == load_strava_athlete.athlete_id
    assert strava_athlete.scope == load_strava_athlete.scope
    assert strava_athlete.access_token == load_strava_athlete.access_token
    assert strava_athlete.access_token_expires_at == load_strava_athlete.access_token_expires_at
    assert strava_athlete.access_token_expires_in == load_strava_athlete.access_token_expires_in
    assert strava_athlete.refresh_token == load_strava_athlete.refresh_token
    assert strava_athlete.last_updated == load_strava_athlete.last_updated

    assert "StravaAthlete" in repr(strava_athlete)


def test_refresh_access_token(test_client, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    authorize_details = json.loads(conftest.STRAVA_RESPONSE_EXAMPLE)
    scope = 'activity:write'
    strava_athlete = ss.create_strava_athlete(authorize_details, u.id, scope)

    db.session.add(strava_athlete)
    db.session.commit()
    # as a dummy token has been written with an expiry date in the future then the strava API shoudl not be called
    # and the same access token is returned
    # new_token = ss.refresh_access_token(u.id)

    # assert new_token == authorize_details['ACCESS_TOKEN']
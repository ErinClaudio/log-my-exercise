import json
import os

from unittest.mock import Mock, patch

from app import db
from app.models import User, StravaAthlete, Activity
from app.tests import conftest
from app.services import strava as ss
from app.api import strava as strava_api


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

    with patch('app.services.strava.OAuth2Session') as mock_oauth:

        authorize_details = json.loads(conftest.STRAVA_RESPONSE_EXAMPLE)
        scope = 'activity:write'
        strava_athlete = ss.create_strava_athlete(authorize_details, u.id, scope)

        db.session.add(strava_athlete)
        db.session.commit()

        # mock the refresh_token call
        new_tokens = json.loads(conftest.STRAVA_REFRESH_EXAMPLE)
        mock_oauth.return_value = Mock()
        mock_oauth.return_value.refresh_token.return_value = new_tokens
        new_token = ss.refresh_access_token(u.id)

        assert new_token is not None
        assert new_token == new_tokens['access_token']


def test_create_activity(test_client, init_database, add_strava_athlete, add_activity):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    a = Activity.query.filter_by(user_id=u.id).first()
    mock_refresh_token_patcher = patch('app.services.strava.refresh_access_token')
    # need to mock the refresh token method inside the service
    mock_oauth = mock_refresh_token_patcher.start()
    mock_oauth.return_value.refresh_token = "token"

    # then mock the requests call to Strava
    mock_requests_patched = patch('app.services.strava.requests.post')
    mock_requests = mock_requests_patched.start()
    mock_requests.return_value.status_code = 200

    status = ss.create_activity(a.id)
    assert status == 200


def test_create_activity_invalid_id(test_client, init_database, add_strava_athlete, add_activity):
    mock_refresh_token_patcher = patch('app.services.strava.refresh_access_token')
    # need to mock the refresh token method inside the service
    mock_oauth = mock_refresh_token_patcher.start()
    mock_oauth.return_value.refresh_token = "token"

    # then mock the requests call to Strava
    mock_requests_patched = patch('app.services.strava.requests.post')
    mock_requests = mock_requests_patched.start()
    mock_requests.return_value.status_code = 200

    status = ss.create_activity(-2)
    assert status == 400


def test_deauthorize_athlete(test_client, init_database, add_strava_athlete):
    # tests the strava de-authorization works
    user = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    athlete = StravaAthlete.query.filter_by(user_id=user.id).first()

    assert athlete.is_active == 1

    ss.deauthorize_athlete(athlete.athlete_id)
    assert athlete.is_active == 0


def test_deauthorize_athlete_invalid_id(test_client, init_database, add_strava_athlete):
    # tests the strava de-authorization rejects an invalid id
    status = ss.deauthorize_athlete(-1)
    assert not status


def test_deauthorize_athlete_view(test_client, init_database, add_strava_athlete):
    # call the view to deauthorize
    # simulate the POST that Strava API will send through
    user = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    athlete = StravaAthlete.query.filter_by(user_id=user.id).first()

    updates = {'authorized': 'false'}
    # requests.post(url, json=my_data)
    assert athlete.is_active == 1
    response = test_client.post('/api/strava/deauthorize', json={
        'object_type': 'athlete',
        'object_id': athlete.athlete_id,
        'aspect_type': 'update',
        'updates': updates,
        'owner_id': athlete.athlete_id,
        'subscription_id': 1
    }, follow_redirects=True)

    assert response.status_code == 200

    athlete = StravaAthlete.query.filter_by(user_id=user.id).first()
    assert athlete.is_active == 0


def test_deauthorize_athlete_view_invalid_id(test_client, init_database, add_strava_athlete):
    # call the view to deauthorize
    # simulate the POST that Strava API will send through
    updates = {'authorized': 'false'}

    response = test_client.post('/api/strava/deauthorize', json={
        'object_type': 'athlete',
        'object_id': -1,
        'aspect_type': 'update',
        'updates': updates,
        'owner_id': -1,
        'subscription_id': 1
    }, follow_redirects=True)
    # still get 200 even if invalid id
    assert response.status_code == 200


def test_deauthorize_athlete_view_invalid_data(test_client, init_database, add_strava_athlete):
    # call the view to deauthorize
    # simulate the POST that Strava API will send through
    updates = {'authorized111': 'false'}
    response = test_client.get('', follow_redirects=True)

    response = test_client.post('/api/strava/deauthorize', json={
        'object_type': 'athlete',
        'object_id': -1,
        'aspect_type': 'update',
        'updates': updates,
        'owner_id': -1,
        'subscription_id': 1
    }, follow_redirects=True)
    # missing data so expect a 400
    assert response.status_code == 400


def test_deauthorize_athlete_view_invalid_object(test_client, init_database, add_strava_athlete):
    # call the view to deauthorize
    # simulate the POST that Strava API will send through
    updates = {'authorized111': 'false'}

    response = test_client.post('/api/strava/deauthorize', json={
        'object_type': 'ghghg',
        'object_id': -1,
        'aspect_type': 'update',
        'updates': updates,
        'owner_id': -1,
        'subscription_id': 1
    }, follow_redirects=True)
    # missing data so expect a 400
    assert response.status_code == 400


def test_deauthorize_athlete_view_invalid_auth_value(test_client, init_database, add_strava_athlete):
    # call the view to deauthorize
    # simulate the POST that Strava API will send through
    updates = {'authorized': 'hfghg'}

    response = test_client.post('/api/strava/deauthorize', json={
        'object_type': 'athlete',
        'object_id': -1,
        'aspect_type': 'update',
        'updates': updates,
        'owner_id': -1,
        'subscription_id': 1
    }, follow_redirects=True)
    # expect a 400 if the authorized has the wrong value
    assert response.status_code == 400


def test_is_valid_strava_challenge_params(test_client):
    token = os.getenv('STRAVA_VERIFY_TOKEN')

    is_valid = strava_api.is_valid_strava_challenge_params('subscribe', 'a challenge', token)

    assert is_valid is True


def test_is_valid_strava_challenge_params_invalid_key(test_client):
    token = os.getenv('STRAVA_VERIFY_TOKEN')

    is_valid = strava_api.is_valid_strava_challenge_params('subscribe12', 'a challenge', token)

    assert is_valid is False


def test_is_valid_strava_challenge_params_invalid_challenge(test_client):
    token = os.getenv('STRAVA_VERIFY_TOKEN')

    is_valid = strava_api.is_valid_strava_challenge_params('subscribe12', '', token)

    assert is_valid is False


def test_is_valid_strava_challenge_params_invalid_token(test_client):
    token = os.getenv('STRAVA_VERIFY_TOKEN')

    is_valid = strava_api.is_valid_strava_challenge_params('subscribe12', 'some challenge', token+'SDF')

    assert is_valid is False


def test_subscription_validation_request(test_client):
    token = os.getenv('STRAVA_VERIFY_TOKEN')

    params = {'hub.mode': 'subscribe', 'hub.challenge': '15f7d1a91c1f40f8a748fd134752feb3', 'hub.verify_token':token}
    response = test_client.get('/api/strava/deauthorize', query_string=params)

    assert response.status_code == 200
    assert response.is_json is True
    response_json = response.get_json()
    assert response_json['hub.challenge'] == '15f7d1a91c1f40f8a748fd134752feb3'


def test_subscription_validation_request_invalid(test_client):
    token = os.getenv('STRAVA_VERIFY_TOKEN')

    params = {'hub.mode': 'subscribe123', 'hub.challenge': 'my_challenge', 'hub.verify_token':token}
    response = test_client.get('/api/strava/deauthorize', query_string=params)

    assert response.status_code == 400
    assert response.is_json is True
    response_json = response.get_json()
    assert response_json['error'] == 'invalid params'


def test_strava_callback_access_denied(test_client, init_database,):
    # fails as user is not logged in and so no current_user
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = {'code': 'ABCDEF', 'scope': 'activity:read', 'error': 'access_denied'}
        response = test_client.get('/auth/strava_callback', query_string=params, follow_redirects=True)
        assert "Strava: Access Denied" in str(response.data)


def test_strava_callback_invalid_write_scope(test_client, init_database,):
    # fails as user is not logged in and so no current_user
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = {'code': 'ABCDEF', 'scope': 'activity:read', 'error': ''}
        response = test_client.get('/auth/strava_callback', query_string=params, follow_redirects=True)
        assert "Please ensure you agree to sharing your data" in str(response.data)


def test_strava_callback_invalid_read_scope(test_client, init_database,):
    # fails as user is not logged in and so no current_user
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = {'code': 'ABCDEF', 'scope': 'activity:write', 'error': ''}
        response = test_client.get('/auth/strava_callback', query_string=params, follow_redirects=True)
        assert "Please ensure you agree to sharing your data" in str(response.data)


def test_strava_callback_invalid_code(test_client, init_database,):
    # fails as user is not logged in and so no current_user
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        params = {'code': '', 'scope': 'activity:write', 'error': ''}
        response = test_client.get('/auth/strava_callback', query_string=params, follow_redirects=True)
        assert "Invalid response" in str(response.data)


def test_user_strava_deauthorize(test_client, init_database, add_strava_athlete):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    athlete = StravaAthlete.query.filter_by(user_id=u.id).first()

    assert athlete.is_active == 1
    mock_refresh_token_patcher = patch('app.services.strava.refresh_access_token')
    # need to mock the refresh token method inside the service
    mock_oauth = mock_refresh_token_patcher.start()
    mock_oauth.return_value.refresh_token = "token"

    # then mock the requests call to Strava
    mock_requests_patched = patch('app.services.strava.requests.post')
    mock_requests = mock_requests_patched.start()
    mock_requests.return_value.status_code = 200

    status = ss.tell_strava_deauth(athlete)
    assert status is True

    athlete = StravaAthlete.query.filter_by(user_id=u.id).first()
    assert athlete.is_active == 0


def test_user_strava_deauthorize_fail(test_client, init_database, add_strava_athlete):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    athlete = StravaAthlete.query.filter_by(user_id=u.id).first()

    assert athlete.is_active == 1
    mock_refresh_token_patcher = patch('app.services.strava.refresh_access_token')
    # need to mock the refresh token method inside the service
    mock_oauth = mock_refresh_token_patcher.start()
    mock_oauth.return_value.refresh_token = "token"

    # then mock the requests call to Strava
    mock_requests_patched = patch('app.services.strava.requests.post')
    mock_requests = mock_requests_patched.start()
    mock_requests.return_value.status_code = 400

    status = ss.tell_strava_deauth(athlete)
    assert status is False

    athlete = StravaAthlete.query.filter_by(user_id=u.id).first()
    assert athlete.is_active == 1


def test_user_strava_refresh_token_scope_not_correct(test_client, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('authlib.integrations.flask_client.OAuth') as mock_oauth:
        with patch('flask_login.utils._get_user') as current_user:
            current_user.return_value.id = u.id
            current_user.return_value.get_id.return_value = u.id

            mock_oauth.return_value.authorize_access_token = conftest.STRAVA_RESPONSE_EXAMPLE
            params = {'code': 'ABCDEF', 'scope': 'activity:write,activity:write', 'error': ''}
            response = test_client.get('/auth/strava_callback', query_string=params, follow_redirects=True)

            assert "Please ensure you agree to sharing" in str(response.data)


def test_user_strava_refresh_token_new(test_client, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    athlete = StravaAthlete.query.filter_by(user_id=u.id).first()

    assert athlete is None

    with patch('app.oauth.strava.authorize_access_token') as mock_oauth:
        with patch('flask_login.utils._get_user') as current_user:
            current_user.return_value.id = u.id
            current_user.return_value.get_id.return_value = u.id
            mock_oauth.return_value = conftest.STRAVA_RESPONSE_EXAMPLE_AS_DICT
            params = {'code': 'ABCDEF', 'scope': 'activity:read,activity:write', 'error': ''}
            response = test_client.get('/auth/strava_callback', query_string=params, follow_redirects=True)

            # this should be valid and so a new strava athlete is created
            athlete = StravaAthlete.query.filter_by(user_id=u.id).first()
            assert athlete is not None
            assert athlete.is_active == 1
            assert athlete.athlete_id == 123456
            assert "Thank you" in str(response.data)

def test_user_strava_refresh_token_existing(test_client, init_database, add_strava_athlete):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    athlete = StravaAthlete.query.filter_by(user_id=u.id).first()

    assert athlete is not None

    with patch('app.oauth.strava.authorize_access_token') as mock_oauth:
        with patch('flask_login.utils._get_user') as current_user:
            current_user.return_value.id = u.id
            current_user.return_value.get_id.return_value = u.id
            mock_oauth.return_value = conftest.STRAVA_RESPONSE_EXAMPLE_AS_DICT
            params = {'code': 'ABCDEF', 'scope': 'activity:read,activity:write', 'error': ''}
            response = test_client.get('/auth/strava_callback', query_string=params, follow_redirects=True)

            # this should be valid and so a new strava athlete is created
            athlete = StravaAthlete.query.filter_by(user_id=u.id).first()
            assert athlete is not None
            assert athlete.is_active == 1
            assert athlete.athlete_id == 123456

            assert "Thank you" in str(response.data)

def test_strava_authorize(test_client, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client.get('/auth/strava_authorize')
        assert response.status_code == 302
        assert "www.strava.com" in response.headers['Location']


def test_strava_integration_on(test_client_csrf, init_database):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.post('/auth/update_strava_integration', data=dict(
            is_integrated=True,
            csrf_token=test_client_csrf.csrf_token))
        assert response.status_code == 302
        assert "/auth/strava_authorize" in response.headers['Location']


def test_strava_integration_already_on(test_client_csrf, init_database, add_strava_athlete):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()

    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.post('/auth/update_strava_integration', data=dict(
            is_integrated=True,
            csrf_token=test_client_csrf.csrf_token))
        assert response.status_code == 302
        assert "/user" in response.headers['Location']


def test_strava_integration_off(test_client_csrf, init_database, add_strava_athlete):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    athlete = StravaAthlete.query.filter_by(user_id=u.id).first()
    athlete.is_active = 0
    db.session.commit()


    with patch('flask_login.utils._get_user') as current_user:
        current_user.return_value.id = u.id
        current_user.return_value.get_id.return_value = u.id

        response = test_client_csrf.post('/auth/update_strava_integration', data=dict(
            is_integrated=True,
            csrf_token=test_client_csrf.csrf_token))
        assert response.status_code == 302
        assert "/strava_authorize" in response.headers['Location']


def test_strava_turn_integration_off(test_client_csrf, init_database, add_strava_athlete):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    athlete = StravaAthlete.query.filter_by(user_id=u.id).first()

    assert athlete.is_active == 1
    with patch('app.services.strava.requests.post') as mock_requests:
        mock_requests.return_value.status_code = 200
        with patch('app.services.strava.OAuth2Session') as mock_oauth:
            new_tokens = json.loads(conftest.STRAVA_REFRESH_EXAMPLE)
            mock_oauth.return_value = Mock()
            mock_oauth.return_value.refresh_token.return_value = new_tokens
            with patch('flask_login.utils._get_user') as current_user:
                current_user.return_value.id = u.id
                current_user.return_value.get_id.return_value = u.id

                response = test_client_csrf.post('/auth/update_strava_integration', data=dict(
                    csrf_token=test_client_csrf.csrf_token))

                assert response.status_code == 302

                print(str(response.data))
                athlete = StravaAthlete.query.filter_by(user_id=u.id).first()
                assert athlete.is_active == 0


def test_strava_turn_integration_off_bad_strava(test_client_csrf, init_database, add_strava_athlete):
    u = User.query.filter_by(username=conftest.TEST_USER_USERNAME).first()
    athlete = StravaAthlete.query.filter_by(user_id=u.id).first()

    assert athlete.is_active == 1
    with patch('app.services.strava.requests.post') as mock_requests:
        mock_requests.return_value.status_code = 401
        with patch('app.services.strava.OAuth2Session') as mock_oauth:
            new_tokens = json.loads(conftest.STRAVA_REFRESH_EXAMPLE)
            mock_oauth.return_value = Mock()
            mock_oauth.return_value.refresh_token.return_value = new_tokens
            with patch('flask_login.utils._get_user') as current_user:
                current_user.return_value.id = u.id
                current_user.return_value.get_id.return_value = u.id

                response = test_client_csrf.post('/auth/update_strava_integration', data=dict(
                    csrf_token=test_client_csrf.csrf_token))

                assert response.status_code == 302
                athlete = StravaAthlete.query.filter_by(user_id=u.id).first()
                assert athlete.is_active == 1

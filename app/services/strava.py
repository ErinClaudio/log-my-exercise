import os
from datetime import datetime

import requests
from authlib.integrations.requests_client import OAuth2Session
from flask import current_app

from app import db
from app.main import routes
from app.models import StravaAthlete, Activity, StravaEvent
from config import app_config

STRAVA_ACTIVITIES_LOOKUP = {1: 'Workout', 2: 'Yoga', 3: 'Ride', 4: 'Run', 5: 'Walk', 6: 'Swim'}

def create_strava_athlete(authorize_details, user_id, scope):
    """

    :param authorize_details: a dictionary containing information about the athlete.
    :type authorize_details: a dictionary with keys athlete, access_token, expires_at, expires_in, refresh_token
                athlete is a dictionary also with a key of id
    :param user_id: the user mapping to this strava athlete
    :type user_id: int
    :param scope: the parts of the strava api that the user has granted this app permission to
    :type scope: string
    :return: a StravaAthlete set to the values in the provided dictionary
    :rtype: StravaAthlete
    """
    strava_athlete = StravaAthlete(user_id=user_id,
                                   athlete_id=int(authorize_details['athlete']['id']),
                                   scope=scope,
                                   access_token=authorize_details['access_token'],
                                   access_token_expires_at=int(authorize_details['expires_at']),
                                   access_token_expires_in=int(authorize_details['expires_in']),
                                   refresh_token=authorize_details['refresh_token'],
                                   last_updated=datetime.utcnow())
    return strava_athlete


def refresh_access_token(user_id):
    """
    Refreshes the strava API access token if it's expired
    :param user_id: identifier for the user
    :type user_id: int
    :return: a valid access token
    :rtype: string
    """
    # Access tokens expire six hours after they are created, so they must be refreshed in order
    # for an application to maintain access to a user’s resources.
    # Every time you get a new access token, we return a new refresh token as well.
    # If you need to make a request, we recommend checking to see if the
    # short-lived access token has expired. If it has expired,
    # request a new short-lived access token with the last received refresh token

    # refresh_token is A OAuth2Token object (a dict too).
    # Need a key of 'access_token' set to the value
    # refresh_token(url, refresh_token=None, body='', auth=None, headers=None, **kwargs)

    # POST https://www.strava.com/oauth/token
    # client_id, client_secret, grant_type='refresh_token', refresh_token

    # retrieve the user's tokens from the database
    # if it has expired, then get a new one and update the database
    # otherwise, use the current one
    # return the token
    strava_athlete = StravaAthlete.query.filter_by(user_id=user_id).first()
    my_token = {'refresh_token': strava_athlete.refresh_token,
                'access_token': strava_athlete.access_token,
                'expires_at': strava_athlete.access_token_expires_at,
                'expires_in': strava_athlete.access_token_expires_in}

    my_config = app_config[os.getenv('FLASK_CONFIG')]()

    oauth_session = OAuth2Session(my_config.STRAVA_CLIENT_ID,
                                  my_config.STRAVA_CLIENT_SECRET,
                                  authorization_endpoint=my_config.STRAVA_CLIENT_DOMAIN + '/oauth/authorize',
                                  token_endpoint=my_config.STRAVA_CLIENT_DOMAIN + '/oauth/token',
                                  token=my_token,
                                  grant_type='refresh_token')
    new_token = oauth_session.refresh_token(
        url=my_config.STRAVA_CLIENT_DOMAIN + '/oauth/token',
        client_id=my_config.STRAVA_CLIENT_ID,
        client_secret=my_config.STRAVA_CLIENT_SECRET)

    # save it to the database assuming there is no error
    if new_token is not None:
        strava_athlete.access_token = new_token['access_token']
        strava_athlete.access_token_expires_at = int(new_token['expires_at'])
        strava_athlete.access_token_expires_in = int(new_token['expires_in'])
        strava_athlete.refresh_token = new_token['refresh_token']
        strava_athlete.last_updated = datetime.utcnow()
        db.session.commit()
        return new_token['access_token']

    # must be an error to log this
    current_app.logger.error('Failed to refresh the token')
    return None


def construct_strava_activity_data(activity):
    """
    constructs the dictionary of data fields to send to strava when creating an activity
    :param activity: the activity to be sent to Strava
    :type activity: Activity
    :return: a Dictionary containing the data formatted to the Strava API
    :rtype:
    """
    # if the timestamp has been saved then use this over converting the other one
    # issues with server tz so better to use the timestamp at the point the activity record was created
    if activity.iso_timestamp:
        local_time = activity.iso_timestamp
    else:
        local_time = activity.local_timestamp.isoformat()

    data = {'name': activity.title,
            'type': STRAVA_ACTIVITIES_LOOKUP[activity.type],
            'start_date_local': local_time,
            'elapsed_time': activity.duration * 60,  # need to convert to seconds, stored in db as minutes
            'description': activity.description}

    if activity.distance is not None and activity.distance > 0:
        data['distance'] = activity.distance * 1000  # Strava API requires distance in m, stored in db as km

    return data


def create_activity(activity_id):
    """
    creates an activity in Strava
    :param activity_id: the identifier of the activity to create
    :type activity_id: int
    :return: a status code indicating whether the activity was created successfully or not
    :rtype: int
    """

    # get the activity
    activity = Activity.query.filter_by(id=activity_id).first()

    if activity:
        # now get a valid token for the associated user
        access_token = refresh_access_token(user_id=activity.user_id)
        if access_token is None:
            # an error must have occurred
            current_app.logger.error('Cannot save activity {} to Strava as unable to refresh token'.format(activity_id))
            # let the app continue on as error has been logged
            return 200

        url = 'https://www.strava.com/api/v3/activities'
        headers = {'Authorization': 'Bearer {}'.format(access_token)}

        data = construct_strava_activity_data(activity)
        response = requests.post(url, headers=headers, data=data)
        strava_athlete = StravaAthlete.query.filter_by(user_id=activity.user_id).first()
        log_strava_event(strava_athlete.athlete_id, "Activity")

        # check the response, if there has been an error then need to log this
        if response.status_code != 200:
            current_app.logger.error('Strava Status code: {}'.format(response.status_code))
            current_app.logger.error('Strava Response: {}'.format(response.json))
        return response.status_code
    # log an error if the activity doesn't exist but allow app to continue on
    current_app.logger.error('Activity {} does not exist'.format(activity_id))
    return 200


def deauthorize_athlete(athlete_id):
    """
    deauthorize the strava athlete so the integration won't be used
    :param athlete_id: the athlete
    :type athlete_id: int
    :param event_time: the time it was called
    :type event_time: int
    :return: bopolean indicating success or not
    :rtype:
    """
    athlete = StravaAthlete.query.filter_by(athlete_id=athlete_id).first()
    if athlete:
        athlete.is_active = 0
        athlete.last_updated = datetime.utcnow()
        db.session.commit()
        log_strava_event(athlete_id, "Deauthorize")
        return True

    current_app.logger.error('Athlete {} does not exist'.format(athlete_id))
    return False


def log_strava_event(athlete_id, action):
    """
    Logs that the Strava API is called for this athlete in some way.
    :param athlete_id: strava athlete_id
    :type athlete_id: int
    :param event: one of 'Deauthorize', 'Authorize', 'Activity'
    :type event: string
    :return:
    :rtype:
    """
    strava_event = StravaEvent(athlete_id=athlete_id, action=action, timestamp=datetime.utcnow())
    db.session.add(strava_event)
    db.session.commit()


def tell_strava_deauth(strava_athlete):
    """
    sends a command to strava informing them of the deauthorisation of this user
    :param strava_athlete: the strava athlete
    :type strava_athlete:
    :return: True if Strava acknowledged success, False otherwise
    :rtype: boolean
    """
    access_token = refresh_access_token(user_id=strava_athlete.user_id)

    url = 'https://www.strava.com/oauth/deauthorize'
    params = {'access_token': access_token}

    response = requests.post(url, params=params)

    if response.status_code == 200:
        # all okay
        log_strava_event(strava_athlete.athlete_id, "Deauthorize from site")
        deauthorize_athlete(strava_athlete.athlete_id)
        return True
    # should not get here, something wrong from Strava
    current_app.logger.error('Strava Status code: {}'.format(response.status_code))
    current_app.logger.error('Strava response: {}'.format(response.json))
    return False

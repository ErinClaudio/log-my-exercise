import os

from flask import request, jsonify

from app.api import bp
from app.services import strava as ss


def is_valid_strava_challenge_params(mode, challenge, token):
    """
    validate the params provided by strave
    :param mode: always subscribe
    :type mode:
    :param challenge: the random string to echo back
    :type challenge:
    :param token: the token, should match the one provided to Strava
    :type token:
    :return:
    :rtype:
    """
    if mode == "subscribe" and \
            len(challenge) > 0 and \
            token == os.getenv("STRAVA_VERIFY_TOKEN"):
        return True
    return False


def subscription_validation(my_request):
    """
    responds back to Strava's request to create a subscription with
    their webhooks
    :param mode: the mode. Will always be subscribe
    :type mode: string
    :param challenge: the random string to echo back
    :type challenge: string
    :param token: the provided token
    :type token: string
    :return:
    :rtype:
    """
    # need to check the parameters
    mode = my_request.args.get('hub.mode')
    challenge = my_request.args.get('hub.challenge')
    token = my_request.args.get('hub.verify_token')

    if is_valid_strava_challenge_params(mode, challenge, token):
        # can now respond back
        # send a 200 and a application/json message of
        # { “hub.challenge”:”15f7d1a91c1f40f8a748fd134752feb3” }
        return 200, jsonify({'hub.challenge': challenge})
    return 400, jsonify({'error': 'invalid params'})


@bp.route('/strava/deauthorize', methods=['GET', 'POST'])
def strava_deauthorize():
    """
    callback function used by strava when an athlete deauthorizes the integration
    needs to be set-up in Strava as a hook
    :return:
    :rtype:
    """
    # object_type = "athlete"
    # object_id - the athlete's strava id
    # aspect_type - one of "create", "update" or "delete"
    # updates - is a hash -  for app deauthorizations, always an "authorized":"false"
    # owner_id - the athlete's ID
    # subscription_id - the push subscription id receiving the evnet
    # event_time - the time the event occurred

    # Subscription callback endpoint must acknowledge the POST of each new event with a status code of 200 OK
    # within two seconds. Event pushes are retried (up to a total of three attempts) if a 200 is not returned.
    # If your application needs to do more processing of the received information, it should do so asynchronously.

    # read the data from the POST form
    # call a function to update the athlete
    # return 200 status

    # if this method was called via a GET then its validating the callback address
    # handle this differently
    if request.method == 'GET':
        status, response = subscription_validation(request)
        return response, status

    data = request.get_json(force=True)
    object_type = data['object_type']
    athlete = int(data['owner_id'])
    updates = data['updates']

    if object_type and object_type == 'athlete' and updates\
            and 'authorized' in updates:
        # athlete has deauthorized the app
        if updates['authorized'] == 'false':
            status = ss.deauthorize_athlete(athlete)
        # if status is anything other than True, need to log this as an error and retry
            return '', 200

    # return something about badly formed POST
    return '', 400

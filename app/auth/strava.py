from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required

from app import db, oauth
from app.auth import bp
from app.models import StravaAthlete
from app.services import strava as ss


@bp.route('login_strava')
def strava_login():
    return render_template('auth/strava_access.html', title='Strava Sign-Up')


@bp.route('/strava_authorize')
@login_required
def strava_authorize():
    """
    Calls strava to allow this application access to the strava profile of the user
    :return: redirects to the auth0 website
    :rtype:
    """

    redirect_uri = url_for('auth.strava_callback', _external=True)

    return oauth.strava.authorize_redirect(redirect_uri)


@bp.route('/strava_callback')
def strava_callback():
    """
    is called back by strava when the user has either provided or rejected access
    by this application to their strava profile
    :return:
    :rtype:
    """
    # need to get the scope details to check the user has given correct permissions
    # to this app
    # resp = oauth.strava.get('scope')
    # will be called back with a scope query string parameter
    scope = request.args.get('scope')
    code = request.args.get('code')
    error = request.args.get('error')

    if error == 'access_denied':
        flash('Strava: Access Denied')
        return redirect(url_for('main.user', username=current_user.username))

    if 'activity:read' in scope and 'activity:write' in scope:
        access_token = oauth.strava.authorize_access_token(code=code,
                                                           grant_type='authorization_code',
                                                           client_id=oauth.strava.client_id,
                                                           client_secret=oauth.strava.client_secret)
        # authorize_details = access_token.json()
        # will need to save this access_token against the user
        # will then need to refresh it when it needs to be used against the API
        # see if we already have a strava record for this user
        # if so, then we can update it, otherwise, we create it
        strava_athlete = StravaAthlete.query.filter_by(user_id=current_user.get_id()).first()
        if not strava_athlete:
            # create the record
            strava_athlete = ss.create_strava_athlete(access_token, current_user.get_id(), scope)
            db.session.add(strava_athlete)
            db.session.commit()
        else:
            # update the record with the new details
            new_strava_athlete = ss.create_strava_athlete(access_token, current_user.get_id(), scope)
            strava_athlete.scope = new_strava_athlete.scope
            strava_athlete.access_token = new_strava_athlete.access_token
            strava_athlete.access_token_expires_at = new_strava_athlete.access_token_expires_at
            strava_athlete.access_token_expires_in = new_strava_athlete.access_token_expires_in
            strava_athlete.refresh_token = new_strava_athlete.refresh_token
            strava_athlete.last_updated = new_strava_athlete.last_updated
            db.session.commit()
        print("access token expires at", strava_athlete.access_token_expires_at)
        print("expires in", strava_athlete.access_token_expires_in / 60)
    else:
        flash('Please ensure you agree to sharing your data with LogMyExercise.')
        return redirect(url_for('main.user', username=current_user.username))

    flash('Thank you for granting access to your Strava details.')
    return redirect(url_for('main.user', username=current_user.username))

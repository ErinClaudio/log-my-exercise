from flask import flash, redirect, url_for, request
from flask_login import current_user, login_required


from app import db, oauth
from app.auth import bp
from app.models import StravaAthlete
from app.services import strava as ss
from app.auth.forms import StravaIntegrationForm


@bp.route('/strava_authorize')
@login_required
def strava_authorize():
    """
    Calls strava to allow this application access to the strava profile of the user
    :return: redirects to the strava website
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
        return redirect(url_for('main.user'))

    if len(code) == 0:
        # error as strava should return a code
        flash('Strava: Invalid response')
        return redirect(url_for('main.user'))

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
            print(access_token)
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
            strava_athlete.is_active = 1
            db.session.commit()
    else:
        flash('Please ensure you agree to sharing your data with LogMyExercise.')
        return redirect(url_for('main.user'))

    flash('Thank you for granting access to your Strava details.')
    ss.log_strava_event(strava_athlete.athlete_id, 'Authorize')
    return redirect(url_for('main.user'))


def user_strava_deauthorize(strava_athlete):
    """
    User doesn't want to integrate with Strava anymore
    Assumes there is a Strava record as this user is already integrated with Strava
    :return:
    :rtype:
    """
    result = ss.tell_strava_deauth(strava_athlete)
    if result:
        flash('LogMyExercise will no longer update Strava on your behalf')
    else:
        flash('There has been an error')

    return redirect(url_for('main.user'))


@bp.route('/update_strava_integration', methods=['POST'])
@login_required
def update_strava_integration():
    """
    updates the Strava integration based on user preferences
    will either end the user to strava to authorise integration or
    ask the user to de-authorise it
    :return:
    :rtype:
    """
    form = StravaIntegrationForm()

    is_integrated = form.is_integrated.data
    # compare this to the value saved previously
    # if it has changed then make the update
    # either turn on or turn off
    strava_athlete = StravaAthlete.query.filter_by(user_id=current_user.get_id()).first()

    if strava_athlete:
        # check to see if the new response is different or not
        if is_integrated:
            if strava_athlete.is_active == 0:
                return redirect(url_for('auth.strava_authorize'))
        else:
            print("deauth the athlete")
            if strava_athlete.is_active == 1:
                # deauthorize the athlete
                user_strava_deauthorize(strava_athlete)
    else:
        # no record
        if is_integrated:
            # need to go through the approval process
            return redirect(url_for('auth.strava_authorize'))

    # if we are here then nothing to do
    flash("Changes have been saved")
    return redirect(url_for('main.user'))

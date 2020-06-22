from datetime import datetime

from flask import render_template, flash, redirect, url_for, current_app
from flask import request
from flask_login import current_user, login_required
from sqlalchemy import desc

from app import db
from app.auth.forms import StravaIntegrationForm
from app.main import ACTIVITIES_LOOKUP, ICONS_LOOKUP
from app.main import bp
from app.main.forms import ActivityForm
from app.models import Activity, RegularActivity, User, StravaAthlete
from app.services import strava, charting
from app.services.charting import ACTIVITY_COLOR_LOOKUP


@bp.before_request
def before_request():
    """
    Tracks the date/time the user last logged in and used the application
    :return:
    :rtype:
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/welcome', methods=['GET'])
def welcome():
    """
    shows the welcome page
    :return:
    :rtype:
    """
    return render_template('welcome.html', title='Welcome')


@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """
    shows the user's regular activities in order for them to log it
    :return:
    :rtype:
    """
    if current_user.is_authenticated:
        activities = RegularActivity.query.filter_by(user_id=current_user.get_id()).all()

    form = ActivityForm()
    # passed the id of the regular activity
    # need to get all the details of the regular activity
    # and use that to save the activity

    # need to pass in the URL to send the one-off activity to the template
    if form.validate_on_submit():
        activity = Activity(title=form.title.data, description=form.description.data,
                            type=int(form.activity_type.data),
                            duration=form.duration.data,
                            timestamp=datetime.utcnow(),
                            distance=form.distance.data,
                            user_id=current_user.get_id())
        activity.set_local_time('', form.user_tz.data)
        db.session.add(activity)
        db.session.commit()
        flash('Well done on completing {} today'.format(activity.title))
        # need to clear the form once it's been saved successfully
        return redirect(url_for('main.index'))

    return render_template('index.html', title='Home', form=form, regular_activities=activities,
                           icons=ICONS_LOOKUP, colors=ACTIVITY_COLOR_LOOKUP,
                           form_url=url_for('main.index'))


@bp.route('/user')
@login_required
def user():
    """
    shows the user's profile
    :return:
    :rtype:
    """
    my_user = User.query.filter_by(id=current_user.get_id()).first_or_404()

    strava_athlete = StravaAthlete.query.filter_by(user_id=current_user.get_id(), is_active=1).first()
    is_strava = True
    if not strava_athlete:
        is_strava = False

    form = StravaIntegrationForm()
    form.is_integrated.data = is_strava
    return render_template('auth/user.html', user=my_user, is_strava=is_strava, strava_form=form)


@bp.route('/regular_activities', methods=['GET', 'POST'])
@login_required
def regular_activities():
    """
    shows the user's regular activities
    :return:
    :rtype:
    """
    activities = RegularActivity.query.filter_by(user_id=current_user.get_id()).all()
    return render_template('activity/regularactivities.html', user=user, regular_activities=activities,
                           activities_lookup=ACTIVITIES_LOOKUP, icons=ICONS_LOOKUP)


@bp.route('/add_regular_activities', methods=['GET', 'POST'])
@login_required
def add_regular_activity():
    """
    creates a new regular activity
    :return:
    :rtype:
    """
    form = ActivityForm()
    is_add_regular_activity = True
    if form.validate_on_submit():
        activity = RegularActivity(title=form.title.data, description=form.description.data,
                                   type=int(form.activity_type.data), duration=form.duration.data,
                                   time=datetime.utcnow(),
                                   distance=form.distance.data,
                                   user_id=current_user.get_id())
        db.session.add(activity)
        db.session.commit()
        flash('Your regular activity is recorded')
        return redirect(url_for('main.regular_activities'))
    return render_template('activity/edit_regularactivity.html', user=user, form=form,
                           is_add_regular_activity=is_add_regular_activity, icons=ICONS_LOOKUP)


@bp.route('/edit_regular_activity/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def edit_regular_activity(activity_id):
    """
    edits a regular activity
    :param activity_id: activity to edit
    :type activity_id: int
    :return:
    :rtype:
    """
    is_add_regular_activity = False
    regular_activity = RegularActivity.query.filter_by(user_id=current_user.get_id(), id=activity_id).first_or_404()
    form = ActivityForm(obj=regular_activity)
    if form.validate_on_submit():
        regular_activity.title = form.title.data
        regular_activity.description = form.description.data
        regular_activity.type = int(form.activity_type.data)
        regular_activity.duration = form.duration.data
        regular_activity.time = datetime.utcnow()
        regular_activity.distance = form.distance.data
        db.session.commit()
        flash('Saved changes to your regular activity')
        return redirect(url_for('main.regular_activities'))

    form.title.data = regular_activity.title
    form.description.data = regular_activity.description
    print(regular_activity.type)
    form.activity_type.data = str(regular_activity.type)
    form.duration.data = regular_activity.duration
    return render_template('activity/edit_regularactivity.html', is_add_regular_activity=is_add_regular_activity,
                           user=user, form=form, title="Edit Regular Activity")


@bp.route('/delete_regular_activity/<int:activity_id>', methods=['GET'])
@login_required
def delete_regular_activity(activity_id):
    """
    deletes a regular activity
    :param activity_id: activity to delete
    :type activity_id: int
    :return:
    :rtype:
    """
    regular_activity = RegularActivity.query.filter_by(user_id=current_user.get_id(), id=activity_id).first_or_404()
    db.session.delete(regular_activity)
    db.session.commit()
    flash('Deleted the regular activity')

    return redirect(url_for('main.regular_activities'))


@bp.route('/log_activity/<int:activity_id>', methods=['GET'])
@login_required
def log_activity(activity_id):
    """
    logs that a particular exercise has been done
    :param activity_id: regular activity to log
    :type activity_id: int
    :return:
    :rtype:
    """
    regular_activity = RegularActivity.query.filter_by(user_id=current_user.get_id(), id=activity_id).first_or_404()

    activity = regular_activity.create_activity()
    activity.set_local_time(request.args.get('local_time'), request.args.get('tz'))
    db.session.add(activity)
    db.session.commit()

    if current_app.config['CALL_STRAVA_API']:
        # first check to see if this user is integrated with strava or not
        strava_athlete = StravaAthlete.query.filter_by(user_id=current_user.get_id(), is_active=1).first()
        if strava_athlete:
            strava.create_activity(activity.id)

    flash('Well done on completing {} today'.format(regular_activity.title))
    return redirect(url_for('main.index'))


@bp.route('/exercise_log/', defaults={'offset': 0}, methods=['GET'])
@bp.route('/exercise_log/<int:offset>', methods=['GET'])
@bp.route('/exercise_log/<int:offset>/<string:sum_by>', methods=['GET'])
@login_required
def exercise_log(offset=0, sum_by='duration'):
    """
    shows the history of all activities performed by the user
    newest activity is shown first
    :return:
    :rtype:
    """
    activities = Activity.query.filter_by(user_id=current_user.get_id()).order_by(desc(Activity.timestamp))
    # get hold of the activities in the last week so they can be shown on the chart
    start_week_date_before, start_week_date, end_week_date = charting.get_week_bookends(None, week_offset=offset)
    activities_this_week = Activity.query.filter(Activity.timestamp >= start_week_date_before,
                                                 Activity.timestamp <= end_week_date,
                                                 Activity.user_id == current_user.get_id()).all()
    # need to consider this as want the actual date for Monday when we are charting it
    # do need the UTC day before for getting the data to cover cases where the local time is ahead
    # of UTC
    chart_data = charting.get_chart_dataset(activities_this_week, start_week_date, sum_by=sum_by)
    return render_template('activity/view_log.html',
                           user=user, activities=activities,
                           activities_lookup=ACTIVITIES_LOOKUP,
                           icons=ICONS_LOOKUP,
                           chart_data=str(chart_data),
                           start_week=start_week_date.strftime("%b %d"),
                           end_week=end_week_date.strftime("%b %d"),
                           sum_by=sum_by,
                           offset=offset,
                           title="View Exercise Log")


@bp.route('/delete_activity/<int:activity_id>', methods=['GET'])
@login_required
def delete_activity(activity_id):
    """
    deletes the given activity
    :param activity_id: activity to delete
    :type activity_id: int
    :return: a 404 page if the activity doesn't exist for this user or the exercise log page on successful delete
    :rtype:
    """
    activity = Activity.query.filter_by(user_id=current_user.get_id(), id=activity_id).first_or_404()
    db.session.delete(activity)
    db.session.commit()
    flash('Deleted the activity')

    return redirect(url_for('main.exercise_log'))

    # activities = Activity.query.filter_by(user_id=current_user.get_id()).order_by(desc(Activity.timestamp))

    # return render_template('activity/view_log.html',
    #                      user=user, activities=activities,
    #                      activities_lookup=ACTIVITIES_LOOKUP, title="View Exercise Log")


@bp.route('/about', methods=['GET'])
def view_about():
    """
    shows the about page
    :return:
    :rtype:
    """
    return render_template('about.html', title="About LogMyExercise")

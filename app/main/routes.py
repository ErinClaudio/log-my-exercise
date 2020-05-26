
from datetime import datetime

from flask import render_template, flash, redirect, url_for
from flask import request
from flask_login import current_user, login_required

from sqlalchemy import desc

from app import db
from app.main import bp

from app.main.forms import ActivityForm, EditProfileForm
from app.models import Activity, RegularActivity, User

ACTIVITIES_LOOKUP = {1: 'Workout', 2: 'Yoga'}


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.is_authenticated:
        activities = RegularActivity.query.filter_by(user_id=current_user.get_id()).all()

    form = ActivityForm()
    # passed the id of the regular activity
    # need to get all the details of the regular activity
    # and use that to save the activity
    if form.validate_on_submit():
        activity = Activity(title=form.title.data, description=form.description.data, type=int(form.activity_type.data),
                            duration=form.duration.data, athlete=current_user)
        db.session.add(activity)
        db.session.commit()
        flash('Your activity is logged')
        return redirect(url_for('main.index'))

    return render_template('index.html', title='Home', form=form, regular_activities=activities)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    return render_template('auth/user.html', user=user)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    add_user = False
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('auth/edit_profile.html', title='Edit Profile', form=form, add_user=add_user)


@bp.route('/regular_activities', methods=['GET', 'POST'])
@login_required
def regular_activities():
    activities = RegularActivity.query.filter_by(user_id=current_user.get_id()).all()
    return render_template('activity/regularactivities.html', user=user, regular_activities=activities,
                           activities_lookup=ACTIVITIES_LOOKUP)


@bp.route('/add_regular_activities', methods=['GET', 'POST'])
@login_required
def add_regular_activity():
    form = ActivityForm()
    is_add_regular_activity = True
    if form.validate_on_submit():
        activity = RegularActivity(title=form.title.data, description=form.description.data,
                                   type=int(form.activity_type.data), duration=form.duration.data,
                                   regular_athlete=current_user)
        db.session.add(activity)
        db.session.commit()
        flash('Your regular activity is recorded')
        return redirect(url_for('main.regular_activities'))
    return render_template('activity/edit_regularactivity.html', user=user, form=form,
                           is_add_regular_activity=is_add_regular_activity)


@bp.route('/edit_regular_activity/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_regular_activity(id):
    is_add_regular_activity = False
    regular_activity = RegularActivity.query.get_or_404(id)
    form = ActivityForm(obj=regular_activity)
    if form.validate_on_submit():
        regular_activity.title = form.title.data
        regular_activity.description = form.description.data
        regular_activity.type = int(form.activity_type.data)
        regular_activity.duration = form.duration.data
        db.session.commit()
        flash('You have successfully edited your regular activity')
        return redirect(url_for('main.regular_activities'))

    form.title.data = regular_activity.title
    form.description.data = regular_activity.description
    form.activity_type.data = regular_activity.type
    form.duration.data = regular_activity.duration
    return render_template('activity/edit_regularactivity.html', is_add_regular_activity=is_add_regular_activity,
                           user=user, form=form, title="Edit Regular Activity")


@bp.route('/delete_regular_activity/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_regular_activity(id):
    regular_activity = RegularActivity.query.get_or_404(id)
    db.session.delete(regular_activity)
    db.session.commit()
    flash('You have successfully deleted the regular activity')

    return redirect(url_for('main.regular_activities'))


@bp.route('/log_activity/<int:activity_id>', methods=['GET'])
@login_required
def log_activity(activity_id):
    # get hold of the regular activity for this user
    # join on the user id to check this activity really does belong to this user
    # then copy across the data and save it
    regular_activity = RegularActivity.query.filter_by(user_id=current_user.get_id()).filter_by(id=activity_id).first()

    if regular_activity is not None:
        activity = regular_activity.create_activity()
        db.session.add(activity)
        db.session.commit()
        flash('Well done on completing {} today'.format(regular_activity.title))
    else:
        flash('Error: Activity does not exist')
    return redirect(url_for('main.index'))


@bp.route('/exercise_log', methods=['GET'])
@login_required
def exercise_log():
    activities = Activity.query.filter_by(user_id=current_user.get_id()).order_by(desc(Activity.timestamp))

    return render_template('activity/view_log.html',
                           user=user, activities=activities,
                           activities_lookup=ACTIVITIES_LOOKUP, title="View Exercise Log")

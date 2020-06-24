from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required

from app import db
from app.goal import bp
from app.goal.forms import GoalForm
from app.models import Goal


@bp.route('/set_goal', methods=['GET', 'POST'])
@login_required
def set_goal():
    """
    sets a user's exercise goal
    :return:
    :rtype:
    """
    form = GoalForm()

    if form.validate_on_submit():
        goal = Goal(title=form.title.data, motivation=form.motivation.data,
                    acceptance_criteria=form.acceptance_criteria.data,
                    reward=form.reward.data,
                    frequency=form.frequency.data, frequency_activity_type=form.frequency_activity_type.data,
                    duration_activity_type=form.duration_activity_type.data, duration=form.duration.data,
                    distance_activity_type=form.distance_activity_type.data, distance=form.distance.data,
                    user_id=current_user.get_id())

        db.session.add(goal)
        db.session.commit()
        flash('Well done on setting yourself a goal')
        return redirect(url_for('main.exercise_log'))

    return render_template('goal/edit_goal.html', title='Set a goal', form=form)

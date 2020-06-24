from datetime import datetime

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
    is_add_goal = True
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

    return render_template('goal/edit_goal.html', title='Set a goal', form=form, is_add_goal=is_add_goal)


@bp.route('/edit_goal/<int:goal_id>', methods=['GET', 'POST'])
@login_required
def edit_goal(goal_id):
    """
    Allows a user to edit an existing goal
    :param goal_id: goal to edit
    :type goal_id: int
    :return:
    :rtype:
    """
    is_add_goal = False
    goal = Goal.query.filter_by(user_id=current_user.get_id(), id=goal_id).first_or_404()
    form = GoalForm(obj=goal)
    if form.validate_on_submit():
        goal.title = form.title.data
        goal.motivation = form.motivation.data
        goal.acceptance_criteria = form.acceptance_criteria.data
        goal.reward = form.reward.data
        goal.frequency = form.frequency.data
        goal.frequency_activity_type = form.frequency_activity_type.data
        goal.duration = form.duration.data
        goal.duration_activity_type = form.duration_activity_type.data
        goal.distance = form.distance.data
        goal.distance_activity_type = form.distance_activity_type.data
        goal.last_updated = datetime.utcnow()
        db.session.commit()
        flash('Saved changes to the goal {}'.format(goal.title))
        return redirect(url_for('main.exercise_log'))

    form.title.data = goal.title
    form.motivation.data = goal.motivation
    form.acceptance_criteria.data = goal.acceptance_criteria
    form.reward.data = goal.reward
    form.frequency.data = goal.frequency
    form.frequency_activity_type.data = str(goal.frequency_activity_type)
    form.duration.data = goal.duration
    form.duration_activity_type.data = str(goal.duration_activity_type)
    form.distance.data = goal.distance
    form.distance_activity_type.data = str(goal.distance_activity_type)
    return render_template('goal/edit_goal.html', title='Set a goal', form=form, is_add_goal=is_add_goal)


@bp.route('/delete_goal/<int:goal_id>', methods=['GET'])
@login_required
def delete_goal(goal_id):
    """
    deletes a goal
    :param goal_id: activity to delete
    :type goal_id: int
    :return:
    :rtype:
    """
    goal = Goal.query.filter_by(user_id=current_user.get_id(), id=goal_id).first_or_404()
    goal_title = goal.title
    db.session.delete(goal)
    db.session.commit()
    flash('Deleted goal {}'.format(goal_title))

    return redirect(url_for('main.exercise_log'))

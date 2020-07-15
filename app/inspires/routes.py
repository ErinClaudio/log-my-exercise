from datetime import datetime

from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required

from app import db
from app.inspires import bp
from app.inspires.forms import InspiresForm
from app.main import ICONS_LOOKUP
from app.models import Inspiration, MyInspirationLikes
from app.services.charting import ACTIVITY_COLOR_LOOKUP


@bp.route('/inspires_list', methods=['GET'])
@login_required
def view_inspirations():
    """
    Shows the list of inspirations from others
    :return:
    :rtype:
    """
    inspirations = Inspiration.query.all()
    return render_template('inspires/inspirations.html', title='Inspire others', inspirations=inspirations,
                           icons=ICONS_LOOKUP, colors=ACTIVITY_COLOR_LOOKUP)


@bp.route('/detail_inspiration/<int:inspiration_id>', methods=['GET'])
@login_required
def detail_inspiration(inspiration_id):
    """
    Shows the details of a specific inspiration
    :param inspiration_id: inspiration to view
    :type inspiration_id: int
    :return:
    :rtype:
    """
    inspiration = Inspiration.query.filter_by(id=inspiration_id).first_or_404()
    return render_template('inspires/detail_inspiration.html', title='Inspire others', inspiration=inspiration,
                           icons=ICONS_LOOKUP,  colors=ACTIVITY_COLOR_LOOKUP)


@bp.route('/add_inspiration', methods=['GET', 'POST'])
@login_required
def add_inspiration():
    """
    creates a new inspiration
    :return:
    :rtype:
    """
    form = InspiresForm()
    if form.validate_on_submit():
        inspiration = Inspiration(title=form.title.data,
                                  description=form.description.data,
                                  why_loved=form.why_inspires.data,
                                  duration=form.duration.data,
                                  instructor=form.instructor.data,
                                  url=form.url.data,
                                  workout_type=int(form.type.data),
                                  likes=1,
                                  instructor_sex=0,
                                  user_id=current_user.get_id())
        db.session.add(inspiration)
        likes_inspiration = MyInspirationLikes(user_id=current_user.get_id(), inspiration_id=inspiration.id)
        db.session.add(likes_inspiration)
        db.session.commit()
        flash('Thank you for sharing your inspiration')
        return redirect(url_for('inspires.view_inspirations'))

    return render_template('inspires/edit_inspiration.html', title='Inspire others', form=form,
                           is_add_inspiration=True)


@bp.route('/edit_inspiration/<int:inspiration_id>', methods=['GET', 'POST'])
@login_required
def edit_inspiration(inspiration_id):
    """
    edits an existing inspiration
    only the user who created it can edit it
    :param inspiration_id: inspiration to edit
    :type inspiration_id: int
    :return:
    :rtype:
    """
    inspiration = Inspiration.query.filter_by(user_id=current_user.get_id(), id=inspiration_id).first_or_404()
    form = InspiresForm(obj=inspiration)
    if form.validate_on_submit():
        inspiration.title = form.title.data
        inspiration.description = form.description.data
        inspiration.why_loved = form.why_inspires.data
        inspiration.duration = form.duration.data
        inspiration.instructor = form.instructor.data
        inspiration.url = form.url.data
        inspiration.workout_type = int(form.type.data)
        inspiration.last_updated = datetime.utcnow()
        db.session.commit()
        flash('Saved changes to the inspiration {}'.format(inspiration.title))
        return redirect(url_for('inspires.view_inspirations'))

    form.title.data = inspiration.title
    form.description.data = inspiration.description
    form.why_inspires.data = inspiration.why_loved
    form.duration.data = inspiration.duration
    form.instructor.data = inspiration.instructor
    form.url.data = inspiration.url
    form.type.data = inspiration.workout_type
    return render_template('inspires/edit_inspiration.html', title='Inspire others', form=form,
                           is_add_inspiration=False)


@bp.route('/delete_inspiration/<int:inspiration_id>', methods=['GET'])
@login_required
def delete_inspiration(inspiration_id):
    """
    deletes an existing inspiration
    only the user who created it can delete it
    :param inspiration_id: inspiration to delete
    :type inspiration_id: int
    :return:
    :rtype:
    """
    inspiration = Inspiration.query.filter_by(user_id=current_user.get_id(), id=inspiration_id).first_or_404()
    inspiration_title = inspiration.title
    db.session.delete(inspiration)
    db.session.commit()
    flash('Deleted inspiration {}'.format(inspiration_title))

    return redirect(url_for('inspires.view_inspirations'))


@bp.route('/like_inspiration/<int:inspiration_id>', methods=['GET'])
@login_required
def like_inspiration(inspiration_id):
    """
    likes an inspiration. A user cannot like an inspiration they've created
    :param inspiration_id: inspiration to like
    :type inspiration_id:
    :return:
    :rtype:
    """
    inspiration = Inspiration.query.filter_by(id=inspiration_id).first_or_404()

    # check to see if user has liked this previously
    has_liked_before = MyInspirationLikes.query.filter_by(id=inspiration_id, user_id=current_user.get_id()).count()
    if has_liked_before == 0:
        inspiration.likes += 1
        inspiration.last_updated = datetime.utcnow()
        likes_inspiration = MyInspirationLikes(user_id=current_user.get_id(), inspiration_id=inspiration_id)
        db.session.add(likes_inspiration)
        db.session.commit()

    return redirect(url_for('inspires.view_inspirations'))

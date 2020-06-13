import json

from flask_login import current_user
from flask import render_template, flash, redirect, url_for, request


from app.models import User
from app.support import bp
from app.support.forms import FeedbackForm


@bp.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    form = FeedbackForm()

    if form.validate_on_submit():
        # save the feedback, consider S3
        feedback_dict = request.form.to_dict()
        feedback_dict.pop('csrf_token', None)
        print(json.dumps(feedback_dict))
        flash('Thank you for sending us a note')
        return redirect(url_for('support.contact_us'))

    if current_user.is_authenticated:
        # can set the name and email on the form
        u = User.query.filter_by(id=current_user.get_id()).first()
        form.email.data = u.email
        form.name.data = u.username

    return render_template('support/contact_us.html', title='Contact Us', form=form)

import unittest
from flask_testing import TestCase

from flask import abort, url_for

from app import create_app, db
from app.models import User, RegularActivity, Activity
from config import TestingConfig

class TestBase(TestCase):

    def create_app(self):
        app = create_app('testing')
        return app

    def setUp(self):

        db.drop_all()
        db.create_all()
        # create a test user
        user = User(username="test_user")
        user.set_password("test_user")
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()



class TestModels(TestBase):
    def test_user_model(self):
        self.assertEqual(User.query.count(),1)

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_regular_activity(self):

        u = User.query.filter_by(username='test_user').first()
        activity = RegularActivity(type=1,title='Regular Activity',
                                   user_id=u.id,description="Some description",duration=23)
        db.session.add(activity)
        db.session.commit()

        load_activity = RegularActivity.query.filter_by(user_id=u.id).first()
        self.assertEqual(activity.type, load_activity.type)
        self.assertEqual(activity.title, load_activity.title )
        self.assertEqual(activity.description, load_activity.description)
        self.assertEqual(activity.duration, load_activity.duration)

        self.assertEqual(RegularActivity.query.filter_by(user_id=u.id).count(),1)

    def test_daily_activity(self):
        # create a regular activity and use this to
        # create the new activity
        # link to the test user created
        u = User.query.filter_by(username='test_user').first()
        regular_activity = RegularActivity(type=1, title='Regular Activity',
                                   user_id=u.id, description="Some description", duration=23)
        db.session.add(regular_activity)
        activity = regular_activity.create_activity()
        db.session.add(activity)
        db.session.commit()
        self.assertEqual(activity.type, regular_activity.type)
        self.assertEqual(activity.title, regular_activity.title)
        self.assertEqual(activity.description, regular_activity.description)
        self.assertEqual(activity.duration, regular_activity.duration)
        self.assertEqual(activity.user_id, regular_activity.user_id)

        self.assertEqual(Activity.query.filter_by(user_id=u.id).count(),1)

class TestViews(TestBase):

    def test_homepage_view(self):
        response = self.client.get(url_for('main.index'))
        self.assertEqual(response.status_code, 302)

    def test_login_view(self):
        response = self.client.get(url_for('auth.login'))
        self.assertEqual(response.status_code, 200)

    def test_register_view(self):
        response = self.client.get(url_for('auth.register'))
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        target_url = url_for('auth.logout')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)


class TestErrorPages(TestBase):

    def test_403_forbidden(self):
        # create route to abort the request with the 403 Error
        @self.app.route('/403')
        def forbidden_error():
            abort(403)

        response = self.client.get('/403')
        self.assertEqual(response.status_code, 403)

    def test_404_not_found(self):
        response = self.client.get('/nothinghere')
        self.assertEqual(response.status_code, 404)

    def test_500_internal_server_error(self):
        # create route to abort the request with the 500 Error
        @self.app.route('/500')
        def internal_server_error():
            abort(500)

        response = self.client.get('/500')
        self.assertEqual(response.status_code, 500)


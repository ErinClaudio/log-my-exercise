from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app import login
from flask_login import UserMixin
from hashlib import md5

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),index=True, unique=True)
    email = db.Column(db.String(120),index=True, unique=True)
    password_hash = db.Column(db.String(128))
    activities = db.relationship('Activity',backref='athlete',lazy='dynamic')
    regular_activities = db.relationship('RegularActivity',backref='regular_athlete',lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<user {}>'.format(self.username)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    title = db.Column(db.String(50))
    description = db.Column(db.String(300))
    duration = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Activity {}'.format(self.title)


class RegularActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    title = db.Column(db.String(50))
    description = db.Column(db.String(300))
    duration = db.Column(db.Integer)
    time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def create_activity(self):
        return Activity(title=self.title,
                        description=self.description,
                        type=self.type,
                        duration=self.duration,
                        timestamp=datetime.utcnow(),
                        user_id=self.user_id)

    def __repr__(self):
        return '<RegularActivity {}'.format(self.type)
from datetime import datetime
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


from app import db
from app import login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    """
    A user of the application
    """
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    activities = db.relationship('Activity', backref='athlete', lazy='dynamic')
    regular_activities = db.relationship('RegularActivity', backref='regular_athlete', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {} {}>'.format(self.id, self.username)

    def __str__(self):
        return '<User: id={} username={}>'.format(self.id, self.username)


class Activity(db.Model):
    """
    An activity that has been performed
    """
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    title = db.Column(db.String(50))
    description = db.Column(db.String(300))
    duration = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    local_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Activity {} {} {} {} {} {} {} {}'.format(self.id, self.type, self.title,
                                                          self.description, self.duration, self.timestamp,
                                                          self.local_timestamp, self.user_id)

    def __str__(self):
        return '<Activity id={} type={} title={} description={} duration={} ' \
               'time={} local_time={} user+{}'.format(self.id, self.type, self.title,
                                                      self.description, self.duration, self.timestamp,
                                                      self.local_timestamp, self.user_id)


class RegularActivity(db.Model):
    """
    Defines an activity that is performed on a regular basis
    """
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
        return '<Regular Activity: {} {} {} {} {} {}'.format(self.title, self.description, self.type,
                                                             self.duration, self.time, self.user_id)

    def __str__(self):
        return '<Regular Activity: title={} description={} ' \
               'type={} duration={} time={} used={}'.format(self.title, self.description, self.type,
                                                            self.duration, self.time, self.user_id)


class StravaAthlete(db.Model):
    """
    Defines an athlete inside Strava. Includes the token details required to access their details via the
    Strava API
    """
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    athlete_id = db.Column(db.Integer)
    scope = db.Column(db.String(50))
    access_token = db.Column(db.String(50))
    access_token_expires_at = db.Column(db.Integer)
    access_token_expires_in = db.Column(db.Integer)
    refresh_token = db.Column(db.String(50))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Integer, default=1)

    def __repr__(self):
        """
        Returns a string representation of the StravaAthlete.
        Purposefully doesn't show the token specifics in case they are logged
        :return: string representation of this object
        :rtype:
        """
        return '<StravaAthlete: {} {} {} {} {} {} {} {}'.format(self.user_id, self.athlete_id, self.scope,
                                                                self.access_token_expires_at,
                                                                self.access_token_expires_in,
                                                                self.created_date, self.last_updated, self.is_active)

    def __str__(self):
        """
        Returns a string representation of the StravaAthlete.
        Purposefully doesn't show the token specifics in case they are logged
        :return: string representation of this object
        :rtype:
        """
        return '<StravaAthlete: id={} strava_id={} scopoe={} ' \
               'expires_at={} expires_in={} created={} ' \
               'updated={} is_Active={}'.format(self.user_id, self.athlete_id, self.scope,
                                                self.access_token_expires_at, self.access_token_expires_in,
                                                self.created_date, self.last_updated, self.is_active)


class StravaEvent(db.Model):
    """
        Defines an event occurring with Strava
    """
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer)
    action = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<StravaEvent: {} {} {}'.format(self.athlete_id, self.action, self.timestamp)

    def __str__(self):
        return '<StravaEvent: {} {} {}'.format(self.athlete_id, self.action, self.timestamp)

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db # Assuming db is initialized in app/__init__.py

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    primary_muscle_group = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<Exercise {self.name}>'

class UserMax(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    max_weight = db.Column(db.Float, nullable=False)
    date_recorded = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('user_maxes', lazy=True))
    exercise = db.relationship('Exercise', backref=db.backref('user_maxes', lazy=True))

    def __repr__(self):
        return f'<UserMax user_id={self.user_id} exercise_id={self.exercise_id} max_weight={self.max_weight}>'

class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    date_logged = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('workout_logs', lazy=True))
    exercise = db.relationship('Exercise', backref=db.backref('workout_logs', lazy=True))

    def __repr__(self):
        return f'<WorkoutLog user_id={self.user_id} exercise_id={self.exercise_id} date_logged={self.date_logged}>'

class PoliquinRatio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    primary_exercise_name = db.Column(db.String(100), nullable=False)
    secondary_exercise_name = db.Column(db.String(100), nullable=False)
    ratio = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<PoliquinRatio primary={self.primary_exercise_name} secondary={self.secondary_exercise_name} ratio={self.ratio}>'

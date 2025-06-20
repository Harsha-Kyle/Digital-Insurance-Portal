from app import db
from datetime import datetime

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(120), unique=True, nullable=False)
    password=db.Column(db.String(128), nullable=False)

class Policy(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(120))
    type=db.Column(db.String(50))
    premium=db.Column(db.Float)

class Application(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    policy_id=db.Column(db.Integer, db.ForeignKey('policy.id'))
    term=db.Column(db.String(50))
    premium=db.Column(db.Float)
    applied_at=db.Column(db.DateTime, default=datetime.utcnow)

class Claim(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    details=db.Column(db.Text)
    file=db.Column(db.String(200))
    filed_at=db.Column(db.DateTime, default=datetime.utcnow)
    status=db.Column(db.String(50), default='Submitted')

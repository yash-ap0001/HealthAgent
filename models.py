from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    health_data = db.relationship('HealthData', back_populates='user', lazy='dynamic')
    insights = db.relationship('Insight', back_populates='user', lazy='dynamic')
    
    def __repr__(self):
        return f"<User {self.username}>"


class HealthData(db.Model):
    __tablename__ = 'health_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    data_type = db.Column(db.String(50), nullable=False)  # 'steps', 'sleep', 'heart_rate', etc.
    date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    meta_data = db.Column(db.Text)  # JSON string with additional data (renamed from metadata)
    source = db.Column(db.String(50))  # Source of the data (device, app, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='health_data')
    
    def __repr__(self):
        return f"<HealthData {self.data_type} {self.date} {self.value}>"


class Insight(db.Model):
    __tablename__ = 'insights'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'activity', 'sleep', 'heart', etc.
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.Integer)  # 1-5 scale, with 5 being most severe
    is_actionable = db.Column(db.Boolean, default=True)
    recommendation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='insights')
    
    def __repr__(self):
        return f"<Insight {self.category} {self.title}>"
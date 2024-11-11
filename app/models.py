from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    account_type = db.Column(db.String(50), nullable=False, default='Basic')
    password_hash = db.Column(db.String(128), nullable=False)
    bookings = db.relationship('Booking', back_populates='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<User {self.username}>'
    def check_password(self, password):
        """Check if the provided password matches the stored password hash."""
        return check_password_hash(self.password_hash, password)
    def get_id(self):
        return str(self.id) 
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    tickets = db.Column(db.Integer, default=0)
    bookings = db.relationship('Booking', back_populates='event')
    # @property
    # def month(self):
    #     return self.event_date.month if self.event_date else None
class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default="Confirmed") 
    user = db.relationship('User', back_populates='bookings')
    event = db.relationship('Event', back_populates='bookings')
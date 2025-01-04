from wtforms import TextAreaField
from wtforms.validators import Length
from hashlib import md5
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    # One-to-many relationship between users and sessions.
    # The so.WriteOnlyMapped defines sessions as a collection that will be populated with objects from the Session class.
    # The back_populates parameter establishes the relationship from the Session class back to the User class.
    sessions: so.WriteOnlyMapped['Session'] = so.relationship(back_populates='user')
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
    
class Session(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    created_at: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    session_at: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    primarySwellHeight: so.Mapped[float] = so.mapped_column(index=True)
    primarySwellDirection: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    primarySwellPeriod: so.Mapped[float] = so.mapped_column(index=True)
    secondarySwellHeight: so.Mapped[float] = so.mapped_column(index=True)
    secondarySwellDirection: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    secondarySwellPeriod: so.Mapped[float] = so.mapped_column(index=True)
    waveHeight: so.Mapped[float] = so.mapped_column(index=True)
    windSpeed: so.Mapped[float] = so.mapped_column(index=True)
    windDirection: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    temperature: so.Mapped[float] = so.mapped_column(index=True)
    pressure: so.Mapped[float] = so.mapped_column(index=True)
    # The user_id field was initialized as a foreign key to User.id, which means that it references values from the id column in the users table.
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    # The so.Mapped class defines author as a reference to the User object that created the session
    user: so.Mapped[User] = so.relationship(back_populates='sessions')

    def __repr__(self):
        return '<Session {}>'.format(self.id)
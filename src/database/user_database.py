from setup import db
from sqlalchemy.dialects.postgresql import JSON


class UserDatabase(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(JSON)

    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return '<id {}>'.format(self.id)
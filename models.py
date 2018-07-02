from app import db
from flask_sqlalchemy import declarative_base

Base = declarative_base()

class User(db.Model):
    __tablename__ = 'Users_Id'

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.String)

    def __repr__(self):
        return '<User %r>' % (self.id_user)


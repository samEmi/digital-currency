# UserModel.py

from flask_login import UserMixin
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db


class AccountModel(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    account_id = db.Column(db.String(100), unique=True, nullable=False)
    account_pin = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000))
    sigvars = relationship('SigVarsModel')
    token = db.Column(db.String(100), unique=True)

    def get_id(self):
        return self.id

    def __init__(self, account_id, account_pin):
        self.account_id = account_id
        self.account_pin = account_pin
        # self.email = email
        #self.hash_password(account_pin)

    def __repr__(self):
        return "<User(name='%s', email='%s')>" % (self.name, self.email)

    def hash_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    # def verify_password(self, password):
    #     return check_password_hash(self.account_pin, password)

    def verify_password(self, password):
        return self.account_pin == password

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_sigvar(self, timestamp):
        for x in self.sigvars:
            if x.timestamp == timestamp:
                return x
        return None

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

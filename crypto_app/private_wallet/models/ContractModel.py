import json
import sys

from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from charm.toolbox.conversion import Conversion
from pos_app import db
from pos_app.utils import *
from crypto_utils.conversions import SigConversion
from crypto_utils.signatures import BlindSignatureVerifier


class Contract(db.Model):
    y_ = db.Column(db.String(256), primary_key=True)
    value_ = db.Column(db.Integer())
    claim_keypair_ = db.Column(db.LargeBinary)
    timestamp_ = db.Column(db.Integer)
    payed_ = db.Column(db.Boolean())
    receiver_ = db.Column(db.String())
    receiver_signature = db.Column(db.Boolean())
    receiver_pubkey = db.Column(db.Boolean())


    def __init__(self, y: str, value: int, claim_keypair: ECC, timestamp, payed: boolean, receiver: str, signature: str, pubkey: bytes):
        self.y = y
        self.value = value
        self.claim_keypair_ = claim_keypair
        self.timestamp = timestamp
        self.payed = payed
        self.receiver = receiver
        self.receiver_signature = signature
        self.receiver_pubkey = pubkey
        
    @property
    def claim_pubk(self) -> bytes:
        key = self.key_pair
        return key.public_key().export_key(format='DER')

    @property
    def u(self):
        return SigConversion.strlist2modint(self.u_)

    @u.setter
    def u(self, u):
        self.u_ = SigConversion.modint2strlist(u)

    @property
    def d(self):
        return SigConversion.strlist2modint(self.d_)

    @d.setter
    def d(self, d):
        self.d_ = SigConversion.modint2strlist(d)

    @property
    def s1(self):
        return SigConversion.strlist2modint(self.s1_)

    @s1.setter
    def s1(self, s1):
        self.s1_ = SigConversion.modint2strlist(s1)

    @property
    def s2(self):
        return SigConversion.strlist2modint(self.s2_)

    @s2.setter
    def s2(self, s2):
        self.s2_ = SigConversion.modint2strlist(s2)

    @property
    def get_timestamp(self):
        return self.timestamp

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


    @staticmethod
    def find(y: str):
        tmp = Contract.query.get(y)
        if tmp: return tmp
        else: return None

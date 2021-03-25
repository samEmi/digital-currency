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
    # customer data
    y = db.Column(db.String(256), primary_key=True)
    claim_pubk_ = db.Column(db.String(), nullable=False)
    token_pubkeys_ = db.Column(db.Array())
    timestamp_ = db.Column(db.Integer)
    payed_ = db.Column(db.Boolean())
    total_value_ = db.Column(db.Integer())

    u_ = db.Column(db.String)
    d_ = db.Column(db.String)
    s1_ = db.Column(db.String)
    s2_ = db.Column(db.String)

    def __init__(self, y: str, pubk: int, token_pubkeys: list, total_value, timestamp):
        self.y = y
        self.claim_pubk_ = str(pubk)
        self.token_pubkeys_ = [str(key) for key in token_pubkeys]
        self.timestamp = timestamp
        self.total_value_ = total_value
        self.payed_ = False

    @payed.setter
    def payed(self, payed):
        self.payed_ = payed

    @property
    def claim_pubk(self) -> bytes:
        return Conversion.IP2OS(int(self.claim_pubk_))

    @property
    def get_timestamp(self):
        return self.timestamp

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def verify_signature(self, signatures: list):
        for signature, token_pubkey in zip(signatures, self.token_pubkeys_):
            # Convert back to bytes
            sig = Conversion.IP2OS(signature)

            # Verifier setup
            ecc = ECC.import_key(token_pubkey)
            verifier = DSS.new(ecc, 'fips-186-3')
            new_hash = SHA256.new(bytes.fromhex(self.y))

            try:
                verifier.verify(new_hash, sig)
                return True
            except Exception as e:
                print(str(e), file=sys.stderr)
                return False

    def verify_blind_signature(self, providers: list, blind_signatures: list):
        for blind_signature, provider, token_pubkey in zip(blind_signatures, providers, self.token_pubkeys_):
            sig = SigConversion.convert_dict_modint(json.loads(blind_signature))
            provider_pubk = get_provider_pubkey(provider, self.timestamp)
            verifier = BlindSignatureVerifier(provider_pubk)
            message = Conversion.OS2IP(token_pubkey)
            return verifier.verify(sig, message)

    @staticmethod
    def find(y: str):
        tmp = Contract.query.get(y)
        if tmp: return tmp
        else: return None
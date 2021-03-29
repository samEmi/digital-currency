from typing import Tuple

from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from charm.toolbox.conversion import Conversion

from crypto_utils.conversions import SigConversion
from crypto_utils.signatures import UserBlindSignature
from .. import db


class TokenModel(db.Model):
    id_ = db.Column(db.Integer, primary_key=True)
    value_ = db.Column(db.Integer())
    expiration_ = db.Column(db.DateTime())
    p_id_ = db.Column(db.Integer)
    key_pair_ = db.Column(db.LargeBinary)
    user_blind_sig_ = db.Column(db.String)
    interval_timestamp_ = db.Column(db.Integer)
    proof_hash_ = db.Column(db.String)

    def __init__(self, p_id: int, value: int = 1, signer: UserBlindSignature = None,
                 interval: int = None, expiration: 'datetime' = None):
        check = TokenModel.query.filter_by(p_id_=p_id, interval_timestamp_=interval)
        if check.first() is not None:
            raise Exception("TokenModel already exists")
        else:
            self.p_id_ = p_id
            self.value_ = value
            self.key_pair_ = ECC.generate(curve='P-256').export_key(format='DER')
            self.user_blind_sig_ = signer.encode() if signer is not None else None
            self.interval_timestamp_ = interval
            self.expiration_ = expiration

    @property
    def id(self) -> int:
        return self.id_

    @property
    def value(self) -> int:
        return self.value_

    @property
    def signer(self) -> UserBlindSignature:
        return UserBlindSignature().decode(self.user_blind_sig_)

    @signer.setter
    def signer(self, signer) -> None:
        self.user_blind_sig_ = signer.encode() if signer is not None else None

    @property
    def type(self) -> str:
        if self.provider_type_ == 1:
            return 'CP'
        elif self.provider_type_ == 2:
            return 'AP'
        else:
            raise ValueError("Unexpected value for provider_type in private_walletTokenModel")

    @type.setter
    def type(self, p_type: str):
        if p_type == 'CP':
            self.provider_type_ = 1
        elif p_type == 'AP':
            self.provider_type_ = 2
        else:
            raise Exception('Invalid provider_type assignment in private_walletTokenModel')

    @property
    def p_id(self) -> int:
        """
        :return: cp: String
        """
        return self.p_id_

    @property
    def key_pair(self) -> ECC:
        """
        :return: ECC object
        """
        return ECC.import_key(encoded=self.key_pair_)

    @property
    def public_key(self) -> bytes:
        """
        Returns a DER encoded copy of the public key stored
        :return: (bytes)
        """
        key = self.key_pair
        return key.public_key().export_key(format='DER')

    @property
    def interval_timestamp(self) -> int:
        """
        :return: POSIX timestamp: int
        """
        return self.interval_timestamp_

    @property
    def policy(self) -> int:
        return self.policy_

    @property
    def proof_hash(self) -> int:
        return int(self.proof_hash_)

    @proof_hash.setter
    def proof_hash(self, hs: int or str) -> None:
        self.proof_hash_ = str(hs)

    def sign(self, y:str) -> Tuple[int, int]:
        key = self.key_pair
        msg_hash = SHA256.new(bytes.fromhex(y))
        signer = DSS.new(key, 'fips-186-3')
        signature = signer.sign(msg_hash)
        return Conversion.OS2IP(msg_hash.digest()), Conversion.OS2IP(signature)

    def generate_blind_signature(self, proof):
        signer = self.signer
        proof = SigConversion.convert_dict_modint(proof)
        return signer.gen_signature(proof)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        pass
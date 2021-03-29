import sys
from Crypto import Random as rd
from .models.ContractModel import Contract
from flask import current_app
from charm.toolbox.conversion import Conversion


class Nonce:
    def __init__(self, id: int, n=None):
        if n is None:
            self.n = 256
        else:
            self.n = n

        self.y = self.__generate_nonce__()
        self.id = id
        # self.pubkeys = pubkeys

    def __generate_nonce__(self) -> str:
        # Generate cryptographically secure random number
        y = rd.get_random_bytes(self.n).hex()

        # Check if y already exists, should be very unlikely
        check = Contract.find(y)
        while check:
            y = rd.get_random_bytes(self.n).hex()
            check = Contract.find(y)
        return y

    def save(self, total_value, timestamp) -> bool:
        # Add the generated uuid to the db
        new_user = Contract(self.y, self.id, total_value, timestamp)

        # Database interaction can throw exceptions
        try:
            new_user.save_to_db()
            return True
        except Exception:
            print("Something went wrong saving the Contract information", file=sys.stderr)
            return False


def get_provider_pubkey():
    pass

def get_merchant_signature(nonce: str):
    signer = current_app.config['signer']
    return Conversion.OS2IP(signer.sign(nonce))
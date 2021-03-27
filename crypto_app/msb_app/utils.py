from crypto_utils.signatures import SignerBlindSignature
from crypto_utils.conversions import SigConversion
from Crypto.Hash.SHA256 import SHA256Hash
from charm.toolbox.conversion import Conversion
from charm.toolbox.integergroup import IntegerGroupQ
import json
from .models.AccountModel import AccountModel
from .models.SigVarsModel import SigVarsModel
from .utils import *
from flask import current_app, flash, jsonify
from flask_jwt_extended import current_user
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta

signer = current_app.config['signer']
pubkey = current_app.config['pubkey']
key_expiration = current_app.config['key_expiration']

def validate_account(account_id, account_pass):
    user = AccountModel.query.filter_by(account_id=account_id).first()
    
    if not user or not user.verify_password(account_pass):
        raise Exception("Please check your login details and try again!")
    
    access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=30))
    refresh_token = create_refresh_token(identity=user.id, expires_delta=timedelta(minutes=30))

    resp = jsonify({
        'access': access_token,
        'refresh': refresh_token
    })

    return resp, 200

def gen_proofs_handler(es, timestamp):
    proofs = []
    # iterate through the challenge responses received
    for x in es:
        # retrieve SigVarsModel object for user so we can populate the signer with u and d
        sigvars = current_user.get_sigvar(timestamp)
        if sigvars:
            signer.d = sigvars.d
            signer.u = sigvars.u
            signer.s1 = sigvars.s1
            signer.s2 = sigvars.s2

            # do the appropriate conversions so that we can serialize
            x['e'] = SigConversion.strlist2modint(x.get('e'))
            proofs = SigConversion.convert_dict_strlist(signer.get_proofs(x))
            hash_tmp = SHA256Hash().new(json.dumps(proofs).encode())
            hash_proof = Conversion.OS2IP(hash_tmp.digest())

            proofs.append(hash_proof)

    resp = {
        'timestamp': timestamp,
        'hash_proofs': proofs
    }

    return resp

def gen_challenge_handler(number:int, timestamp: int):
    '''
    Function to initialize blind signature scheme and generate the challenge (r, a, b1, b2)
    :param: number: the number of requested signatures
    :return: data: list of dict containing challenges and the pubkey used by the signer to generate them
    '''
    sigvars = AccountModel.query.get(current_user.id).get_sigvar(timestamp)
    if sigvars:
        raise Exception("Key already exists")
    
    #TODO: add key expiration and generate new key when expired
    # start with only one challenge per request regardless of the number of tokens
    challenge = SigConversion.convert_dict_strlist(signer.get_challenge())
    sigvars = SigVarsModel(timestamp=timestamp, u=signer.u, d=signer.d, s1=signer.s1, s2=signer.s2, user_id=current_user.id)
    sigvars.save_to_db()
    
    resp = {
        'pub_key': pubkey,
        'challenge': challenge,
        'expiration': key_expiration
    }
    return resp

def verify_blind_signature():
    pass
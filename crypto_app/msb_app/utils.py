from crypto_utils.signatures import SignerBlindSignature
from crypto_utils.conversions import SigConversion
from Crypto.Hash.SHA256 import SHA256Hash
from charm.toolbox.conversion import Conversion
from charm.toolbox.integergroup import IntegerGroupQ
import json
from .models.AccountModel import AccountModel
from .models.SigVarsModel import SigVarsModel
from flask import current_app, flash, jsonify
from flask_jwt_extended import current_user
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
import sys
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from charm.toolbox.conversion import Conversion

def validate_account(account_id, account_pin):
    user = AccountModel.query.filter_by(account_id=account_id).first()
    
    if not user or not user.verify_password(account_pin):
        raise Exception("Please check your login details and try again")
    
    access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=30))
    refresh_token = create_refresh_token(identity=user.id, expires_delta=timedelta(minutes=30))

    resp = {
        'userid': user.id,
        'access': access_token,
        'refresh': refresh_token
    }
    return resp


def gen_proofs_handler(es, timestamp, userid):
    signer = current_app.config['signer']
    pool = list()
    user = AccountModel.query.get(userid)

    # print(len(SigVarsModel.query.filter_by(user_id=userid, timestamp=timestamp).all()))
    # print(len(SigVarsModel.query.filter_by(user_id=userid).all()))
    
    for x in es:
        # retrieve SigVarsModel object for user so we can populate the signer with u and d
        sigvars = user.get_sigvar(timestamp)
        if sigvars:
            signer.d = sigvars.d
            signer.u = sigvars.u
            signer.s1 = sigvars.s1
            signer.s2 = sigvars.s2

            # do the appropriate conversions so that we can serialize
            x['e'] = SigConversion.strlist2modint(x.get('e'))
            proof = SigConversion.convert_dict_strlist(signer.get_proofs(x))
            # hash_tmp = SHA256Hash().new(json.dumps(proof).encode())
            # hash_proof = Conversion.OS2IP(hash_tmp.digest())
            # print("here", flush=True)
            pool.append(proof)

    # print(len(pool), flush=True)
    resp = {
        'timestamp': timestamp,
        'proofs': pool
    } 
    return resp

def gen_challenge_handler(userid: int, number: int, timestamp: int):
    '''
    Function to initialize blind signature scheme and generate the challenge (r, a, b1, b2)
    :param: number: the number of requested signatures
    :return: data: list of dict containing challenges and the pubkey used by the signer to generate them
    '''
    sigvars = AccountModel.query.get(userid).get_sigvar(timestamp)
    if sigvars:
        raise Exception("Key already exists")

    signer = current_app.config['signer']
    pubkey = current_app.config['pubkey']
    key_expiration = current_app.config['key_expiration']
    
    #TODO: add key expiration and generate new key when expired
    # start with only one challenge per request regardless of the number of tokens
    challenge = SigConversion.convert_dict_strlist(signer.get_challenge())
    sigvars = SigVarsModel(timestamp=timestamp, u=signer.u, d=signer.d, s1=signer.s1, s2=signer.s2, user_id=userid)
    sigvars.save_to_db()
    
    resp = {
        'pub_key': pubkey,
        'challenge': challenge,
        'expiration': key_expiration
    }
 
    return resp

def verify_signature(signatures, token_pubkeys, nonce):
    for signature, token_pubkey in zip(signatures, token_pubkeys):       
        token_pubkey = Conversion.IP2OS(int(token_pubkey))
        sig = Conversion.IP2OS(signature)

        # Verifier setup
        ecc = ECC.import_key(encoded=token_pubkey)
        verifier = DSS.new(ecc, 'fips-186-3')
        new_hash = SHA256.new(bytes.fromhex(nonce))

        try:
            verifier.verify(new_hash, sig)
            return True
        except Exception as e:
            print(str(e), file=sys.stderr)
            return False

def verify_blind_signature(blind_signatures, providers, token_pubkeys):
    for blind_signature, provider, token_pubkey in zip(blind_signatures, providers, token_pubkeys):
        sig = SigConversion.convert_dict_modint(json.loads(blind_signature))
        provider_pubk = get_provider_pubkey(provider)
        verifier = BlindSignatureVerifier(provider_pubk)
        message = Conversion.OS2IP(token_pubkey)
        if verifier.verify(sig, message) == False: return False
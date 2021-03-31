from Crypto import Random as rd
from .models.TokenModel import TokenModel
import json
from typing import Tuple
from charm.toolbox.conversion import Conversion
from crypto_utils.conversions import SigConversion
from crypto_utils.signatures import UserBlindSignature
from Crypto.Hash.SHA256 import SHA256Hash

def handle_challenges(pubkey, tokens: TokenModel, resp: dict, timestamp):
    """
    Utility function that takes care of type conversions and ultimately calls the signing function
    :param signer_type: Whether a blind signature is being requested from a CP or an AP.
    :param signer_id: The CP\\AP's participant ID
    :param resp: The MSB's response to the challenge request.
    :param message: The message that the blind signature needs to be generated on (token id).
    :return: e: The challenge response that is used by the signer MSB to generate the proofs.
    """
    # get info received from signer msb
    # pubk = SigConversion.convert_dict_modint(resp.get('public_key'))
    challenge = SigConversion.convert_dict_modint(resp.get('challenge'))
    
    es = []
    updated_tokens = []

    # blind the tokens using challenge
    for token in tokens:
        # signer = token.signer
        signer = UserBlindSignature(pubkey)
        message = Conversion.OS2IP(token.public_key)
        es.append(SigConversion.convert_dict_strlist(signer.challenge_response(challenge, message)))
        token.signer = signer
        updated_tokens.append(token)
    
    res = {
        # 'timestamp': timestamp,
        'timestamp': timestamp,
        'es': es,
        'userid': resp.get('userid')
    }
    
    return res, updated_tokens

def get_token(provider_id, pubkey, timestamp, expiration, value=1):
    signer = UserBlindSignature(pubkey)
    token_model = TokenModel(p_id=provider_id, 
                             signer=signer, 
                             value=value, 
                             interval=timestamp, 
                             expiration=expiration)
    return token_model

def get_tokens_from_wallet(total_value, timestamp):
    #TODO: implement denominations
    # tokens = list(TokenModel.query.filter(TokenModel.expiration_ < timestamp).all())
    # print(len(tokens), flush=True)
    tokens = list(TokenModel.query.all())
    # print(len(tokens), flush=True)
    if len(tokens) < total_value: raise Exception("Insufficient funds")
    tokens = tokens[0:total_value]
    return tokens

def save_tokens(resp: dict, tokens: list, provider: str):
    """
    This helper function processes the hashes sent by a CP to a user. These hashes each correspond to a proof that will
    be published on the ledger. This function extracts the proof hash from the response and saves it with the
    corresponding model the user maintains for that signature.
    :param resp: The hashes of the proofs.
    :param cp: The participant ID of the CP on the network
    :param policy: The policy ID for which the signatures were requested.
    :return: None
    """

    for proof, token in zip(resp.get('proofs'), tokens):
        token.proof = proof
        token.save_to_db()
        print("saved", flush=True)        
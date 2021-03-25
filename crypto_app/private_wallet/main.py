from .utils import *
import functools
import requests
from charm.toolbox.conversion import Conversion
from flask import Blueprint, render_template, redirect, url_for, request, json, flash
import os
from time import localtime
import dotenv
from crypto_utils.conversions import SigConversion
from user.models.TokenModel import TokenModel
from user.models.ContractModel import Contract
from flask import current_app
# from private_wallet.dbs.sessions import SessionModel
from private_wallet.utils import handle_challenge, handle_response_hashes, prove_owner, validate_block, \
    handle_challenge_ap, validate_proof
import dateutil.parser

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def index():
    """
    Renders the user main page.
    :return:
    """
    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")
    if not app_name:
        app_name = "User Interface"

    return render_template('index.html', name=app_name)

@main.route('/withdraw_request', methods=['POST'])
def withdraw_tokens_from_acc(headers):
    '''Method called by the wallet front-end when the user requests to withdraw tokens from her account'''
    
    msb_id = str(request.form.get('msb'))
    total_value = int(request.form.get('total_value'))
    
    #TODO: implement denominations
    #token_values = split_amt_into_denominations()
    #num_tokens = len(token_values)

    params = {
        'account_id': str(request.form.get('account_id')),
        'account_pin': str(request.form.get('account_pin')),
        'total_value': total_value,
        'num_tokens': total_value,
        'timestamp': int(dateutil.parser.parse(request.form.get('time')).timestamp()),
    }

    # connect to msb_id which will try and generate the key model and signature challenge for each token
    res = requests.get("http://%s/key_setup" % current_app.config[msb_id], params=params, headers=headers) 
    res = res.json()
    
    # invalid input
    if res.status_code == 400:
        flash(res.get('message'))
        return redirect(url_for('main.withdraw_tokens_from_acc'))
    
    # generate list of tokens
    tokens = [get_token(provider_id=msb_id, pub_key=pub_key, 
                        timestamp=params['timestamp'], 
                        expiration=res.get('expiration')) 
                        for pub_key, value in zip(res['pub_key'], params['values'])
            ]    
    
    try:
        # generates the challenge response for each token
        es, tokens = handle_challenges(tokens, res.json(), params['timestamp'])
        try:
            res = requests.post("http://%s/withdraw_tokens" % current_app.config[msb_id], json=json.dumps(es), headers=headers)
            if res.status_code == 201:
                data = res.json()
                save_tokens(data, tokens, msb_id)
                flash("Tokens have been signed")
                return render_template('withdraw_tokens.html', 'withdraw_success')
            else:
                flash("Invalid input")
                return render_template('withdraw_tokens.html', 'withdraw_fail')
        except Exception as e:
            flash(str(e), "post_tokens")
            return render_template('withdraw_tokens.html', 'withdraw_fail')
    except Exception as e:
        flash(str(e), "post_tokens")
        return render_template('withdraw_tokens.html', 'withdraw_fail')


@main.route('/send_to_merchant_request', methods=['POST'])
def send_tokens_to_merchant():
    '''
    Method called by the wallet front-end when the user requests to send tokens to merchant.
    '''
    merchant_id = str(request.form.get('merchant_id'))
    total_value = int(request.form.get('total_value'))

    try:
        # get tokens from wallet database 
        # TODO: implement support for list of values 
        tokens = get_tokens_from_wallet(total_value)

        params = {
            'total_value': total_value,
            'claim_pubkey': tokens[0].pub_key,
            'token_pubkeys': [token.pub_key for token in tokens],
            'timestamp': int(dateutil.parser.parse(request.form.get('timestamp')).timestamp()),
        }

        # request contract which will have to be signed with tokens private keys
        res = requests.get('http://{}/request_contract'.format(current_app.config[merchant_id]), params=params)
        nonce = res.json().get('nonce')
        
        # get the list of signature proofs
        blind_signatures, signatures = [], []
        for token in tokens:
            blind_signatures.append(token.generate_blind_signature(token.proof_hash))
            signatures.append(token.sign(nonce))
        
        proofs = {
            'nonce': nonce,
            'providers': [token.p_id for token in tokens],
            'blind_signatures': [json.dumps(SigConversion.convert_dict_strlist(x)) for x in blind_signatures],
            'signatures': signatures,
        }
        
        # send tokens to merchant for validation
        res = requests.post('http://{}/send_tokens'.format(merchant_id), json=proofs)

        # handle error codes
        if res.status_code == 400:
            flash("Invalid input", '')
            return render_template('withdraw_tokens.html')

        if res.status_code == 400:
            flash("Invalid input", '')
            return render_template('withdraw_tokens.html')

        # save payment information
        if res.status == 200:
            contract = Contract(y=nonce, value = total_value, claim_keypair=tokens[0].key_pair, 
                                timestamp=params['timestamp'], payed=True, receiver=merchant_id,
                                signature=res.get('signature'), pubkey=res.get('pubkey'))
            contract.save_to_db()

    except Exception as e:
        flash(str(e))
        return render_template('send_tokens.html')


def send_tokens_to_acc():
    pass

def send_tokens_to_pw():
    pass

def receive_tokens():
    pass
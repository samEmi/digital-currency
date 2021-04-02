import functools
import requests
from charm.toolbox.conversion import Conversion
from flask import Blueprint, render_template, redirect, url_for, request, json, flash
import os
from time import localtime
import dotenv
from crypto_utils.conversions import SigConversion
from .models.TokenModel import TokenModel
from .models.ContractModel import Contract
from .models.SessionModel import Session
from flask import current_app
from .utils import *
import dateutil.parser
import sys
import datetime

main = Blueprint('main', __name__, template_folder='templates')

def token_required(func):
    """
    Helper wrapper that injects the access token that is needed for authentication into the protected methods.
    :param func: JWT protected function.
    :return:
    """
    @functools.wraps(func)
    def decorator_token_required(*args, **kwargs):
        first = Session.query.first()
        headers = {}
        if first:
            access_token = Session.query.first().access_token
            headers = {
                'Authorization': "Bearer " + access_token
            }
        return func(headers)
    return decorator_token_required

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

@main.route('/withdraw_request')
@token_required
def withdraw_request(headers):
    """
    Renders the withdraw_tokens.html page.
    :param headers:
    :return:
    """
    access_token = Session.query.first()
    if access_token is None:
        return redirect(url_for('auth.login'))
    return render_template('withdraw_tokens.html', now=localtime())


@main.route('/withdraw_request', methods=['POST'])
@token_required
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
    res = requests.get("http://%s/key_setup" % current_app.config[msb_id], params=params) 
    
    # invalid input
    if res.status_code == 400:      
        flash(res.json().get('message'), 'withdraw_fail')
        return redirect(url_for('main.withdraw_tokens_from_acc'))

    expiration = dateutil.parser.parse(res.json().get('expiration')).timestamp()
    pubkey = SigConversion.convert_dict_modint(res.json().get('pub_key'))
    tokens = [get_token(provider_id=msb_id, pubkey=pubkey, 
                        timestamp=params['timestamp'], 
                        expiration=expiration) 
                        for _ in range(params['total_value'])
            ]      
    
    try:
        # generates the challenge response for each token
        es, tokens = handle_challenges(pubkey, tokens, res.json(), params['timestamp'])
        
        try:
            # use access tokens in order to not be required to check account details every time            
            headers = {
              'Authorization': "Bearer " + res.json().get('access')
            }
            res = requests.post("http://%s/withdraw_tokens" % current_app.config[msb_id], json=json.dumps(es), headers=headers)
            if res.status_code == 201:
                data = res.json()
                save_tokens(data, tokens, msb_id)
                flash("Tokens have been signed successfully", 'withdraw_success')
                return render_template('withdraw_tokens.html')
            else:
                flash("Invalid input", 'withdraw_fail')
                return render_template('withdraw_tokens.html')
        except Exception as e:
            flash(str(e), 'withdraw_fail')
            return render_template('withdraw_tokens.html')
    except Exception as e:
        flash(str(e), 'withdraw_fail')
        return render_template('withdraw_tokens.html')


@main.route('/send_to_merchant_request')
@token_required
def send_to_merchant_request(headers):
    """
    Renders the withdraw_tokens.html page.
    :param headers:
    :return:
    """
    access_token = Session.query.first()
    if access_token is None:
        return redirect(url_for('auth.login'))
    return render_template('send_tokens.html', now=localtime())


@main.route('/send_to_merchant_request', methods=['POST'])
@token_required
def send_tokens_to_merchant(headers):
    '''
    Method called by the wallet front-end when the user requests to send tokens to merchant.
    '''
    merchant_id = str(request.form.get('merchant_id'))
    total_value = int(request.form.get('total_value'))
    timestamp = int(dateutil.parser.parse(request.form.get('time')).timestamp())
 
    try:
        # get tokens from wallet database 
        # TODO: implement support for list of values 
        tokens = get_tokens_from_wallet(total_value, timestamp)
        params = {
            'total_value': total_value,
            'claim_pubkey': tokens[0].public_key,
            'timestamp': timestamp,
        }
        

        # request contract which will have to be signed with tokens private keys
        res = requests.get('http://{}/request_contract'.format(current_app.config[merchant_id]), params=params)
        nonce = res.json().get('nonce')
        
        # get the list of signature proofs
        blind_signatures, signatures = [], []
        for token in tokens:           
            blind_signatures.append(token.generate_blind_signature(token.proof))
            signatures.append(token.sign(nonce)[1])
        
        
        token_keys = {}
        token_keys['token_pubkeys'] = []
        for token in tokens:
            # token_keys['token_pubkeys'].extend(str(Conversion.OS2IP(token.public_key)))
            token_keys['token_pubkeys'].extend(token.public_key)
        print(token_keys['token_pubkeys'][0], flush=True)
               
        proofs = json.dumps({
            'nonce': nonce,
            'providers': [token.p_id for token in tokens],
            'blind_signatures': [json.dumps(SigConversion.convert_dict_strlist(x)) for x in blind_signatures],
            'signatures': signatures,
        })
        res = requests.post('http://{}/send_tokens'.format(current_app.config[merchant_id]), json=proofs, params=token_keys)            
        
        # save payment information
        if res.status_code == 200:
            print("200", flush=True)
            contract = Contract(y=nonce, value = total_value, claim_keypair=tokens[0].key_pair, 
                                timestamp=params['timestamp'], payed=True, receiver=merchant_id,
                                signature=res.get('signature'), pubkey=res.get('pubkey'))
            print("here", flush=True)
            contract.save_to_db()
            print("here", flush=True)
            for token in tokens: TokenModel.query.filter(TokenModel.id_ == token.id).delete()
            print("here", flush=True)
            balance = len(TokenModel.query.all())
            flash("Payment completed successfully", 'send_success')
            flash(f"Remaining balance: {balance}", 'send_success')
            return render_template('withdraw_tokens.html')
        else:
            #why is the flash not working?
            flash(res.json().get('message'), 'send_fail')
            return render_template('send_tokens.html')
                    
    except Exception as e:
        flash(str(e), 'send_fail')
        return render_template('send_tokens.html')


def send_tokens_to_acc():
    pass

def send_tokens_to_pw():
    pass

def receive_tokens():
    pass
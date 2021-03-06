from flask import request, current_app, jsonify, flash, Blueprint, render_template
from .utils import *
from experiment.user import User, addUser
from experiment.dsdb import db
import json
import requests 
from crypto_utils.signatures import SignerBlindSignature
from crypto_utils.conversions import SigConversion
from flask_jwt_extended import jwt_required
import os
import time
 
main = Blueprint('main', __name__, template_folder='templates')
 
@main.route('/')
def index():
    app_name = os.getenv("APP_NAME")
    if not app_name:
        app_name = "MSB Interface"

    return render_template('index.html', name=app_name)
 

@main.route('/signup')
def signup():
    return render_template('signup.html')

@main.route('/signup', methods=['POST'])
def signup_post():
    account_id = request.form.get('account_id')
    account_pin = request.form.get('account_pin')

    # if this returns a user, then the email already exists in database
    user = AccountModel.query.filter_by(account_id=account_id).first()
    
    # if a user is found, we want to redirect back to signup page so user can try again
    if user:
        return jsonify({'message': 'User already exists'}), 401

    new_user = AccountModel(account_id=account_id, account_pin=account_pin)
    # create corresponding fabric user
    fabric_token = addUser(str(account_id))['token']
    print(fabric_token, flush=True)
    user = User(address=fabric_token, init_value=50)
    user.addAsset(40)
    new_user.token = fabric_token
    new_user.save_to_db()
    return jsonify({'message': 'Created.' + account_id}), 201


@main.route('/key_setup', methods=['GET'])
def key_setup():
    '''Function called when the user wallet app requests to withdraw tokens from given account'''
    
    account_id = request.args.get('account_id')
    account_pin = request.args.get('account_pin')
    number = request.args.get('num_tokens')
    timestamp = request.args.get('timestamp')

    if (account_id is None) or (number is None) or (account_pin is None):
        resp = jsonify({
            'message': "Bad Request: Required parameters are not set"
        })
        return resp, 400
 
    try:
        access = validate_account(account_id, account_pin)
        sigvar = gen_challenge_handler(access['userid'], number, timestamp)
        resp = {
            'access': access['access'],
            'userid': access['userid'],            
            'refresh': access['refresh'],
            'pub_key': sigvar['pub_key'],
            'challenge': sigvar['challenge'],
            'expiration': sigvar['expiration'].__str__()
        }
        return json.dumps(resp), 201
    except Exception as e:
        resp = jsonify({
            'message': "Unauthorised: " + str(e)
        })
        return resp, 400


#! connect to ledger
@main.route('/withdraw_tokens/', methods=['POST'])
@jwt_required
def withdraw_tokens():
    data = json.loads(request.json)
    
    if not data: 
        flash('Please submit data', 'post_keys')
        resp = jsonify({
            'message': "Bad Request"
        })
        return resp, 400
    
    es = data.get('es')
    timestamp = data.get('timestamp')
    userid = data.get('userid')
    try:
        res = gen_proofs_handler(es, timestamp, userid)
        resp = json.dumps(res)
        # invoken 'burn' chaincode function using Fabric API
        user = AccountModel.query.get(userid)
        print(f'User token: {user.token}', flush=True)
        fabric_user = User(address=user.token)
        #TODO: add proper amt once denominations are implemented
        fabric_user.removeAsset(amount=len(es))
        return resp, 201
    except Exception as e:
        resp = jsonify({
            'message': str(e)
        })
        return resp, 400

#! connect to ledger
@main.route('/receive_tokens_into_account', methods=['POST'])
def receive_tokens_into_account():
    data = json.loads(request.get_json())
    token_pubkeys = data.get('token_pubkeys')

    user = AccountModel.query.filter_by(account_id=request.args.get('account_id')).first()
    # check against double-spending using Fabric API
    dsdb = db(address=user.token)
    for token_pubkey in token_pubkeys:
        resp = dsdb.FindToken(pk=token_pubkey)
        # if the token is spent already then transaction is a double-spent
        if resp['result'] is True:
            return jsonify({'message': 'Double-spent attempt'}), 400
    
    # deserialise token pubkeys
    deser_token_pubkeys = [Conversion.IP2OS(int(token_pubkey)) for token_pubkey in token_pubkeys]

    total_value = request.args.get('total_value')
    providers = data.get('providers')
    nonce = data.get('nonce')
    
    # validate ownership signatures
    signatures = data.get('signatures')
    verif1 = time.time()
    
    if signatures is None or len(signatures) != int(total_value) or \
    verify_signature(signatures, deser_token_pubkeys, nonce) is False:
        return jsonify({'message': 'Invalid Signature'}), 400
    print(f"Verify ownership sig: {time.time() - verif1}", flush=True)
   
    # validate unblinded signature
    blind_signatures = data.get('blind_signatures')
    verif2 = time.time()
    if blind_signatures is None or len(blind_signatures) != int(total_value) or \
    verify_blind_signature(blind_signatures, providers, deser_token_pubkeys) is False:
        return jsonify({'message': 'Invalid Blind Signature'}), 400
    print(f"Verify blind sig: {time.time() - verif2}", flush=True)
    
    # invoke mint chaincode function using Fabric API
    # TODO: modify amount once denominations are implemented
    fabric_user = User(address=user.token, init_value=len(signatures))
    fabric_user.addAsset(amount=len(signatures))
    
    # if transaction is successfully published add tokens to dsdb 
    for token_pubkey in token_pubkeys:
        resp = dsdb.AddToken(pk=token_pubkey)
    
    return jsonify({'message': 'Payment completed successfully'}), 201

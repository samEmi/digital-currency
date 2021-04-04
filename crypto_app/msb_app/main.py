from flask import request, current_app, jsonify, flash, Blueprint, render_template
from .utils import *
from ....experiment.user import User
from ....experiment.dsdb import db
import json
import requests
from crypto_utils.signatures import SignerBlindSignature
from crypto_utils.conversions import SigConversion
from flask_jwt_extended import jwt_required
import os
 
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
        # user = AccountModel.query.get(userid)
        # fabric_user = User(token=user.token)
        # #TODO: add proper amt once denominations are implemented
        # fabric_user.removeAsset(value=len(es))
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
    
    # check against double-spending
    # dsdb = db()
    # for token_pubkey in token_pubkeys:
    #     if dsdb.FindToken(token_pubkey) is True:
    #         return jsonify({'message': 'Double-spent attempt'}), 400
    
    # deserialise token pubkeys
    token_pubkeys = [Conversion.IP2OS(int(token_pubkey)) for token_pubkey in token_pubkeys]

    total_value = request.args.get('total_value')
    providers = data.get('providers')
    nonce = data.get('nonce')
    
    # validate ownership signatures
    signatures = data.get('signatures')
    if signatures is None or len(signatures) != int(total_value) or \
    verify_signature(signatures, token_pubkeys, nonce) is False:
        return jsonify({'message': 'Invalid Signature'}), 400
    
    # validate unblinded signature
    blind_signatures = data.get('blind_signatures')
    if blind_signatures is None or len(blind_signatures) != int(total_value) or \
    verify_blind_signature(blind_signatures, providers, token_pubkeys) is False:
        return jsonify({'message': 'Invalid Blind Signature'}), 400

    # invoke mint chaincode function
    # user = AccountModel.query.filter_by(account_id=request.args.get('account_id')).first()
    # #TODO: modify amount once denominations are implemented
    # fabric_user = User(token=user.token, init_value=len(signatures))
    # fabric_user.addAsset()
    return jsonify({'message': 'Payment completed successfully'}), 201
    
    
   
    



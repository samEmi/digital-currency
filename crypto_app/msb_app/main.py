from flask import request, current_app, jsonify, flash, Blueprint, render_template
from .utils import *
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


@main.route('/key_setup', methods=['GET'])
def key_setup():
    '''Function called when the user wallet app requests to withdraw tokens from given account'''
    
    account_id = request.args.get('account_id')
    account_pin = request.args.get('account_pass')
    number = request.args.get('num_tokens')
    timestamp = request.args.get('timestamp')

    if (account_id is None) or (number is None) or (account_pin is None) :
        resp = jsonify({
            'message': "Bad Request: Required parameters are not set."
        })
        return resp, 400

    try:
        access = validate_account(account_id, account_pin)
        sigvar = gen_challenge_handler(number, timestamp)
        resp = jsonify({
            'access': access['access'],
            'refresh': access['refresh'],
            'pub_key': sigvar['pub_key'],
            'challenge': sigvar['challenge'],
            'expiration': sigvar['expiration']
        })
        return resp, 201
    except Exception as e:
        resp = jsonify({
            'message': "Unauthorised: " + e
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
    resp = json.dumps(gen_proofs_handler(es, timestamp))
    return resp, 201


@main.route('/validate_tokens', methods=['POST'])
def validate_tokens():
    data = json.loads(request.get_json())
    blind_signatures = data['blind_signatures']
    signers = data['signers']
    messages = data['messages']
    
    # verify each blind_signature
    for blind_signature, signer, message in zip(blind_signatures, signer, messages):
        if verify_blind_signature(blind_signature, signer, message) == False:
            resp = jsonify({
            'message': "Bad Request: At least on signature is not valid'"
            })
        return resp, 400
    
    return resp, 200

#! connect to ledger
@main.route('/receive_tokens_into_account', methods=['POST'])
def receive_tokens_into_account():
    data = json.loads(request.get_json())
    signatures = data['signatures']
    blind_signatures = data['blind_signatures']
    signers = data['signers']
    messages = data['messages']
    pass



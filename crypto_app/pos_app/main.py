
from user_app.utils import *
import json
import os
from datetime import timedelta
import requests
from flask import request, Response, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, current_user
from crypto_utils.conversions import SigConversion
from pos_app.dbs import Contract
from pos_app.utils import *
from flask import current_app
import dateutil.parser


@main.route('/request_contract', methods=['GET'])
def request_contract():
    '''Method called by merchant' backaned whenever a customer makes a request'''
    
    # get contract details
    total_value = int(request.args.get('total_value'))
    timestamp = int(request.args.get('timestamp'))
    token_pubkeys = list(request.args.get('token_pubkeys'))
    claim_pubkey = request.args.get('claim_pubkey')
   
    if token_pubkeys is None or claim_pubkey is None or total_value is None:
        return Response("Bad Request: Required parameters are not set.", status=400, mimetype='application/json')
    
    #TODO: implement a different check so as not to reveal the amount
    if len(token_pubkeys) < total_value: 
        return Response("Insufficient funds were sent", status=402, mimetype='application/json')
    
    nonce = Nonce(id=claim_pubkey, pubkeys=token_pubkeys)
    saved = nonce.save(total_value, timestamp)
    if saved: return jsonify({'contract': nonce.y}), 201
    else:
        return Response("{'content': 'Something went wrong saving contract info.'}", status=501, mimetype='application/json')


@main.route('/send_tokens', methods=['POST'])
def send_tokens():
    data = json.loads(request.get_json())
    nonce = data.get('nonce')
    contract = Contract.find(nonce)
    if contract == None: return jsonify({'message': 'No corresponding contract'}), 500

    singatures = data.get('signatures')
    if contract.verify_signature(singatures) == False: 
        return jsonify({'message': 'Invalid Signature'}), 400
    
    blind_singatures = data.get('blind_signatures')
    if contract.verify_blind_signature(blind_singatures) == False: 
        jsonify({'message': 'Blind signature failed to verify'}), 400

    # connect to msb which will validate tokens against database of spent tokens
    msb_id = current_app.config['msb_id']
    params = {
        'account_id':
        'account_pin':
    }
    
    res = requests.post('http://{}/receive_tokens_into_account'.format(msb_id), json=json.dumps(data), params=params)

    if res.status_code == 400:
        resp = jsonify({
            'message': "Bad Request: Couldn't publish transaction to the ledger due to invalid credentials"
        })
        return resp, 400

    if res.status_code == 409:
        resp = jsonify({
            'message': "Conflict: Couldn't publish transaction to the ledger due to double-spending attempt"
        })
        return resp, 409
    
    
    contract.payed = True
    resp = {
        'confirmation_signature': get_merchant_signature(nonce)
    }
    
    contract.save()
    return resp, 200



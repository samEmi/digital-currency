import json
import os
from datetime import timedelta
import requests
from flask import request, Response, jsonify, render_template, redirect, url_for, flash, Blueprint
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, current_user
from crypto_utils.conversions import SigConversion
# from .models.ContractModel import Contract
from .utils import *
from flask import current_app
import requests

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/request_contract', methods=['GET'])
def request_contract():
    '''Method called by merchant' backaned whenever a customer makes a request'''
    
    # get contract details
    total_value = int(request.args.get('total_value'))
    timestamp = int(request.args.get('timestamp'))
    claim_pubkey = request.args.get('claim_pubkey')
   
    if claim_pubkey is None or total_value is None:
        return Response("Bad Request: Required parameters are not set.", status=400, mimetype='application/json')
    
    nonce = Nonce(id=claim_pubkey)
    saved = nonce.save(total_value, timestamp)
    if saved: return jsonify({'nonce': nonce.y}), 201
    else:
        return Response("{'content': 'Something went wrong saving contract info.'}", status=501, mimetype='application/json')


@main.route('/send_tokens', methods=['POST'])
def send_tokens():
    data = json.loads(request.get_json())
    nonce = data.get('nonce')
    token_pubkeys = list(request.args.get('token_pubkeys'))
    print(f'Tokens: {len(token_pubkeys)}', flush=True)
   
    contract = Contract.find(nonce)
    if contract == None: return jsonify({'message': 'No corresponding contract'}), 500

    # check if the sender owns the sent tokens
    signatures = data.get('signatures')
    print(f'Sigs: {len(signatures)}', flush=True)
    if signatures is None or len(signatures) != contract.total_value \
    or contract.verify_signature(signatures, token_pubkeys) == False: 
        return jsonify({'message': 'Invalid Signature'}), 400
    
    # verify signature from msb
    blind_signatures = data.get('blind_signatures')
    if blind_signatures is None or len(blind_signatures) != contract.total_value \
    or contract.verify_blind_signature(blind_signatures, token_pubkeys) == False: 
        jsonify({'message': 'Blind signature failed to verify'}), 400

    print("good3", flush=True)

    # connect to msb which will validate tokens against database of spent tokens
    
    params = {
        'account_id': current_app.config['account_id'],
        'account_pass': current_app.config['account_pass'],
    }
    #TODO: remove hardcoded msb_id
    msb_id = current_app.config['msb1']
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
    return resp, 201



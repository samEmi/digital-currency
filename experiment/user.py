import requests
import random
import threading
from threading import Thread, Event
import time

random.seed(10)
rootUrl = "http://localhost:4000"

config = {}
config['msb1'] = '127.0.0.1:6000'
config['pw'] = '127.0.0.1:5000'

class User(Thread): 
    def __init__(self, address, init_value=None, size=None, amount=None, stats=None, nTransactions=0, throughput=False):
          super().__init__()
          self.address = address
          self.value = init_value
          self.size = size
          self.amount = amount
          self.nTransactions = nTransactions
          self.stats = stats
          self.throughput = throughput
          self.stopped = False
    
    def run(self):
        self.addAsset(self.value)
        self.perform_transactions()
    
    def addAsset(self, amount: int):
        payload = {
            "fcn": "Mint",
            "args": [str(amount)],
            "peers": [
                "peer0.msb1.example.com",
                "peer0.msb2.example.com"
            ],
            "chaincodeName": "token-erc-20",
            "channelName": "mychannel"
        }
        return self.helper(payload)
 
    def removeAsset(self, amount: int):
        payload = {
            "fcn": "Burn",
            "args": [str(amount)],
            "peers": [
                "peer0.msb1.example.com",
                "peer0.msb2.example.com"
            ],
            "chaincodeName": "token-erc-20",
            "channelName": "mychannel"
        }
        return self.helper(payload)
    

    def perform_transactions(self):
        if self.throughput:
            self.addToThroughPutList()
        else:
            self.addToLatencyList()

    def addToThroughPutList(self):
        nTrnasactions = 0
        while not self.stopped:
            randInt = random.randint(0, self.size)
            r = self.transfer(randInt, self.amount)
            if r["result"]:
                # print("Response ", r, "Recipient ", randInt, "Thread name ", self.name)
                nTrnasactions += 1
            else:
                print(":(((", r, "Thread name ", self.name)
        self.stats.append(nTrnasactions)

    def addToLatencyList(self):
        success = 0
        total = 0
        for i in range(self.nTransactions):
            randInt = random.randint(0, self.size)
            r = self.transfer(randInt, self.amount)
            if r["result"]:
                # print("Response ", r, "Recipient ", randInt, "Thread name ", self.name)
                success += 1
                total += r["latency"]
            else:
                print("RandInt", randInt, ":(((", r, "Thread name ", self.name)
        if success: self.stats.append(total/success)

    def transfer(self, recipient, amount):
        payload = {
            "fcn": "Transfer",
            "peers": [
                "peer0.msb1.example.com",
                "peer0.msb2.example.com"
            ],
            "chaincodeName": "token-erc-20",
            "channelName": "mychannel",
            "args": [
                str(recipient),
                str(amount)
            ]
        }
        return self.helper(payload)
    
    #TODO: function to call 'withdraw_tokens_from_acc' tokens from private_wallet app
    def withdraw(self, account_id: str, account_pin: str, amount: int, time: 'timestamp', msb_id: str):
        params = {
            'account_id': account_id,
            'account_pin': account_pin,
            'total_value': amount,
            'time': time,
            'msb': msb_id
        }
        requests.post("http://%s/withdraw_tokens_from_acc" % config['pw'], params=params)
    
    #TODO: function to call 'send_tokens_to_merchant' from private_wallet app
    def transfer_pw_to_acc(self, merchant_id: str, amount: int, time: 'timestamp'):
        params = {
            'merchant_id': merchant_id,
            'total_value': amount,
            'time': time
        }
        return requests.post("http://%s/send_tokens_to_merchant" % config['pw'], params=params)

    def helper(self, payload):
        url = f'{rootUrl}/channels/mychannel/chaincodes/token-erc-20'
        headers = {"Authorization" : "Bearer " + str(self.address)}
        return post(payload, url, headers=headers)


def addUser(name):
    payload = {
        "username": str(name),
        "orgName": "Org1"
    }
    return post(payload, url=f'{rootUrl}/users')

#TODO: add function to create user from the crypto app in order to test PW to account transactions
def addCryptoUser(account_id: str, account_pin: str, msb_id='msb1'):
    params = {
        'account_id': account_id,
        'account_pin': account_pin
    }
    return requests.post("http://%s/signup_post" % config[msb_id], params=params)


def post(payload, url, headers=None):
    response = None
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=180).json()
        # if not response["result"]: print(payload)
    except Exception as e:
        print(f"Post Request Error ", e)
        return response
    return response




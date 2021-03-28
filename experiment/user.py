import requests
import random
from threading import Thread

random.seed(10)

class User(Thread):
    def __init__(self, address, value, n, amount):
          super().__init__()
          self.address = address
          self.value = value
          self.n = n
          self.amount = amount
          self.rootUrl = "http://localhost:4000"
    
    def run(self):
        self.addAsset(self.value)
        self.perform_transactions(self.amount, self.n)
    
    def addAsset(self, value):
        payload = {
            "fcn": "Mint",
            "args": [str(value)],
            "peers": [
                "peer0.msb1.example.com",
                "peer0.msb2.example.com"
            ],
            "chaincodeName": "token-erc-20",
            "channelName": "mychannel"
        }
        return self.helper(payload)
    

    def perform_transactions(self, amount, n):
        for i in range(n):
            randInt = random.randint(0, n)
            r = self.transfer(randInt, amount)
            if r["result"]:
                print("Response ", r, "Recipient ", randInt, "Thread name ", self.name)
            else:
                print(":(((", r)
    

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

    def helper(self, payload):
        url = f'{self.rootUrl}/channels/mychannel/chaincodes/token-erc-20'
        headers = {"Authorization" : "Bearer " + str(self.address)}
        return post(payload, url, headers=headers)



def post(payload, url, headers=None):
    response = None
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=180).json()
    except Exception as e:
        print(f"Post Request Error ", e)
        return response
    return response
    # def post(self, payload, url, headers=None):
    #     response = None
    #     try:
    #         response = requests.post(url, json=payload, headers=headers, timeout=180).json()
    #     except Exception as e:
    #         print(f"Post Request Error ", e)
    #         return response
    #     return response

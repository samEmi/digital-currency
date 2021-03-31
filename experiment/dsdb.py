import requests
import random
from threading import Thread

random.seed(10)
rootUrl = "http://localhost:4000"


class db(Thread):
    def __init__(self, address):
          super().__init__()
          self.address = address

    def AddToken(self, pk, address):
        payload = {
                "fcn": "AddSpentToken",
                "peers": [
                    "peer0.msb1.example.com",
                    "peer0.msb2.example.com"
                ],
                "chaincodeName": "token-erc-20",
                "channelName": "mychannel",
                "args": [
                    pk
                ],
            }
        return self.helper(payload, 0)


    def FindToken(self, pk, address):
        payload = {
            "fcn": "AddSpentToken",
            "peer": [
                "peer0.msb1.example.com",
            ],
            "args": [
                pk
            ],
        }
        return self.helper(payload, 1)

    
    def helper(self, payload, code):
        #If code is 0 then post request, if code is 1 then get request
        url = f'{rootUrl}/channels/mychannel/chaincodes/token-erc-20'
        headers = {"Authorization" : "Bearer " + str(self.address)}
        if (code == 0):
            return post(payload, url, headers=headers)
        return get(payload, url, headers=headers)




def post(payload, url, headers=None):
    response = None
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=180).json()
        # if not response["result"]: print(payload)
    except Exception as e:
        print(f"Post Request Error ", e)
        return response
    return response

def get(payload, url, headers=None):
    response = None
    try:
        response = requests.get(url, params=payload, headers=headers, timeout=180).json()
        # if not response["result"]: print(payload)
    except Exception as e:
        print(f"Post Request Error ", e)
        return response
    return response

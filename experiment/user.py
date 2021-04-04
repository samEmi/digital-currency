import requests
import random
from threading import Thread
import time

random.seed(10)
rootUrl = "http://localhost:4000"

class User(Thread):
    def __init__(self, address, init_value, size, amount, stats, nTransactions=0, throughput=False):
          super().__init__()
          self.address = address
          self.value = init_value
          self.size = size
          self.amount = amount
          self.nTransactions = nTransactions
          self.stats = stats
          self.throughput = throughput
    
    def run(self):
        self.addAsset()
        self.perform_transactions()
    
    def addAsset(self):
        payload = {
            "fcn": "Mint",
            "args": [str(self.value)],
            "peers": [
                "peer0.msb1.example.com",
                "peer0.msb2.example.com"
            ],
            "chaincodeName": "token-erc-20",
            "channelName": "mychannel"
        }
        return self.helper(payload)

    def removeAsset(self):
        pass
    

    def perform_transactions(self):
        if self.throughput:
            self.addToThroughPutList()
        else:
            self.addToLatencyList()

    def addToThroughPutList(self):
        elapsed = 0
        nTrnasactions = 0
        while elapsed < 10:
            randInt = random.randint(0, self.size)
            start = time.time()
            r = self.transfer(randInt, self.amount)
            end = time.time()
            if r["result"]:
                # print("Response ", r, "Recipient ", randInt, "Thread name ", self.name)
                nTrnasactions += 1
            # else:
            #     print(":(((", r, "Thread name ", self.name)
            elapsed += end - start
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
            # else:
            #     print(":(((", r, "Thread name ", self.name)
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


def post(payload, url, headers=None):
    response = None
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=180).json()
        # if not response["result"]: print(payload)
    except Exception as e:
        print(f"Post Request Error ", e)
        return response
    return response

import requests
import json
from user import User, post

rootUrl = "http://localhost:4000"


# def addUsers(n):
#     for i in range(n):
#         response = addUser(i)
#         if response and response["success"]:
#             token = response["token"]
#             addAsset(token, 100)
#             perform_transactions(token, 10, n)
#         else:
#             print(response)
#         print("=================================================\n")

def simulate_network(size):
    for i in range(size):
        response = addUser(i)
        if response and response["success"]:
            token = response["token"]
            user = User(token, 100, size, 9)
            user.start()
        else:
            print(response)
        print("=================================================\n")

def addUser(name):
    payload = {
        "username": str(name),
        "orgName": "Org1"
    }
    return post(payload, url=f'{rootUrl}/users')


# def addAsset(address, amount):
#     payload = {
#         "fcn": "Mint",
#         "args": [str(amount)],
#         "peers": [
#             "peer0.msb1.example.com",
#             "peer0.msb2.example.com"
#         ],
#         "chaincodeName": "token-erc-20",
#         "channelName": "mychannel"
#     }
#     return invokeChaincodeFunc(address, payload)


# def perform_transactions(sender, amount, n):
#     for i in range(n):
#         r = transfer(sender, i, amount)
#         print(r)
    

# def transfer(sender, recipient, amount):
#     payload = {
#         "fcn": "Transfer",
#         "peers": [
#             "peer0.msb1.example.com",
#             "peer0.msb2.example.com"
#         ],
#         "chaincodeName": "token-erc-20",
#         "channelName": "mychannel",
#         "args": [
#             str(recipient),
#             str(amount)
#         ]
#     }
#     return invokeChaincodeFunc(sender, payload)


# def invokeChaincodeFunc(authorized_address, payload):
#     url = f'{rootUrl}/channels/mychannel/chaincodes/token-erc-20'
#     headers = {"Authorization" : "Bearer " + str(authorized_address)}
#     return post(payload, url, headers=headers)


# def post(payload, url, headers=None):
#     response = None
#     try:
#         response = requests.post(url, json=payload, headers=headers, timeout=180).json()
#     except Exception as e:
#         print(f"Post Request Error ", e)
#         return response
#     return response


simulate_network(4)



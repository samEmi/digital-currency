import requests
import json

rootUrl = "http://localhost:4000"



def addUsers(n):
    for i in range(n):
        response = addUser(i)
        if response and response["success"]:
            token = response["token"]
            r = addAsset(token, 100)
            print(r)
        else:
            print(response)



def addUser(name):
    payload = {
        "username": str(name),
        "orgName": "Org1"
    }
    return post(payload, url=f'{rootUrl}/users')


def addAsset(address, amount):
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
    return invokeChaincodeFunc(address, payload)


def transfer(sender, recipient, amount):
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
    return invokeChaincodeFunc(sender, payload)

def invokeChaincodeFunc(authorized_address, payload):
    url = f'{rootUrl}/channels/mychannel/chaincodes/token-erc-20'
    headers = {"Authorization" : "Bearer " + str(authorized_address)}
    return post(payload, url, headers=headers)

def post(payload, url, headers=None):
    response = None
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=180).json()
    except Exception as e:
        print(f"Post Request Error ", e)
        return response
    return response


addUsers(4)

# addAsset("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MTY5MTUwNzQsInVzZXJuYW1lIjoiZmZmIiwib3JnTmFtZSI6Ik9yZzEiLCJpYXQiOjE2MTY4NzkwNzR9.hW8ZL3oMt7l1kblrbREL2_M5Xx87SP3dybGUGWhUnWg")

# payload = {
#     "fcn": "Transfer",
#     "peers": [
#         "peer0.msb1.example.com",
#         "peer0.msb2.example.com"
#     ],
#     "chaincodeName": "token-erc-20",
#     "channelName": "mychannel",
#     "args": [
#         "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MTY3MzM5NDUsInVzZXJuYW1lIjoibmFtIiwib3JnTmFtZSI6Ik9yZzEiLCJpYXQiOjE2MTY2OTc5NDV9.OhbbARlWXOeigYs-WxVI2MOVWBQK0CbmhgZgV4_tFBE",
#          "40"
#     ]
# }


# # headers = {"Authorization" : "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MTY5MTUwNzQsInVzZXJuYW1lIjoiZmZmIiwib3JnTmFtZSI6Ik9yZzEiLCJpYXQiOjE2MTY4NzkwNzR9.hW8ZL3oMt7l1kblrbREL2_M5Xx87SP3dybGUGWhUnWg" }

# header = {"Authorization" : "Bearer eDUwOTo6Q049cm9uLE9VPWNsaWVudCtPVT1vcmcxK09VPWRlcGFydG1lbnQxOjpDTj1jYS5tc2IxLmV4YW1wbGUuY29tLE89bXNiMS5leGFtcGxlLmNvbSxMPVNhbiBGcmFuY2lzY28sU1Q9Q2FsaWZvcm5pYSxDPVVT" }

# r = requests.post('http://localhost:4000/channels/mychannel/chaincodes/token-erc-20', json=payload, headers=headers, timeout=180)

# print(r.text)

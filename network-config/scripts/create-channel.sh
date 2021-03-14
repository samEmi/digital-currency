export CORE_PEER_TLS_ENABLED=true
export ORDERER_CA=${PWD}/../crypto-config/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem

export PEER0_MSB1_CA=${PWD}/../crypto-config/peerOrganizations/msb1.example.com/peers/peer0.msb1.example.com/tls/ca.crt
export PEER0_MSB2_CA=${PWD}/../crypto-config/peerOrganizations/msb2.example.com/peers/peer0.msb2.example.com/tls/ca.crt
export PEER0_MSB3_CA=${PWD}/../crypto-config/peerOrganizations/msb3.example.com/peers/peer0.msb3.example.com/tls/ca.crt
export PEER0_MSB4_CA=${PWD}/../crypto-config/peerOrganizations/msb4.example.com/peers/peer0.msb4.example.com/tls/ca.crt
export PEER0_MSB5_CA=${PWD}/../crypto-config/peerOrganizations/msb5.example.com/peers/peer0.msb5.example.com/tls/ca.crt

export FABRIC_CFG_PATH=${PWD}/../config/

export CHANNEL_NAME=mychannel

# Orderer

setGlobalsForOrderer(){
    export CORE_PEER_LOCALMSPID="OrdererMSP"
    export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/../crypto-config/ordererOrganizations/example.com/orderers/orderer1.example.com/msp/tlscacerts/tlsca.example.com-cert.pem
    export CORE_PEER_MSPCONFIGPATH=${PWD}/../crypto-config/ordererOrganizations/example.com/users/Admin@example.com/msp
    
}

# Peers for each msb

setGlobalsForPeer0Org1(){
    export CORE_PEER_LOCALMSPID="MSB1"
    export CORE_PEER_TLS_ROOTCERT_FILE=$PEER0_MSB1_CA
    export CORE_PEER_MSPCONFIGPATH=${PWD}/../crypto-config/peerOrganizations/msb1.example.com/users/Admin@msb1.example.com/msp
    export CORE_PEER_ADDRESS=localhost:7051
}

setGlobalsForPeer1Org1(){
    export CORE_PEER_LOCALMSPID="MSB1"
    export CORE_PEER_TLS_ROOTCERT_FILE=$PEER0_MSB1_CA
    export CORE_PEER_MSPCONFIGPATH=${PWD}/../crypto-config/peerOrganizations/msb1.example.com/users/Admin@msb1.example.com/msp
    export CORE_PEER_ADDRESS=localhost:8051
    
}

setGlobalsForPeer0Org2(){
    export CORE_PEER_LOCALMSPID="MSB2"
    export CORE_PEER_TLS_ROOTCERT_FILE=$PEER0_MSB2_CA
    export CORE_PEER_MSPCONFIGPATH=${PWD}/../crypto-config/peerOrganizations/msb2.example.com/users/Admin@msb2.example.com/msp
    export CORE_PEER_ADDRESS=localhost:9051
    
}

setGlobalsForPeer1Org2(){
    export CORE_PEER_LOCALMSPID="MSB2"
    export CORE_PEER_TLS_ROOTCERT_FILE=$PEER0_MSB2_CA
    export CORE_PEER_MSPCONFIGPATH=${PWD}/../crypto-config/peerOrganizations/msb2.example.com/users/Admin@msb2.example.com/msp
    export CORE_PEER_ADDRESS=localhost:10051
    
}

setGlobalsForPeer0Org3(){
    export CORE_PEER_LOCALMSPID="MSB3"
    export CORE_PEER_TLS_ROOTCERT_FILE=$PEER0_MSB3_CA
    export CORE_PEER_MSPCONFIGPATH=${PWD}/../crypto-config/peerOrganizations/msb3.example.com/users/Admin@msb3.example.com/msp
    export CORE_PEER_ADDRESS=localhost:9051
    
}

setGlobalsForPeer1Org3(){
    export CORE_PEER_LOCALMSPID="MSB3"
    export CORE_PEER_TLS_ROOTCERT_FILE=$PEER0_MSB3_CA
    export CORE_PEER_MSPCONFIGPATH=${PWD}/../crypto-config/peerOrganizations/msb3.example.com/users/Admin@msb3.example.com/msp
    export CORE_PEER_ADDRESS=localhost:10051
    
}

setGlobalsForPeer0Org4(){
    export CORE_PEER_LOCALMSPID="MSB4"
    export CORE_PEER_TLS_ROOTCERT_FILE=$PEER0_MSB4_CA
    export CORE_PEER_MSPCONFIGPATH=${PWD}/../crypto-config/peerOrganizations/msb4.example.com/users/Admin@msb4.example.com/msp
    export CORE_PEER_ADDRESS=localhost:9051
    
}

setGlobalsForPeer1Org4(){
    export CORE_PEER_LOCALMSPID="MSB4"
    export CORE_PEER_TLS_ROOTCERT_FILE=$PEER0_MSB4_CA
    export CORE_PEER_MSPCONFIGPATH=${PWD}/../crypto-config/peerOrganizations/msb4.example.com/users/Admin@msb4.example.com/msp
    export CORE_PEER_ADDRESS=localhost:10051
    
}

setGlobalsForPeer0Org5(){
    export CORE_PEER_LOCALMSPID="MSB5"
    export CORE_PEER_TLS_ROOTCERT_FILE=$PEER0_MSB5_CA
    export CORE_PEER_MSPCONFIGPATH=${PWD}/../crypto-config/peerOrganizations/msb5.example.com/users/Admin@msb52.example.com/msp
    export CORE_PEER_ADDRESS=localhost:9051
    
}

setGlobalsForPeer1Org5(){
    export CORE_PEER_LOCALMSPID="MSB5"
    export CORE_PEER_TLS_ROOTCERT_FILE=$PEER0_MSB5_CA
    export CORE_PEER_MSPCONFIGPATH=${PWD}/../crypto-config/peerOrganizations/msb5.example.com/users/Admin@msb52.example.com/msp
    export CORE_PEER_ADDRESS=localhost:10051
    
}

createChannel(){
    rm -rf ./channel-artifacts/*
    setGlobalsForPeer0Org1
    
    peer channel create -o localhost:7050 -c $CHANNEL_NAME \
    --ordererTLSHostnameOverride orderer1.example.com \
    -f ../${CHANNEL_NAME}.tx --outputBlock ../channel-artifacts/${CHANNEL_NAME}.block \
    --tls $CORE_PEER_TLS_ENABLED --cafile $ORDERER_CA
}

removeOldCrypto(){
    rm -rf ./api-1.4/crypto/*
    rm -rf ./api-1.4/fabric-client-kv-org1/*
    rm -rf ./api-2.0/org1-wallet/*
    rm -rf ./api-2.0/org2-wallet/*
}


joinChannel(){
    setGlobalsForPeer0Org1
    peer channel join -b ../channel-artifacts/$CHANNEL_NAME.block
    
    setGlobalsForPeer1Org1
    peer channel join -b ../channel-artifacts/$CHANNEL_NAME.block
    
    setGlobalsForPeer0Org2
    peer channel join -b ../channel-artifacts/$CHANNEL_NAME.block
    
    setGlobalsForPeer1Org2
    peer channel join -b ../channel-artifacts/$CHANNEL_NAME.block

    setGlobalsForPeer0Org3
    peer channel join -b ../channel-artifacts/$CHANNEL_NAME.block
    
    setGlobalsForPeer1Org3
    peer channel join -b ../channel-artifacts/$CHANNEL_NAME.block

    setGlobalsForPeer0Org4
    peer channel join -b ../channel-artifacts/$CHANNEL_NAME.block
    
    setGlobalsForPeer1Org4
    peer channel join -b ../channel-artifacts/$CHANNEL_NAME.block

    setGlobalsForPeer0Org5
    peer channel join -b ../channel-artifacts/$CHANNEL_NAME.block
    
    setGlobalsForPeer1Org5
    peer channel join -b ../channel-artifacts/$CHANNEL_NAME.block
    
}

updateAnchorPeers(){
    setGlobalsForPeer0Org1
    peer channel update -o localhost:7050 --ordererTLSHostnameOverride orderer1.example.com -c $CHANNEL_NAME -f ./${CORE_PEER_LOCALMSPID}anchors.tx --tls $CORE_PEER_TLS_ENABLED --cafile $ORDERER_CA
    
    setGlobalsForPeer0Org2
    peer channel update -o localhost:7050 --ordererTLSHostnameOverride orderer1.example.com -c $CHANNEL_NAME -f ./${CORE_PEER_LOCALMSPID}anchors.tx --tls $CORE_PEER_TLS_ENABLED --cafile $ORDERER_CA
    
}

# removeOldCrypto

#createChannel
joinChannel
# updateAnchorPeers
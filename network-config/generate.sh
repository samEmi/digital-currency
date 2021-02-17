
# add the configtx tool to your CLI 
export PATH=${PWD}/../fabric-samples/bin:$PATH

# setup the above env var to the path of the configtx.yaml file
export FABRIC_CFG_PATH=${PWD}
CHANNEL_NAME=mychannel

# script to create the network config transactions

# remove previous crypto material and config transactions
rm -fr config/*
rm -fr crypto-config/*

# 1. generate crypto material
# Q: what exactly is this crypto material
cryptogen generate --config=./crypto-config.yaml
if [ "$?" -ne 0 ]; then
  echo "Failed to generate crypto material..."
  exit 1
fi

# 2. generate genesis block for orderer
# the genesis block contains the network config (oderer and consortium) as specified profile arg
configtxgen -profile MultiOrgOrdererGenesis -outputBlock ./config/genesis.block
if [ "$?" -ne 0 ]; then
  echo "Failed to generate orderer genesis block..."
  exit 1
fi

# generate channel configuration transaction
configtxgen -profile MultiOrgChannel -outputCreateChannelTx ./config/channel.tx -channelID mychannel
if [ "$?" -ne 0 ]; then
  echo "Failed to generate channel configuration transaction..."
  exit 1
fi


# TODO: transform this into for loop to create anchor peers for each relevant org
# Q: what exactly is an anchor peer?

# generate anchor peer transaction
configtxgen -profile MultiOrgChannel -outputAnchorPeersUpdate ./config/Org1MSPanchors.tx -channelID mychannel -asOrg Org1MSP
if [ "$?" -ne 0 ]; then
  echo "Failed to generate anchor peer update for Org1MSP..."
  exit 1
fi

configtxgen -profile MultiOrgChannel -outputAnchorPeersUpdate ./config/Org2MSPanchors.tx -channelID mychannel -asOrg Org2MSP
if [ "$?" -ne 0 ]; then
  echo "Failed to generate anchor peer update for Org1MSP..."
  exit 1
fi

configtxgen -profile MultiOrgChannel -outputAnchorPeersUpdate ./config/Org3MSPanchors.tx -channelID mychannel -asOrg Org3MSP
if [ "$?" -ne 0 ]; then
  echo "Failed to generate anchor peer update for Org1MSP..."
  exit 1
fi


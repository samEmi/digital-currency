
# chmod -R 0755 ./crypto-config
# # Delete existing artifacts
# rm -rf ./crypto-config
# rm genesis.block mychannel.tx
# rm -rf ../../channel-artifacts/*

#Generate Crypto artifactes for organizations
cryptogen generate --config=./crypto-config.yaml --output=./crypto-config/


# System channel
SYS_CHANNEL="sys-channel"

# channel name defaults to "mychannel"
CHANNEL_NAME="mychannelna"

echo $CHANNEL_NAME

# Generate System Genesis block
configtxgen -profile OrdererGenesis -configPath . -channelID $SYS_CHANNEL  -outputBlock ./genesis.block

# Generate channel configuration block
configtxgen -profile BasicChannel -configPath . -outputCreateChannelTx ./${CHANNEL_NAME}.tx -channelID $CHANNEL_NAME

echo "#######    Generating anchor peer update for MSB1  ##########"
configtxgen -profile BasicChannel -configPath . -outputAnchorPeersUpdate ./MSB1anchors.tx -channelID $CHANNEL_NAME -asOrg MSB1

echo "#######    Generating anchor peer update for MSB2  ##########"
configtxgen -profile BasicChannel -configPath . -outputAnchorPeersUpdate ./MSB2anchors.tx -channelID $CHANNEL_NAME -asOrg MSB2

echo "#######    Generating anchor peer update for MSB3  ##########"
configtxgen -profile BasicChannel -configPath . -outputAnchorPeersUpdate ./MSB3anchors.tx -channelID $CHANNEL_NAME -asOrg MSB3

echo "#######    Generating anchor peer update for MSB4  ##########"
configtxgen -profile BasicChannel -configPath . -outputAnchorPeersUpdate ./MSB4anchors.tx -channelID $CHANNEL_NAME -asOrg MSB4

echo "#######    Generating anchor peer update for MSB5  ##########"
configtxgen -profile BasicChannel -configPath . -outputAnchorPeersUpdate ./MSB5anchors.tx -channelID $CHANNEL_NAME -asOrg MSB5
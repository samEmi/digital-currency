# run outside project dir
sudo apt-get install nodejs

sudo apt-get install npm

sudo curl -sSL https://bit.ly/2ysbOFE | bash -s

sudo cp ./fabric-samples/bin/* /usr/local/bin

# cd into project dir
cd digital-currency

chmod +x ./install_dependencies.sh
./install_dependencies.sh

cd network-config/artifacts
docker-compose up -d

cd ..
chmod +x ./createChannel.sh
./createChannel.sh

chmod +x ./deployChaincode.sh
./deployChaincode.sh
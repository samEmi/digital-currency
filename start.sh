chmod +x ./install_dependencies.sh
./install_dependencies.sh

cd network-config/artifacts
docker-compose up -d
cd ..
chmod +x ./createChannel.sh
./createChannel.sh

chmod +x ./deployChaincode.sh
./deployChaincode.sh



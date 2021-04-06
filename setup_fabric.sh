# run outside project dir
sudo apt-get install golang
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin

sudo apt-get install nodejs

sudo apt-get install npm

sudo curl -sSL https://bit.ly/2ysbOFE | bash -s

sudo cp ./fabric-samples/bin/* /usr/local/bin
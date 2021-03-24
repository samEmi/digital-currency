# charm dependencies
sudo apt update && sudo apt install --yes build-essential flex bison wget subversion m4 python3 python3-dev python3-setuptools libgmp-dev libssl-dev
wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz && tar xvf pbc-0.5.14.tar.gz
cd ./pbc-0.5.14
sudo ./configure LDFLAGS="-lgmp"
sudo make && sudo make install && sudo ldconfig
cd ..

# get charm
git clone https://github.com/JHUISI/charm.git
cd ./charm
sudo ./configure.sh 
sudo make && sudo make install && sudo ldconfig

# pip install requirements
pip3 install --no-cache-dir -r requirements.txt
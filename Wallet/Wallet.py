import CreateDatabase as cd
from bitcoinlib.wallets import Wallet, wallet_delete, wallet_delete_if_exists
from bitcoinlib.mnemonic import Mnemonic
import KeyGeneration


class ColdWallet:
    def __init__(self):
        self.TotalAmount = 0
        self.walletAddress = None
        self.walletObj = None
        self.initialiseWalletAddress()
        # self.send("feoifje")
        self.displayTotal()

    def initialiseWalletAddress(self):
        if (self.walletAddress == None):
            kg = KeyGeneration.KeyGenerator()
            privk = kg.generate_key()
            self.walletAddress = privk

    def receive(self):
        pass

    def send(self, recipientAddress):
        kg = KeyGeneration.KeyGenerator()
        privk = kg.generate_key()
        pk = kg.private2public(privk)

    def updateTotal(self, amount):
        pass

    def displayTotal(self):
        conn = cd.createConnection()
        SQLQuery = """SELECT SUM(AMOUNT) FROM wallet"""
        rows = cd.sqlSelect(conn, SQLQuery)
        for row in rows:
            print(row)

    def createTransactionAddress(self):
        #Stealth Address: Wallet Address + Private Key of Tokens + Random Data
        pass

    def createPrivateKey(self):
        #When receiving token we make private key and store in database
        pass

def main():
    conn = cd.createConnection()
    sqlCreateWallet = """ CREATE TABLE IF NOT EXISTS wallet (
                                         id integer PRIMARY KEY,
                                         PrivateKey VARCHAR(130) NOT NULL,
                                         PublicKey VARCHAR(130) NOT NULL,
                                         Amount FLOAT NOT NULL,
                                         ReceivedTimeStamp TIMESTAMP NOT NULL
                                     ); """
    cd.sqlCreateInsert(conn, sqlCreateWallet)
    w = ColdWallet()

if __name__ == "__main__":
    main()

'''
When sending - you just need to know the recipients address 
(stealth Address - wallet address and random data)

When receiving - connect to Ledger?

Transaction - sender address, recipient address, amount (list of tokens)

'''
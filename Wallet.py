import CreateDatabase as cd
import KeyGeneration as KeyGeneration
import Token as Token
import datetime

class ColdWallet:
    def __init__(self):
        self.TotalAmount = 0
        self.walletAddress = None
        self.walletObj = None
        self.initialiseWalletAddress()
        # self.displayTotal()
        # tk = Token.Token(50, datetime.datetime.now())
        # self.receive(tk)
        self.displayTotal()
        amount = [2, 4, 6]
        self.updateTotal(amount)
        self.displayTotal()


    def initialiseWalletAddress(self):
        if (self.walletAddress == None):
            kg = KeyGeneration.KeyGenerator()
            privk = kg.generate_key()
            self.walletAddress = privk

    def receive(self, token):
        kg = KeyGeneration.KeyGenerator()
        privk = kg.generate_key()
        pk = kg.private2public(privk)
        InsertReceived = """INSERT INTO wallet(PrivateKey, PublicKey, Amount, ReceivedTimeStamp) 
        VALUES(?, ?, ?, ?)"""
        parameters = (privk, pk, token.amount, token.receivedtime)
        conn = cd.createConnection()
        cd.sqlInsert(conn, InsertReceived, parameters)
        print("Successfully Received")

    def send(self, recipientAddress):
        pass

    def updateTotal(self, amount):
        #Delete the tokens that were transacted
        #Amount is a list of primary keys
        sqlDelete = "DELETE FROM Wallet WHERE id = ?"
        conn = cd.createConnection()
        cd.sqlDelete(conn, sqlDelete, amount)

    def displayTotal(self):
        conn = cd.createConnection()
        SQLQuery = """SELECT SUM(AMOUNT) FROM wallet"""
        rows = cd.sqlSelect(conn, SQLQuery)
        print("Total is £" + str(rows[0][0]))

    def createTransactionAddress(self):
        #Stealth Address: Wallet Address + Private Key of Tokens + Random Data
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
    cd.sqlCreate(conn, sqlCreateWallet)
    w = ColdWallet()

if __name__ == "__main__":
    main()

'''
When sending - you just need to know the recipients address 
(stealth Address - wallet address and random data)

When receiving - connect to Ledger?

Transaction - sender address, recipient address, amount (list of tokens)

'''
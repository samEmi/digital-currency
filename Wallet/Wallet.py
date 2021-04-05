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

    def receive(self):
        # Do we need this function? Might only be useful when transaction is sent from another PW
        # since receiving transactions from account should be handled by request_tokens_from_account
        pass

    def request_tokens_from_account(self):
        '''Function to sent transaction with payload: pubKey, blind(token ids), amounts'''
        # generate random token ids, each token key is associated with amount
        # blind the token ids: interactive back and forth scheme between user and signer
        # blind the amount with Pedersen commitments
        # generate public key for tokens to be sent to
        # connect to fabric gateway
        # retrieve account identity from Fabric wallet i.e. Alice 'account' credentials
        # invoke Fabric chaincode with transaction payload: pubKey, blind(token ids), amounts
        # For this transaction endorsement should only verify that the transaction has been correctly built
        # and that the account is legitimate
        # The chaincode function invocation returns a transaction response which in our case should contain the signed blinded tokens
        # These will be added to the wallet database?


    def send_to_pw(self):
        pass

    def send_to_account(self):
        '''Function which takes a set of signed(blinded(tokens)) unblinds them 
        and sends a transaction with payload: signed(tokens), amount, receiver identity ('Bob')'''
        # In this case the network endorsing peers will only verify the signature


    def send(self, recipientAddress):
        pass

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
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC 
from Crypto.Signature import DSS
from charm.toolbox.conversion import Conversion
from Crypto import Random as rd


def main():
    # generate an ECC key and export
    key = ECC.generate(curve='P-256').export_key(format='DER')
    
    # import key back
    key = ECC.import_key(encoded=key)
    
    y = rd.get_random_bytes(256).hex()
    msg_hash = SHA256.new(bytes.fromhex(y))
    signer = DSS.new(key, 'fips-186-3')
    signature = signer.sign(msg_hash)
    pubkey = key.public_key().export_key(format='DER')
   
    pubkey = ECC.import_key(encoded=pubkey)
    verifier = DSS.new(pubkey, 'fips-186-3')
    new_hash = SHA256.new(bytes.fromhex(y))

    try:
        x = verifier.verify(new_hash, signature)
        print(x)
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    main()
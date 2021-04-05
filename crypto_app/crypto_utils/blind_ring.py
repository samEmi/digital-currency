from charm.toolbox.ecgroup import ECGroup, ZR, G

class UserBlindRing():
    def __init__(self, curve, P, ring_pks, l=None):
        self.group = ECGroup(curve)
        self.P = P
        self.ring_pks = ring_pks
        self.ring_size = len(self.ring_pks)
        self.u = list()
        self.v = list()
    
    def challenge_response(self, input, message):
        self.l = self.group.random(ZR)
        R_hat = [message]
        for R, Y in zip(input, self.ring_pks):
            self.u.append(self.group.random(ZR))
            self.v.append(self.group.random(ZR))
            R_hat.append((R ** l) + (self.P ** self.v[-1]) + (Y ** self.u[-1]))
        c = self.group.hash(tuple(R_hat))
        return c / l

    def gen_signature(self, proofs: dict):
        c, s = proofs['c'], proofs['s']
        c_prime, s_prime = list(), list()
        for i in range(self.ring_size):
            c_prime.append(self.l * c[i] + self.u[i])
            s_prime.append(self.l * s[i] + self.v[i])
        signature = {}
        signature['c'] = c_prime
        signature['s'] = s_prime
        return signature
 

class SignerBlindRing():
    def __init__(self, k, curve, P, pk=None, sk=None, ring_pks=None, signer_id=0):
        self.group = ECGroup(curve)
        self.P = P
        
        if pk is None:
            self.sk_ = self.group.random(ZR)
            self.pk_ = P ** self.sk_
            
        self.ring_pks = ring_pks
        self.ring_size = len(self.ring_pks)
        self.c = [0] * self.ring_size
        self.s = [0] * self.ring_size
        self.k = k
        self.signer_id = signer_id

    def get_public_key(self):
        return self.pk_

    def get_private_key(self):
        return self.sk_

    def get_challenge(self):
        R = list()
        for i in range(self.ring_size):
            if i == self.signer_id: 
                R.append(self.P ** self.k)
            else:
                self.c[i] = self.group.random(ZR)
                self.s[i] = self.group.random(ZR)
                R.append(self.P ** self.s[i]) + (self.ring_pks[i] ** self.c[i])
        
        return R

    def get_proofs(self, c_prime: int):
        c_sum = sum(self.c)
        self.c[self.signer_id] = c_prime - c_sum
        self.s[self.signer_id] = self.k - self.c[self.signer_id] * self.sk_
        proofs = {}
        proofs['c'] = self.c
        proofs['s'] = self.s
        return proofs

class VerifierBlindRing():
    def __init__(self, curve, P, ring_pks):
        self.group = ECGroup(curve)
        self.P = P
        self.ring_pks = ring_pks

    def verify(self, signature: tuple, message):
        c, s = signature['c'], signature['s']
        assert(len(c) == len(s))
        R = [message]
        for i in range(len(c)):
            c_sum += c[i]
            R.append((self.P ** s[i]) + (self.ring_pks ** c[i]))
        R_hash = self.group.hash(tuple(R))
        return R_hash == c_sum





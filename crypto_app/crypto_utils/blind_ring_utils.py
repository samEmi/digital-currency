

def setup(n, l=1, ):
    ''' PPT algorithm which takes as input security param n and outputs a set of public params P.
        - n: security parameter
        - q: polynomial prime number - poly(n)
        - d: 
        - k: 
        - m: max(64+n*log(q)/log(2d+1),5*n*log(q))
        - l: size of the ring
        - K = m^(1+e)
        - σ: real >= K·ω(sqrt(log n))
        - m: 
       
        - k: 
        
    '''
        
    #P = (n, l, m, q, k, κ, σ, H, σ1, σ2, σ3, M1, M2, M3, T, η)

    
    pass

def trapgen(n: int, m: int, q: int, K):
    A 
    return A, BA

def sample_key(A, BA, sigma, T):
    pass


def key_gen(P: dict):
    '''PPT algorithm which takes as input public params P and returns a key pair: (pk=A, sk=S).'''
    A, BA = trapgen(P['n'], P['m'], P['q'], P['K'])
    S = sample_key(A, BA, P['sigma'], P['T'])
    return (A, S)
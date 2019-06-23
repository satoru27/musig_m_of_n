import hashlib as hs
from fastecdsa import curve
import gmpy2 as gmp
from os import urandom


def schnorr_sig(x, X, m, ec=curve.secp256k1, hash = hs.sha256):
    """
    Produz uma assinatura (R,s) para a mensagem m relativa ao par de chaves privada/pública (x,X) utilizando o esquema de
    assinatura de Schnorr.
    INPUT: Domain parameters/elliptic curve, private key x, public key X, message m.
    OUTPUT: Signature (R, s)
    1. Select r ∈R [1,n −1].
    2. Compute R = rP
    3. c = H(X,R,m) -> int(c)
    4. s = r + cx
    5. Return (R,s)
    """
    r = 0
    while r == 0:
        r = gmp.mpz_random(gmp.random_state(int.from_bytes(urandom(4), byteorder='little')), ec.q)
        r = r % ec.q

    R = r*ec.G

    c = hash()
    c.update((str(X.x)+str(X.y)+str(R.x)+str(R.y)+m).encode())
    c = c.digest()  # size 48 bytes
    c = int.from_bytes(c, byteorder='little')

    s = (gmp.mpz(r) + gmp.mpz(c)*gmp.mpz(x)) % ec.q

    return R, s


def schnorr_ver(X, m, R, s, ec=curve.secp256k1, hash = hs.sha256):
    """
    Verifica se a assinatura de Schnorr (R,s) é válida para a mensagem m e a chave pública X, verificando se a equação
    sP = R + cX, para c = H(X,R,m), é válida.
    """
    c = hash()
    c.update((str(X.x) + str(X.y) + str(R.x) + str(R.y) + m).encode())
    c = c.digest()  # size 48 bytes
    c = int.from_bytes(c, byteorder='little')
    c = c % ec.q

    left = s*ec.G
    right = R + c*X

    if left.x == right.x and left.y == right.y:
        return True
    else:
        return False


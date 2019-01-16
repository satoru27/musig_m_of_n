import hashlib as hs
from fastecdsa import curve
import gmpy2 as gmp
from os import urandom
from sys import getsizeof

"""
Initialize the parameters of an elliptic curve.
       WARNING: Do not generate your own parameters unless you know what you are doing or you could
       generate a curve severely less secure than you think. Even then, consider using a
       standardized curve for the sake of interoperability.
       Currently only curves defined via the equation :math:`y^2 \equiv x^3 + ax + b \pmod{p}` are
       supported.
       Args:
           |  name (string): The name of the curve
           |  p (long): The value of :math:`p` in the curve equation.
           |  a (long): The value of :math:`a` in the curve equation.
           |  b (long): The value of :math:`b` in the curve equation.
           |  q (long): The order of the base point of the curve.
           |  gx (long): The x coordinate of the base point of the curve.
           |  gy (long): The y coordinate of the base point of the curve.
           |  oid (str): The object identifier of the curve.
"""


def key_generation(ec=curve.secp256k1):
    """
    INPUT: Domain parameters D = (q, FR, S, a, b, P, n, h).
    OUTPUT: Public key Q, private key d.
    1.Select d E R[1, n −1].
    2.Compute Q = dP.
    3.Return(Q, d)
    """
    """
    curve.Curve.G
    The base point of the curve.
    For the purposes of ECDSA this point is multiplied by a private key to obtain the
    corresponding public key. Make a property to avoid cyclic dependency of Point on Curve
    (a point lies on a curve) and Curve on Point (curves have a base point).
    """
    d = gmp.mpz_random(gmp.random_state(int.from_bytes(urandom(4), byteorder='little')), ec.q)
    Q = d*ec.G
    # d is the private key, Q is the public key

    return Q, d


def key_verification():
    """
    INPUT: Domain parameters D = (q,FR, S,a,b, P,n,h), public key Q.
    OUTPUT: Acceptance or rejection of the validity of Q.
    1. Verify that Q = infinity.
    2. Verify that xQ and yQ are properly represented elements of Fq (e.g., integers in the interval [0,q −1] if Fq is a prime field, and bit strings of length m bits if Fq is a binary field of order 2m).
    3. Verify that Q satisfies the elliptic curve equation defined by a and b.
    4. Verify that nQ = infinity.
    5. If any verification fails then return(“Invalid”); else return(“Valid”).
    """
    pass


def ecdsa_geneneration(d, m, ec=curve.secp256k1):
    """
    INPUT: Domain parameters D = (q,FR, S,a,b, P,n,h), private key d, message m.
    OUTPUT: Signature (r,s).
    1. Select k ∈R [1,n −1].
    2. Compute kP = (x1, y1) and convert x1 to an integer x1'.
    3. Compute r = x1 mod n. If r = 0 then go to step 1.
    4. Compute e = H(m).
    5. Compute s = k−1(e +dr) mod n. If s = 0 then go to step 1.
    6. Return(r,s).
    """
    r = 0
    k = 0
    while r == 0:
        k = gmp.mpz_random(gmp.random_state(int.from_bytes(urandom(4), byteorder='little')), ec.q)
        kP = k * ec.G
        x1 = kP.x
        r = x1 % ec.q
    """
    H denotes a cryptographic hash function whose outputs have
    bitlength no more than that of n (if this condition is not satisfied, then the outputs
    of H can be truncated)
    """
    e = hs.sha3_384()
    e.update(m.encode())
    e = e.digest() #size 48 bytes
    e = int.from_bytes(e, byteorder='little')
    s = (gmp.invert(k, ec.q) * (gmp.mpz(e) + gmp.mpz(d)*gmp.mpz(r))) % ec.q

    return r, s


def ecdsa_verification(Q, m, r, s, ec=curve.secp256k1):
    """
    INPUT: Domain parameters D = (q,FR, S,a,b, P,n,h), public key Q, message m, signature (r,s).
    OUTPUT: Acceptance or rejection of the signature.
    1. Verify that r and s are integers in the interval [1,n −1]. If any verification fails
    then return(“Reject the signature”).
    2. Compute e = H(m).
    3. Compute w = s−1 mod n.
    4. Compute u1 = ew mod n and u2 = rw mod n.
    5. Compute X = u1P +u2Q.
    6. If X = inf then return(“Reject the signature”);
    7. Convert the x-coordinate x1 of X to an integer x1; compute v = x1 mod n.
    8. If v = r then return(“Accept the signature”);
    Else return(“Reject the signature”).
    """
    if r < 1 or r > ec.q or s < 1 or s > ec.q:
        return False

    e = hs.sha3_384()
    e.update(m.encode())
    e = e.digest()  # size 48 bytes
    e = int.from_bytes(e, byteorder='little')

    w = gmp.invert(s, ec.q)
    u1 = (gmp.mpz(e)*w) % ec.q
    u2 = (gmp.mpz(r)*w) % ec.q

    X = u1*ec.G + u2*Q

    v = X.x % ec.q

    if v == r:
        return True
    else:
        return False


def main():
    pub_key, priv_key = key_generation()
    print('Key Generation:')
    print(pub_key)
    print(priv_key)

    print('\nECDSA:')
    r, s = ecdsa_geneneration(priv_key, 'Hello World', ec=curve.secp256k1)
    print(r)
    print(s)

    print('\nVerification:')
    ok = ecdsa_verification(pub_key, 'Hello World', r, s, ec=curve.secp256k1)
    print(ok)


if __name__ == "__main__":
    main()
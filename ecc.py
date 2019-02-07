import hashlib as hs
from fastecdsa import curve
import gmpy2 as gmp
from os import urandom
import network
from sys import getsizeof
"""
Key generation, key verification, ecdsa_geneneration, ecdsa_verification algorithms are based on the algorithms proposed
on Darrel Hankerson, Alfred Menezes and Scott Vanstone Guide to Elliptic Curve Cryptography (2004) book.

Simple schnorr signature and verification, and the naive schnorr musig and verification was based on the description
presented on Gregory Maxwell, Andrew Poelstra1, Yannick Seurin, and Pieter Wuille paper Simple Schnorr Multi-Signatures
with Applications to Bitcoin (2018)

Bellare-neven signature scheme was based on the description presented on Mihir Bellare and Gregory Neven paper 
Multi-Signatures in the Plain Public-Key Model and a General Forking Lemma (2006).

Another important paper is the one where C. P. Schnorr first proposed his signature scheme,
Efficient Signature Generation by Smart Cards (1991).

The schemes were adapted to be used with elliptic curves, especially with the curve secp256k1 (bitcoin curve)
"""
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
    5. Compute s = k^−1(e +dr) mod n. If s = 0 then go to step 1.
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
    e = e.digest() # size 48 bytes
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


def schnorr_sig(x, X, m, ec=curve.secp256k1):
    """
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

    c = hs.sha3_384()
    c.update((str(X.x)+str(X.y)+str(R.x)+str(R.y)+m).encode())
    c = c.digest()  # size 48 bytes
    c = int.from_bytes(c, byteorder='little')

    s = (gmp.mpz(r) + gmp.mpz(c)*gmp.mpz(x)) % ec.q

    return R, s


def schnorr_ver(X, m, R, s, ec=curve.secp256k1):
    """
    Verify if sP = R + cX
    """
    c = hs.sha3_384()
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


def naive_schnorr_musig(m, *args, ec=curve.secp256k1):
    # args = [(pub_key, priv_key,)]
    i = 1
    r_list = []
    rpoint_list = []
    rpoint_sum = None
    pub_key_sum = None

    for keys in args:
        #print(keys)
        #print('\n-------------------------------------------\n')
        #print(f'Signer {i} process:')
        r = 0
        while r == 0:
            r = gmp.mpz_random(gmp.random_state(int.from_bytes(urandom(4), byteorder='little')), ec.q)
            r = r % ec.q
        r_list.append(r)
        print(f'Generated r{i} = {r_list[i-1]}')
        rpoint = r*ec.G
        rpoint_list.append(rpoint)
        print(f'Generated R{i} = ({rpoint_list[i-1]})')

        if i == 1:
            rpoint_sum = rpoint
            pub_key_sum = keys[0]
        else:
            rpoint_sum += rpoint
            pub_key_sum += keys[0]

        i += 1

    print(f'Sum of all Ri is R = {rpoint_sum}')
    print(f'Sum of all public keys X is X\'= {pub_key_sum} ')

    c = hs.sha3_384()
    c.update((str(pub_key_sum.x) + str(pub_key_sum.y) + str(rpoint_sum.x) + str(rpoint_sum.y) + m).encode())
    c = c.digest()  # size 48 bytes
    c = int.from_bytes(c, byteorder='little')
    c = c % ec.q  # necessario ?

    print(f'Hash result c = {c}')

    i = 1
    partial_signatures = []
    s = gmp.mpz(0)
    for keys in args:
        s_i = (r_list[i-1] + gmp.mpz(c) * gmp.mpz(keys[1])) % ec.q
        partial_signatures.append(s_i)
        print(f'Partial signature s{i} = {partial_signatures[i-1]}')
        s = (s + s_i) % ec.q
        i += 1

    print(f'Sum of the signatures = {s}')

    return rpoint_sum, s


def naive_schnorr_musig_ver(R, s, m, *args, ec=curve.secp256k1):
    """
        Verify if sP = R + cX'
    """
    first = True
    pub_key_sum = None
    for pub_key in args:
        if first:
            pub_key_sum = pub_key
            first = False
        else:
            pub_key_sum += pub_key

    c = hs.sha3_384()
    c.update((str(pub_key_sum.x) + str(pub_key_sum.y) + str(R.x) + str(R.y) + m).encode())
    c = c.digest()  # size 48 bytes
    c = int.from_bytes(c, byteorder='little')
    c = c % ec.q

    left = s * ec.G
    right = R + c * pub_key_sum

    if left.x == right.x and left.y == right.y:
        return True
    else:
        return False


def rogue_key_attack(rogue_key, *args, ec=curve.secp256k1):

    print(f'Target X value is: {rogue_key}')

    first = True
    pub_keys_sum = None

    for key in args:
        if first:
            pub_keys_sum = key
            first = False
        else:
            pub_keys_sum += key

    print(f'Sum of other public keys is: {pub_keys_sum}')
    pub_keys_sum_inv = -pub_keys_sum

    print(f'Inverse of the sum of target public keys is: {pub_keys_sum_inv}')
    final_rogue_key = rogue_key + pub_keys_sum_inv

    print(f'X1 value: {final_rogue_key}')
    x_result = final_rogue_key + pub_keys_sum
    print(f'Final public key result: {x_result}')

    if rogue_key.x == x_result.x and rogue_key.y == x_result.y:
        equal = True
    else:
        equal = False

    print(f'Equal: {equal}')

    return


def bellare_neven_musign(m, *args, ec=curve.secp256k1):
    # args = [(pub_key, priv_key,)]
    i = 1
    r_list = []
    rpoint_list = []
    rpoint_sum = None

    public_key_list = ''

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    # quicksort or some other adequate sorting algorithm will be implemented here
    # for now, the order is just the received order (which here is the same for all signers)
    for keys in args:
        public_key_list = public_key_list + ',' + str(keys[0])

    # multiple iterations will be used for clarity in the interpretation of the algorithm
    for keys in args:

        r = 0

        while r == 0:
            r = gmp.mpz_random(gmp.random_state(int.from_bytes(urandom(4), byteorder='little')), ec.q)
            r = r % ec.q

        r_list.append(r)
        print(f'Generated r{i} = {r_list[i - 1]}')

        rpoint = r * ec.G
        rpoint_list.append(rpoint)
        print(f'Generated R{i} = ({rpoint_list[i - 1]})\n')

        if i == 1:
            rpoint_sum = rpoint
        else:
            rpoint_sum += rpoint

        i += 1

    print(f'R = {rpoint_sum}\n')

    hash_list = []
    signature_list = []
    s_sum = gmp.mpz(0)
    i = 0
    for keys in args:
        #c = None
        c = hs.sha3_384()
        c.update((str(keys[0].x) + str(keys[0].y) + str(rpoint_sum.x) + str(rpoint_sum.y) + public_key_list + m).encode())
        c = c.digest()  # size 48 bytes
        c = int.from_bytes(c, byteorder='little')
        c = c % ec.q
        hash_list.append(c)
        print(f'c{i+1} = {c}')

        s = (gmp.mpz(keys[1])*gmp.mpz(c) + gmp.mpz(r_list[i])) % ec.q
        signature_list.append(s)
        print(f's{i + 1} = {s}\n')
        s_sum = (s_sum + s) % ec.q
        i += 1

    print(f's = {s_sum}\n')
    print(f'Signature (R,s) is: ({rpoint_sum},{s_sum})\n')
    return rpoint_sum, s_sum


def bellare_neven_musign_ver(R, s, m, *args, ec=curve.secp256k1):
    # args = [pub_key1,...,pub_keyn]
    public_key_list = ''

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    # quicksort or some other adequate sorting algorithm will be implemented here
    # for now, the order is just the received order (which here is the same for all signers)
    for key in args:
        public_key_list = public_key_list + ',' + str(key)

    i = 0
    hash_list = []
    c_pub_key = None
    first = True

    for key in args:
        #c = None
        c = hs.sha3_384()
        c.update((str(key.x) + str(key.y) + str(R.x) + str(R.y) + public_key_list + m).encode())
        c = c.digest()  # size 48 bytes
        c = int.from_bytes(c, byteorder='little')
        c = c % ec.q
        hash_list.append(c)
        print(f'c{i+1} = {c}\n')

        if first:
            c_pub_key = c*key
            first = False
        else:
            c_pub_key = c_pub_key + c*key

        i += 1

    left = s * ec.G
    right = R + c_pub_key

    if left.x == right.x and left.y == right.y:
        return True
    else:
        return False


def musig(m, *args, ec=curve.secp256k1):
    # args = [(pub_key, priv_key,)]

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    # quicksort or some other adequate sorting algorithm will be implemented here
    # for now, the order is just the received order (which here is the same for all signers)

    # gambiarra
    if isinstance(args[0], list):
        args = args[0]

    public_key_list = ''
    for keys in args:
        public_key_list = public_key_list + ',' + str(keys[0])

    i = 0
    # computing ai = Hagg(L,Xi)
    a_list = []
    for keys in args:
        a = hs.sha3_384()
        a.update((public_key_list+str(keys[0].x) + str(keys[0].y)).encode())
        a = a.digest()  # size 48 bytes
        a = int.from_bytes(a, byteorder='little')
        a = a % ec.q
        a_list.append(a)
        print(f'a{i+1} = {a_list[i]}')
        i += 1

    #calculating X = sum(ai*Xi)
    i = 1
    first = True
    aggregated_key = None
    for keys in args:
        if first:
            aggregated_key = a_list[0]*keys[0]
            first = False
            print(f'X += a{i}*X{i}')
        else:
            aggregated_key += a_list[i]*keys[0]
            print(f'X += a{i+1}*X{i+1}')
            i += 1

    print(f'Aggregated key is: {aggregated_key}')

    # generate r1 and compute R1 = r1P
    # calculate and send Ri commitment
    r_list = []
    rpoint_list = []
    commit_list = []
    i = 1
    for keys in args:
        r = 0
        while r == 0:
            r = gmp.mpz_random(gmp.random_state(int.from_bytes(urandom(4), byteorder='little')), ec.q)
            r = r % ec.q
        r_list.append(r)
        print(f'Generated r{i} = {r_list[i - 1]}')

        rpoint = r * ec.G
        rpoint_list.append(rpoint)
        print(f'Generated R{i} = ({rpoint_list[i - 1]})')

        t = hs.sha3_384()
        t.update((str(rpoint.x)+str(rpoint.y)).encode())
        t = t.digest()  # size 48 bytes
        # t = int.from_bytes(t, byteorder='little')
        commit_list.append(t)
        print(f'Generated t{i} = ({commit_list[i - 1]})\n')
        i += 1

    # checking the commited t with respective R
    # in this implementation this is redundant but will be necessary once the communication isn't centralized
    i = 0
    ok = True
    for keys in args:
        t = hs.sha3_384()
        t.update((str(rpoint_list[i].x) + str(rpoint_list[i].y)).encode())
        t = t.digest()  # size 48 bytes

        if t != commit_list[i]:
            ok = False

        i += 1
    print(f'Commit ok: {ok}\n')

    # computing R = sum(Ri)
    rpoint_sum = None
    first = True
    for rpoint in rpoint_list:
        if first:
            rpoint_sum = rpoint
            first = False
        else:
            rpoint_sum += rpoint

    print(f'R = {rpoint_sum}\n')

    # computing the challenge c = Hsig(X', R, m)
    c = hs.sha3_384()
    c.update((str(aggregated_key.x) + str(aggregated_key.y) + str(rpoint_sum.x) + str(rpoint_sum.y) + m).encode())
    c = c.digest()  # size 48 bytes
    c = int.from_bytes(c, byteorder='little')
    c = c % ec.q

    print(f'c = {c}\n')

    # computing s1 = r1 + c*a1*x1 mod p
    i = 0
    s_list = []
    for keys in args:
        si = (gmp.mpz(r_list[i]) + gmp.mpz(c) * gmp.mpz(a_list[i]) * gmp.mpz(keys[1])) % ec.q
        s_list.append(si)
        print(f's{i+1} = {s_list[i]}')
        i += 1

    # computing s = sum(si) mod n
    i = 0
    s = gmp.mpz(0)
    for keys in args:
        s += s_list[i]
        i += 1
    s = s % ec.q
    print(f'\ns = {s}\n')

    # signature is (R,s)
    return rpoint_sum, s


def musig_ver(R, s, m, *args, ec=curve.secp256k1):
    # args = [pub_key_1,...,pub_key_k]

    # gambiarra
    if isinstance(args[0], list):
        args = args[0]

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    # quicksort or some other adequate sorting algorithm will be implemented here
    # for now, the order is just the received order (which here is the same for all signers)
    public_key_list = ''
    for key in args:
        public_key_list = public_key_list + ',' + str(key)

    # computing ai = Hagg(L,Xi)
    i = 0
    a_list = []
    for key in args:
        a = hs.sha3_384()
        a.update((public_key_list + str(key.x) + str(key.y)).encode())
        a = a.digest()  # size 48 bytes
        a = int.from_bytes(a, byteorder='little')
        a = a % ec.q
        a_list.append(a)
        print(f'a{i + 1} = {a_list[i]}')
        i += 1

    # calculating X = sum(ai*Xi)
    i = 1
    first = True
    aggregated_key = None
    for key in args:
        if first:
            aggregated_key = a_list[0] * key
            first = False
            print(f'X += a{i}*X{i}')
        else:
            aggregated_key += a_list[i] * key
            print(f'X += a{i + 1}*X{i + 1}')
            i += 1
    print(f'Aggregated key is: {aggregated_key}')

    # computing the challenge c = Hsig(X', R, m)
    c = hs.sha3_384()
    c.update((str(aggregated_key.x) + str(aggregated_key.y) + str(R.x) + str(R.y) + m).encode())
    c = c.digest()  # size 48 bytes
    c = int.from_bytes(c, byteorder='little')
    c = c % ec.q
    print(f'c = {c}\n')

    # checking if sP = R + sum(ai*c*Xi) = R + c*X'
    left = s*ec.G
    right = R + c*aggregated_key

    if left.x == right.x and left.y == right.y:
        return True
    else:
        return False


def musig_distributed(m, user_key, pub_keys, address_dict, ec=curve.secp256k1, hash = hs.sha256):
    # user_key = (priv key, pub key)
    # pub_keys = (None, pub key)
    # address_dict = {pubkey:(ip,port)}

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    # quicksort or some other adequate sorting algorithm will be implemented here
    # for now, the order is just the received order (which here is the same for all signers)


    pub_keys.insert(0, user_key[1])

    public_key_l = ''

    for key in pub_keys:
        public_key_l = public_key_l + ',' + str(key)

    type(public_key_l)
    print(public_key_l)

    i = 0
    a_list = []

    for key in pub_keys:
        a = hash()
        a.update((public_key_l + str(key.x) + str(key.y)).encode())
        a = a.digest()  # size 48 bytes
        a = int.from_bytes(a, byteorder='little')
        a = a % ec.q
        a_list.append(a)
        print(f'a{i + 1} = {a_list[i]}')
        i += 1

    print(a_list)

    i = 1
    first = True
    aggregated_key = None
    for key in pub_keys:
        if first:
            aggregated_key = a_list[0] * key
            first = False
            print(f'X += a{i}*X{i}')
        else:
            aggregated_key += a_list[i] * key
            print(f'X += a{i + 1}*X{i + 1}')
            i += 1

    print(aggregated_key)

    r = 0
    while r == 0:
        r = gmp.mpz_random(gmp.random_state(int.from_bytes(urandom(4), byteorder='little')), ec.q)
        r = r % ec.q
    print(f'Generated r = {r}')
    r_point = r * ec.G
    print(f'Generated R = ({r_point})')

    t = hash()
    t.update((str(r_point.x) + str(r_point.y)).encode())
    t = t.hexdigest()  # size 48 bytes
    # t = int.from_bytes(t, byteorder='little')
    print(f'Generated t = ({t})\n')

    commit = str(user_key[1]) + ':' + str(t)

    print(commit)
    # X: 0xc1c1d0590e2aa499ad285b17415f9dd3005a97f4d2dfef05e5687d76150ec65f
    # Y: 0x280f8e5605faa8fe66fbf1221b75240dbb3ff6370bd9030ec4364809e8a0c77f
    # (On curve <secp256k1>):beb23659edbf8912aad141291f74791badd7d865d220aed2324a6a3b55eddfd4

    # send to signers
    iterable = []
    for key, address in address_dict.items():
        temp = (address, commit)
        iterable.append(temp)

    network.multi_thread_send_t(iterable)

    # receive from other signers
    # colocar antes de mandar para ja esperar se necessario ?



def main():
    pub_key, priv_key = key_generation()
    #print('Key Generation:')
    #print(pub_key)
    #print(priv_key)

    pub_key2, priv_key2 = key_generation()
    pub_key3, priv_key3 = key_generation()
    pub_key4, priv_key4 = key_generation()

    #print('\nECDSA:')
    #r, s = ecdsa_geneneration(priv_key, 'Hello World', ec=curve.secp256k1)
    #print(r)
    #print(s)

    #print('\nVerification:')
    #ok = ecdsa_verification(pub_key, 'Hello World', r, s, ec=curve.secp256k1)
    #print(ok)

    #print('Schnorr signature:')
    #R, s = schnorr_sig(priv_key, pub_key, 'Hello Worlds5434v3tv4tv4', ec=curve.secp256k1)
    #print(R)
    #print(s)

    #print('Schnorr signature verification')
    #result = schnorr_ver(pub_key2, 'Hello Worlds5434v3tv4tv4', R, s, ec=curve.secp256k1)
    #print(result)

    #R, s = naive_schnorr_musig('Hello Worlds5434v3tv4tv4', (pub_key, priv_key,), (pub_key2, priv_key2), (pub_key3, priv_key3), (pub_key4, priv_key4))

    #result = naive_schnorr_musig_ver(R, s, 'Hello Worlds5434v3tv4tv4', pub_key, pub_key2, pub_key3, pub_key4)

    #print(f'Verification result: {result}')

    #rogue_key_attack(pub_key, pub_key2, pub_key3, pub_key4)
    #print('Bellare-Neven MuSign scheme: ')
    #R, s = bellare_neven_musign('Hello Worlds5434v3tv4tv4', (pub_key, priv_key), (pub_key2, priv_key2), (pub_key3, priv_key3), (pub_key4, priv_key4))
    #print('Bellare-Neven MuSign scheme verification: ')
    #result = bellare_neven_musign_ver(R, s, 'Hello Worlds5434v3tv4tv4', pub_key, pub_key2, pub_key3, pub_key4)
    #print(f'Verification result: {result}')

    # m = 'Hello Worlds5434v3tv4tv4'
    # print('MuSig scheme: ')
    # R, s = musig(m, (pub_key, priv_key), (pub_key2, priv_key2), (pub_key3, priv_key3), (pub_key4, priv_key4))
    # print('MuSig scheme verification: ')
    # result = musig_ver(R, s, m, pub_key, pub_key2, pub_key3, pub_key4)
    # print(f'Verification result: {result}')

    import keystorage

    my_key = keystorage.import_keys('k2.pem')
    key2 = keystorage.import_keys('key2.pem')
    key3 = keystorage.import_keys('key4.pem')
    key4 = keystorage.import_keys('key90.pem')

    key2 = (None, key2[1])
    key3 = (None, key3[1])
    key4 = (None, key4[1])

    addr2 = ('127.0.0.1', 2437)
    addr3 = ('127.0.0.1', 2438)
    addr4 = ('127.0.0.1', 2439)

    m = 'teste39826c4b39'

    address_dict = {str(key2[1]): addr2, str(key3[1]): addr3, str(key4[1]): addr4}

    pub_key_lst = [key2[1], key3[1], key4[1]]

    musig_distributed(m, my_key, pub_key_lst, address_dict, ec=curve.secp256k1)






if __name__ == "__main__":
    main()


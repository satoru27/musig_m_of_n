import hashlib as hs
from fastecdsa import curve
import gmpy2 as gmp
from os import urandom
import pointsort
import p2pnetwork
import re
from fastecdsa import point


def musig(m, my_key, key_lst, ec=curve.secp256k1):
    # my_key = (priv key, pub key)
    # key_lst = [(priv key1, pub key1), (priv key2, pub key2)]

    key_dict = {}
    key_lst.append(my_key)
    for key in key_lst:
        key_dict[str(key[1])] = key[0]

    pub_keys = []
    for key in key_lst:
        pub_keys.append(key[1])

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    pointsort.sort(pub_keys)
    print(f'\nPUB KEYS ORDER: {pub_keys}\n')

    public_key_list = ''
    for key in pub_keys:
        public_key_list = public_key_list + '|' + str(key)

    i = 0
    # computing ai = Hagg(L,Xi)
    a_list = []
    for key in pub_keys:
        print(key)
        a = hs.sha256()
        a.update((public_key_list+str(key.x) + str(key.y)).encode())
        a = a.digest()  # size 48 bytes
        a = int.from_bytes(a, byteorder='little')
        a = a % ec.q
        a_list.append(a)
        print(f'a{i+1} = {a_list[i]}')
        i += 1
    print(f'\nA LIST: {a_list}\n')

    #calculating X = sum(ai*Xi)
    i = 1
    first = True
    aggregated_key = None
    for key in pub_keys:
        if first:
            aggregated_key = a_list[0]*key
            first = False
            print(f'X += a{i}*X{i}')
        else:
            aggregated_key += a_list[i]*key
            print(f'X += a{i+1}*X{i+1}')
            i += 1

    print(f'AGGREGATED KEY: {aggregated_key}')

    # generate r1 and compute R1 = r1P
    # calculate and send Ri commitment
    r_list = []
    rpoint_list = []
    commit_list = []
    i = 1
    for key in pub_keys:
        r = 0
        while r == 0:
            r = gmp.mpz_random(gmp.random_state(int.from_bytes(urandom(4), byteorder='little')), ec.q)
            r = r % ec.q
        r_list.append(r)
        #print(f'Generated r{i} = {r_list[i - 1]}')

        rpoint = r * ec.G
        rpoint_list.append(rpoint)
        #print(f'Generated R{i} = ({rpoint_list[i - 1]})')

        t = hs.sha256()
        t.update((str(rpoint.x)+str(rpoint.y)).encode())
        t = t.digest()  # size 48 bytes
        # t = int.from_bytes(t, byteorder='little')
        commit_list.append(t)
        #print(f'Generated t{i} = ({commit_list[i - 1]})\n')
        i += 1

    # checking the commited t with respective R
    # in this implementation this is redundant but will be necessary once the communication isn't centralized
    i = 0
    ok = True
    for key in pub_keys:
        t = hs.sha256()
        t.update((str(rpoint_list[i].x) + str(rpoint_list[i].y)).encode())
        t = t.digest()  # size 48 bytes

        if t != commit_list[i]:
            ok = False

        i += 1
    #print(f'Commit ok: {ok}\n')

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
    c = hs.sha256()
    c.update((str(aggregated_key.x) + str(aggregated_key.y) + str(rpoint_sum.x) + str(rpoint_sum.y) + m).encode())
    c = c.digest()  # size 48 bytes
    c = int.from_bytes(c, byteorder='little')
    c = c % ec.q

    print(f'c = {c}\n')

    # computing s1 = r1 + c*a1*x1 mod p
    i = 0
    s_list = []
    for key in pub_keys:
        si = (gmp.mpz(r_list[i]) + gmp.mpz(c) * gmp.mpz(a_list[i]) * gmp.mpz(key_dict[str(key)])) % ec.q
        s_list.append(si)
        print(f's{i+1} = {s_list[i]}')
        i += 1

    # computing s = sum(si) mod n
    i = 0
    s = gmp.mpz(0)
    for key in pub_keys:
        s += s_list[i]
        i += 1
    s = s % ec.q
    print(f'\ns = {s}\n')

    # signature is (R,s)
    return rpoint_sum, s


def musig_ver(R, s, m, pub_keys, ec=curve.secp256k1):
    # R: elliptic curve point
    # s: int/mpz
    # m: string
    # pub_key: elliptic curve point
    # pub_keys: [pub_key_1,...,pub_key_k]
    # ec: elliptic curve

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    pointsort.sort(pub_keys)
    print(f'\nPUB KEYS ORDER: {pub_keys}\n')

    public_key_list = ''
    for key in pub_keys:
        public_key_list = public_key_list + ',' + str(key)

    # computing ai = Hagg(L,Xi)
    i = 0
    a_list = []
    for key in pub_keys:
        a = hs.sha256()
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
    for key in pub_keys:
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
    c = hs.sha256()
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


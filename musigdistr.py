import hashlib as hs
from fastecdsa import curve
import gmpy2 as gmp
from os import urandom
import pointsort
import p2pnetwork
import re
from fastecdsa import point
import os

SEPARATOR = '|'
CURVES = {"secp256k1": curve.secp256k1, "secp224k1": curve.secp224k1, "brainpoolP256r1": curve.brainpoolP256r1,
              "brainpoolP384r1": curve.brainpoolP384r1, "brainpoolP512r1": curve.brainpoolP512r1}

def point_from_str(input):
    x_value = re.search('X:(.*)\\nY:', input).group(1).strip(' ')
    y_value = re.search('Y:(.*)\\n\\(', input).group(1).strip(' ')
    curve_name = re.search('<(.*)>', input).group(1).strip(' ')

    print(x_value)
    print(y_value)
    print(curve_name)

    return point.Point(int(x_value, 0), int(y_value, 0), CURVES[curve_name])

def validate(commit_rcv, r_point_rcv, hash = hs.sha256):
    # pub_key = re.search('(.*)\\|', input).group(1).strip(' ')
    # commit = re.search('\\|(.*)', input).group(1).strip(' ')
    # print(pub_key)
    # print(commit)
    pub_key1, commit = commit_rcv.split('|')
    pub_key2, r_point = r_point_rcv.split('|')

    r_point = point_from_str(r_point)

    t = hash()
    t.update((str(r_point.x) + str(r_point.y)).encode())
    t = t.hexdigest()

    if commit == str(t):
        return True
    else:
        return False

def check_commits(commit_list, r_point_list, hash = hs.sha256):
    for commit, r_point in zip(commit_list,r_point_list):
        result = validate(commit, r_point, hash)
        print(result)
        if not result: # if not true
            return False
    return True



def musig_distributed(m, user_key, pub_keys, address_dict, hostname, port, ec=curve.secp256k1, hash = hs.sha256):
    # user_key = (priv key, pub key)
    # pub_keys = [pub key
    # address_dict = {pubkey:(ip,port)}

    pub_keys.insert(0, user_key[1])

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    # quicksort or some other adequate sorting algorithm will be implemented here
    # for now, the order is just the received order (which here is the same for all signers)

    pointsort.sort(pub_keys)

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

    commit = str(user_key[1]) + SEPARATOR + str(t)

    print(commit)
    # X: 0xc1c1d0590e2aa499ad285b17415f9dd3005a97f4d2dfef05e5687d76150ec65f
    # Y: 0x280f8e5605faa8fe66fbf1221b75240dbb3ff6370bd9030ec4364809e8a0c77f
    # (On curve <secp256k1>):beb23659edbf8912aad141291f74791badd7d865d220aed2324a6a3b55eddfd4

    peer_list = []
    #print('\n------------\n')
    for key in pub_keys:
        try:
            peer_list.append(address_dict[str(key)])
        except KeyError:
            peer_list.append((hostname, port))

    print(address_dict)
    print('\n')
    print(pub_keys)
    print('\n')
    print(peer_list)

    # send to signers
    print('\n>>> SENDING AND RECEIVING T <<<\n')
    t_list_rcv = p2pnetwork.p2p_get((hostname, port), peer_list, commit)
    print('\n>>> SENDING AND RECEIVING R <<<\n')
    r_point_package = str(user_key[1]) + SEPARATOR + str(r_point)
    r_point_list_rcv = p2pnetwork.p2p_get((hostname, port), peer_list, r_point_package)

    print('\n>>> T LIST <<<\n')
    print(t_list_rcv)
    print('\n>>> R POINT LIST <<<\n')
    print(r_point_list_rcv)

    os.system('clear')
    ok = check_commits(t_list_rcv, r_point_list_rcv, hash = hs.sha256)
    print('Result>>>>>>>>>>>>')
    print(ok)

    

    # receive from other signers
    # colocar antes de mandar para ja esperar se necessario ?
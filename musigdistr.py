import hashlib as hs
from fastecdsa import curve
import gmpy2 as gmp
from os import urandom
import pointsort
import p2pnetwork
import re
from fastecdsa import point
import merkle

SEPARATOR = '|'
CURVES = {"secp256k1": curve.secp256k1, "secp224k1": curve.secp224k1, "brainpoolP256r1": curve.brainpoolP256r1,
              "brainpoolP384r1": curve.brainpoolP384r1, "brainpoolP512r1": curve.brainpoolP512r1}

def point_from_str(input):
    x_value = re.search('X:(.*)\\nY:', input).group(1).strip(' ')
    y_value = re.search('Y:(.*)\\n\\(', input).group(1).strip(' ')
    curve_name = re.search('<(.*)>', input).group(1).strip(' ')

    #print(x_value)
    #print(y_value)
    #print(curve_name)

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
    #t = int.from_bytes(t, byteorder='little')

    if commit == str(t):
        return True
    else:
        return False

def check_commits(commit_list, r_point_list, hash = hs.sha256):
    for commit, r_point in zip(commit_list,r_point_list):
        result = validate(commit, r_point, hash)
        #print(result)
        if not result: # if not true
            return False
    return True


def r_point_list_to_dict(r_point_list):
    temp = {}
    for item in r_point_list:
        pub_key, r_point = item.split(SEPARATOR)
        r_point = point_from_str(r_point)
        temp[pub_key] = r_point

    return temp

def s_list_to_dict(s_list):
    temp = {}
    for item in s_list:
        pub_key, sig = item.split(SEPARATOR)
        temp[pub_key] = int(sig)
    return temp

def calculate_ai(pub_keys, public_key_string, mod, hash):
    temp = {}
    for key in pub_keys:
        a = hash()
        a.update((public_key_string + str(key.x) + str(key.y)).encode())
        a = a.digest()
        a = int.from_bytes(a, byteorder='little')
        a = a % mod
        temp[str(key)] = a
    return temp


def calculate_aggregated_key(pub_keys, a_dict):
    aggregated_key = a_dict[str(pub_keys[0])]*pub_keys[0]
    for key in pub_keys[1:]:
        aggregated_key += a_dict[str(key)]*key
    return aggregated_key


def compute_challenge(aggregated_key, r_point, m, mod, hash):
    c = hash()
    c.update((str(aggregated_key.x) + str(aggregated_key.y) + str(r_point.x) + str(r_point.y) + m).encode())
    c = c.digest()
    c = int.from_bytes(c, byteorder='little')
    c = c % mod
    return c

def musig_distributed(m, user_key, pub_keys_entry, address_dict, hostname, port, ec=curve.secp256k1, hash = hs.sha256, complete_pub_keys_list = None):
    # m: string
    # priv key: int/mpz
    # pub key: elliptic curve point
    # user_key: (priv key, pub key)
    # pub_keys_entry: [pub key1, pub_key2,...]
    # address_dict = {str(pubkey):(ip,port), ...}
    # hostname: string
    # port: int
    # ec: elliptic curve
    # hash: hash function

    a_dict = {}
    commit_dict = {}
    r_point_dict = {}
    partial_signature_dict = {}
    s_dict = {}

    pub_keys = pub_keys_entry.copy()
    pub_keys.append(user_key[1])

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    pointsort.sort(pub_keys)
    print(f'\nPUB KEYS ORDER: {pub_keys}\n')

    if complete_pub_keys_list is None:
        complete_pub_keys_list = pub_keys.copy()
    else:
        pointsort.sort(complete_pub_keys_list)

    # string of all pub keys to be used in the hash
    public_key_string = str(complete_pub_keys_list)
    print(f'\nPUB KEY STRING: {public_key_string}\n')

    # generating ai = Hagg(L,Xi)
    a_dict = calculate_ai(pub_keys, public_key_string, ec.q, hash)
    print(f'\nA DICT: {a_dict}\n')

    # calculating the aggregated key
    aggregated_key = calculate_aggregated_key(pub_keys, a_dict)
    print(f'\nAGGREGATED KEY: {aggregated_key}\n')

    # generating r:
    my_r = 0
    while my_r == 0:
        my_r = gmp.mpz_random(gmp.random_state(int.from_bytes(urandom(4), byteorder='little')), ec.q)
        my_r = my_r % ec.q
    print(f'\nMY r: {my_r}\n')

    # generating R:
    my_r_point = my_r * ec.G
    print(f'\nMY R POINT: {my_r_point}\n')

    # generating the commit
    my_t = hash()
    my_t.update((str(my_r_point.x) + str(my_r_point.y)).encode())
    my_t = my_t.hexdigest()
    #my_t = int.from_bytes(my_t, byteorder='little')
    print(f'\nMY T = ({my_t})\n')

    # concatenating the pub key with the commit
    commit = str(user_key[1]) + SEPARATOR + str(my_t)

    # generating the ordered peer list to send and receive the commits
    peer_list = []
    for key in pub_keys:
        try:
            peer_list.append(address_dict[str(key)])
        except KeyError:
            peer_list.append((hostname, port))
    print(f'\nPEER LIST: {peer_list}\n')

    # send and receive the commits
    commit_list = p2pnetwork.p2p_get((hostname, port), peer_list, commit)
    print(f'\nCOMMIT LIST: {commit_list}\n')

    # concatenating the pub key with the r point
    r_point_package = str(user_key[1]) + SEPARATOR + str(my_r_point)

    # sending and receiving the R points
    r_point_list = p2pnetwork.p2p_get((hostname, port), peer_list, r_point_package)
    print(f'\nR POINT LIST: {r_point_list}\n')

    # check the R points with the commits
    ok = check_commits(commit_list, r_point_list, hash=hs.sha256)
    print(f'OK = {ok}')

    # if the commit doesn't match with the R, exit
    if not ok:
        print('R isn\'t valid')
        return 0, 0

    # generating a r point dictionary from the list
    r_point_dict = r_point_list_to_dict(r_point_list)
    print(f'\nR POINT DICT: {r_point_dict}\n')

    # calculating the sum of the r points
    r_point = r_point_dict[str(pub_keys[0])]
    for key in pub_keys[1:]:
        r_point += r_point_dict[str(key)]
    print(f'\nR POINT: {r_point}\n')

    # computing the challenge c = Hsig(X', R, m)
    c = compute_challenge(aggregated_key, r_point, m, ec.q , hash)
    print(f'\nCHALLENGE: {c}\n')

    # calculating the partial signature s1
    my_s = (gmp.mpz(my_r) + gmp.mpz(c) * gmp.mpz(a_dict[str(user_key[1])]) * gmp.mpz(user_key[0])) % ec.q
    print(f'\nMY S: {my_s}\n')

    # sending s1 and receiving si
    s_package = str(user_key[1]) + SEPARATOR + str(my_s)
    s_list = p2pnetwork.p2p_get((hostname, port), peer_list, s_package)
    print(f'\nS LIST: {s_list}\n')

    s_dict = s_list_to_dict(s_list)
    print(f'\nS DICT: {s_dict}\n')

    signature = gmp.mpz(0)
    for key in pub_keys:
        signature += s_dict[str(key)]

    signature = signature % ec.q
    print(f'\nSIGNATURE: {signature}\n')

    return r_point, signature

def musig_ver(R, s, m, pub_keys_entry, ec=curve.secp256k1, hash = hs.sha256, complete_pub_keys_list = None):
    # R: elliptic curve point
    # s: int/mpz
    # m: string
    # pub_key: elliptic curve point
    # pub_keys_entry: [pub_key_1,...,pub_key_k]
    # ec: elliptic curve
    # hash: hash function

    pub_keys = pub_keys_entry.copy()

    a_dict = {}

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    pointsort.sort(pub_keys)
    print(f'\nPUB KEYS ORDER: {pub_keys}\n')

    if complete_pub_keys_list is None:
        complete_pub_keys_list = pub_keys.copy()
    else:
        pointsort.sort(complete_pub_keys_list)

    # string of all pub keys to be used in the hash
    public_key_string = str(complete_pub_keys_list)
    # for key in pub_keys:
    #     public_key_string = public_key_string + SEPARATOR + str(key)
    print(f'\nPUB KEY STRING: {public_key_string}\n')

    # generating ai = Hagg(L,Xi)
    a_dict = calculate_ai(pub_keys, public_key_string, ec.q, hash)

    print(f'\nA DICT: {a_dict}\n')

    # calculating the aggregated key
    aggregated_key = calculate_aggregated_key(pub_keys, a_dict)
    print(f'\nAGGREGATED KEY: {aggregated_key}\n')

    # computing the challenge c = Hsig(X', R, m)
    c = compute_challenge(aggregated_key,R,m,ec.q,hash)
    print(f'\nCHALLENGE: {c}\n')

    # checking if sP = R + sum(ai*c*Xi) = R + c*X'
    left = s * ec.G
    print(f'\nsP: {left}\n')
    right = R + c * aggregated_key
    print(f'\nR + c*X: {right}\n')

    if left.x == right.x and left.y == right.y:
        return True
    else:
        return False


def musig_ver_with_key_verification(R, s, m, pub_keys_entry, signing_pub_key, proof, root=None, complete_pub_key_lst=None,
                                    restrictions=None,ec=curve.secp256k1, hash=hs.sha256):
    # R: elliptic curve point
    # s: int/mpz
    # m: string
    # pub_key: elliptic curve point
    # pub_keys: [pub_key_1,...,pub_key_k]
    # ec: elliptic curve

    key_ok = False

    if root is None:

        if complete_pub_key_lst is None:
            complete_pub_key_lst = pub_keys_entry

        print(80*'-')
        print(f'RESTRICTIONS: {restrictions}')

        merkle_tree = merkle.build_merkle_tree(complete_pub_key_lst, sorted_keys=False, restrictions=restrictions)

        key_ok = merkle.verify(merkle_tree[0], signing_pub_key, proof)

    else:

        key_ok = merkle.verify(root, signing_pub_key, proof)

    if not key_ok:
        print('KEY VERIFICATION FAILED')
        return False

    return musig_ver(R, s, m, pub_keys_entry, ec=ec, hash=hash, complete_pub_key_lst = complete_pub_key_lst)



def musig_distributed_with_key_verification(m, user_key, pub_keys_entry, address_dict, hostname, port, ec=curve.secp256k1, hash = hs.sha256, complete_pub_keys_list=None, restrictions=None):
    # m: string
    # priv key: int/mpz
    # pub key: elliptic curve point
    # user_key: (priv key, pub key)
    # pub_keys_entry: [pub key1, pub_key2,...]
    # address_dict = {str(pubkey):(ip,port), ...}
    # hostname: string
    # port: int
    # ec: elliptic curve
    # hash: hash function

    a_dict = {}
    commit_dict = {}
    r_point_dict = {}
    partial_signature_dict = {}
    s_dict = {}

    pub_keys = pub_keys_entry.copy()
    pub_keys.append(user_key[1])

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    pointsort.sort(pub_keys)
    print(f'\nPUB KEYS ORDER: {pub_keys}\n')

    if complete_pub_keys_list is None:
        complete_pub_keys_list = pub_keys.copy()
    else:
        pointsort.sort(complete_pub_keys_list)

    # string of all pub keys to be used in the hash
    #public_key_string = str(pub_keys)
    # ****************
    public_key_string = str(complete_pub_keys_list)
    print(f'\nPUB KEY STRING: {public_key_string}\n')

    # generating ai = Hagg(L,Xi)
    #a_dict = calculate_ai(pub_keys, public_key_string, ec.q, hash)
    # ****************
    a_dict = calculate_ai(pub_keys, public_key_string, ec.q, hash)
    print(f'\nA DICT: {a_dict}\n')

    # calculating the aggregated key
    aggregated_key = calculate_aggregated_key(pub_keys, a_dict)
    print(f'\nAGGREGATED KEY: {aggregated_key}\n')

    # generating r:
    my_r = 0
    while my_r == 0:
        my_r = gmp.mpz_random(gmp.random_state(int.from_bytes(urandom(4), byteorder='little')), ec.q)
        my_r = my_r % ec.q
    print(f'\nMY r: {my_r}\n')

    # generating R:
    my_r_point = my_r * ec.G
    print(f'\nMY R POINT: {my_r_point}\n')

    # generating the commit
    my_t = hash()
    my_t.update((str(my_r_point.x) + str(my_r_point.y)).encode())
    my_t = my_t.hexdigest()
    #my_t = int.from_bytes(my_t, byteorder='little')
    print(f'\nMY T = ({my_t})\n')

    # concatenating the pub key with the commit
    commit = str(user_key[1]) + SEPARATOR + str(my_t)

    # generating the ordered peer list to send and receive the commits
    peer_list = []
    for key in pub_keys:
        try:
            peer_list.append(address_dict[str(key)])
        except KeyError:
            peer_list.append((hostname, port))
    print(f'\nPEER LIST: {peer_list}\n')

    # send and receive the commits
    commit_list = p2pnetwork.p2p_get((hostname, port), peer_list, commit)
    print(f'\nCOMMIT LIST: {commit_list}\n')

    # concatenating the pub key with the r point
    r_point_package = str(user_key[1]) + SEPARATOR + str(my_r_point)

    # sending and receiving the R points
    r_point_list = p2pnetwork.p2p_get((hostname, port), peer_list, r_point_package)
    print(f'\nR POINT LIST: {r_point_list}\n')

    # check the R points with the commits
    ok = check_commits(commit_list, r_point_list, hash=hs.sha256)
    print(f'OK = {ok}')

    # if the commit doesn't match with the R, exit
    if not ok:
        print('R isn\'t valid')
        return 0, 0

    # generating a r point dictionary from the list
    r_point_dict = r_point_list_to_dict(r_point_list)
    print(f'\nR POINT DICT: {r_point_dict}\n')

    # calculating the sum of the r points
    r_point = r_point_dict[str(pub_keys[0])]
    for key in pub_keys[1:]:
        r_point += r_point_dict[str(key)]
    print(f'\nR POINT: {r_point}\n')

    # computing the challenge c = Hsig(X', R, m)
    c = compute_challenge(aggregated_key, r_point, m, ec.q , hash)
    print(f'\nCHALLENGE: {c}\n')

    # calculating the partial signature s1
    my_s = (gmp.mpz(my_r) + gmp.mpz(c) * gmp.mpz(a_dict[str(user_key[1])]) * gmp.mpz(user_key[0])) % ec.q
    print(f'\nMY S: {my_s}\n')

    # sending s1 and receiving si
    s_package = str(user_key[1]) + SEPARATOR + str(my_s)
    s_list = p2pnetwork.p2p_get((hostname, port), peer_list, s_package)
    print(f'\nS LIST: {s_list}\n')

    s_dict = s_list_to_dict(s_list)
    print(f'\nS DICT: {s_dict}\n')

    signature = gmp.mpz(0)
    for key in pub_keys:
        signature += s_dict[str(key)]

    signature = signature % ec.q
    print(f'\nSIGNATURE: {signature}\n')

    print(80 * '-')
    print(f'RESTRICTIONS: {restrictions}')
    print(f'COMPLETE PUB KEYS LIST:\n{complete_pub_keys_list}')
    merkle_tree = merkle.build_merkle_tree(complete_pub_keys_list, sorted_keys=True, restrictions=restrictions)
    print(f'MERKLE TREE:\n{merkle_tree}')
    proof = merkle.produce_proof(aggregated_key, merkle_tree)

    return r_point, signature, aggregated_key, proof
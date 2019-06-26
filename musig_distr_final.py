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


def calculate_l(pub_keys, hash = hs.sha256):
    """Produz uma codificação única <L> de L={X_1,...,X_n}. Ordenando L com base na ordem lexicográfica e produzindo
    <L> a partir do hash de L ordenado"""
    pointsort.sort(pub_keys)
    l = hash()
    l.update(str(pub_keys).encode())
    return str(l.digest())


def calculate_a_i(pub_keys, unique_l, ec=curve.secp256k1, hash_function=hs.sha256):
    temp = {}
    for key in pub_keys:
        a = hash_function()
        a.update((unique_l + str(key)).encode())
        a = a.digest()
        a = int.from_bytes(a, byteorder='little')
        a = a % ec.q
        temp[str(key)] = a
    return temp


def calculate_aggregated_key(pub_keys, a_dict):
    aggregated_key = a_dict[str(pub_keys[0])]*pub_keys[0]
    for key in pub_keys[1:]:
        aggregated_key += a_dict[str(key)]*key
    return aggregated_key


def calculate_r(ec=curve.secp256k1):
    """Obtem um r aleatório dentro da ordem da curva"""
    r = 0
    while r == 0:
        r = gmp.mpz_random(gmp.random_state(int.from_bytes(urandom(4), byteorder='little')), ec.q)
        r = r % ec.q
    return r


def calculate_r_point(r, ec=curve.secp256k1):
    """Calcula R_i = r_i*P, sendo P o ponto base da curva ec"""
    return r * ec.G


def calculate_t_commit(r_point, hash_function=hs.sha256):
    """Calcula t_i = H_com(R_i)"""
    t = hash_function()
    t.update((str(r_point)).encode())
    return t.hexdigest()


def prepare_package(user_pub_key, package):
    return str(user_pub_key) + SEPARATOR + str(package)


def point_from_str(input):
    x_value = re.search('X:(.*)\\nY:', input).group(1).strip(' ')
    y_value = re.search('Y:(.*)\\n\\(', input).group(1).strip(' ')
    curve_name = re.search('<(.*)>', input).group(1).strip(' ')

    #print(x_value)
    #print(y_value)
    #print(curve_name)

    return point.Point(int(x_value, 0), int(y_value, 0), CURVES[curve_name])

def validate(commit_rcv, r_point_rcv, hash_function = hs.sha256):
    # pub_key = re.search('(.*)\\|', input).group(1).strip(' ')
    # commit = re.search('\\|(.*)', input).group(1).strip(' ')
    # print(pub_key)
    # print(commit)
    pub_key1, commit = commit_rcv.split('|')
    pub_key2, r_point = r_point_rcv.split('|')

    r_point = point_from_str(r_point)

    t = calculate_t_commit(r_point, hash_function=hash_function)
    #t = int.from_bytes(t, byteorder='little')

    if pub_key1 == pub_key2 and commit == str(t):
        return True
    else:
        return False


def check_commits(commit_list, r_point_list, hash_function=hs.sha256):
    i = 0
    for commit, r_point in zip(commit_list, r_point_list):
        result = validate(commit, r_point, hash_function)
        #print(result)
        if not result: # if not true
            print(f'[S]ERROR at entry {i}\n Commit: {commit} not valid for\n R: {r_point}')
            return False
        i += 1
    return True


def r_point_list_to_dict(r_point_list):
    temp = {}
    for item in r_point_list:
        pub_key, r_point = item.split(SEPARATOR)
        r_point = point_from_str(r_point)
        temp[pub_key] = r_point

    return temp


def calculate_r_point_sum(r_point_dict, pub_keys):
    # calculating the sum of the r points
    r_point = r_point_dict[str(pub_keys[0])]
    for key in pub_keys[1:]:
        r_point += r_point_dict[str(key)]
    return r_point


def calculate_s_i(r, c, a, priv_key, ec=curve.secp256k1):
    return (gmp.mpz(r) + gmp.mpz(c) * gmp.mpz(a) * gmp.mpz(priv_key)) % ec.q


def s_list_to_dict(s_list):
    temp = {}
    for item in s_list:
        pub_key, sig = item.split(SEPARATOR)
        temp[pub_key] = int(sig)
    return temp


def calculate_s(pub_keys, s_dict, ec=curve.secp256k1):
    s = gmp.mpz(0)
    for key in pub_keys:
        s += s_dict[str(key)]
    return s % ec.q


def calculate_c(aggregated_key, r_point, m, ec=curve.secp256k1, hash_function=hs.sha256):
    c = hash_function()
    c.update((str(aggregated_key) + str(r_point) + m).encode())
    c = c.digest()
    c = int.from_bytes(c, byteorder='little')
    return c % ec.q


def musig_distributed_with_key_verification(m, user_key, pub_keys_entry, address_dict, hostname, port,
                                            ec=curve.secp256k1, hash = hs.sha256, h_com=hs.sha256, h_agg=hs.sha256,
                                            h_sig=hs.sha256, h_tree=hs.sha256,
                                            complete_pub_keys_list=None, restrictions=None):
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

    public_key_l = None

    # pub_keys will be the list with all public keys in the signing process
    pub_keys = pub_keys_entry.copy()
    pub_keys.append(user_key[1])

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    if complete_pub_keys_list is None:
        public_key_l = calculate_l(pub_keys)
    else:
        pointsort.sort(pub_keys)
        public_key_l = calculate_l(complete_pub_keys_list)

    print('_'*80)
    print(f'[S] <L> = {public_key_l}')

    # calculating a_i = H_agg(L,X_i) for each X_i
    a_dict = calculate_a_i(pub_keys, public_key_l, ec=ec, hash_function=h_agg)
    print(f'\nA DICT: {a_dict}\n')

    # calculating the aggregated key
    aggregated_key = calculate_aggregated_key(pub_keys, a_dict)
    print(f'\nAGGREGATED KEY: {aggregated_key}\n')

    # generating r:
    user_r = calculate_r(ec=ec)
    print(f'\nMY r: {user_r}\n')

    # generating R:
    user_r_point = calculate_r_point(user_r, ec=ec)
    print(f'\nMY R POINT: {user_r_point}\n')

    # generating the commit
    user_t = calculate_t_commit(user_r_point, hash_function=h_com)
    print(f'\nMY T = ({user_t})\n')

    # concatenating the pub key with the commit
    commit = prepare_package(user_key[1], user_t)

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
    r_point_package = prepare_package(user_key[1],user_r_point)

    # sending and receiving the R points
    r_point_list = p2pnetwork.p2p_get((hostname, port), peer_list, r_point_package)
    print(f'\nR POINT LIST: {r_point_list}\n')

    # check the R points with the commits
    ok = check_commits(commit_list, r_point_list, hash_function=hs.sha256)
    print(f'OK = {ok}')

    # if the commit doesn't match with the R, exit
    if not ok:
        print('R isn\'t valid')
        return 0, 0

    # generating a r point dictionary from the list
    r_point_dict = r_point_list_to_dict(r_point_list)
    print(f'\nR POINT DICT: {r_point_dict}\n')

    # calculating the sum of the r points
    r_point = calculate_r_point_sum(r_point_dict, pub_keys)
    print(f'\nR POINT: {r_point}\n')

    # computing the challenge c = Hsig(X', R, m)
    c = calculate_c(aggregated_key, r_point, m, ec=ec, hash_function=h_sig)
    print(f'\nCHALLENGE: {c}\n')

    # calculating the partial signature s1
    user_s = calculate_s_i(user_r, c, a_dict[str(user_key[1])], user_key[0], ec=ec)
    print(f'\nMY S: {user_s}\n')

    # sending s1 and receiving si
    s_package = prepare_package(user_key[1], user_s)
    s_list = p2pnetwork.p2p_get((hostname, port), peer_list, s_package)
    print(f'\nS LIST: {s_list}\n')

    s_dict = s_list_to_dict(s_list)
    print(f'\nS DICT: {s_dict}\n')

    partial_signature = calculate_s(pub_keys, s_dict, ec=ec)
    print(f'\nSIGNATURE: {partial_signature}\n')

    print(80 * '-')
    print(f'RESTRICTIONS: {restrictions}')
    print(f'COMPLETE PUB KEYS LIST:\n{complete_pub_keys_list}')
    #merkle_tree = merkle.build_merkle_tree(complete_pub_keys_list, sorted_keys=True, restrictions=restrictions)
    merkle_tree = merkle.build_merkle_tree(pub_keys, complete_public_key_list=complete_pub_keys_list,
                                           restrictions=restrictions, hash_function=h_tree)
    print('$'*80)
    print(f'MERKLE TREE:\n{merkle_tree}')
    print('$' * 80)
    proof = merkle.produce_proof(aggregated_key, merkle_tree, hash_function=hash)

    return r_point, partial_signature, aggregated_key, proof, public_key_l


def musig_ver(r_point, s, m, aggregated_key=None, complete_pub_keys_list=None, ec=curve.secp256k1, h_agg=hs.sha256,
              h_sig=hs.sha256, pub_keys_entry=None, public_key_l=None):
    """TODO: COLOCAR A CHAVE AGG COMO PARAMETRO OBRIGATORIO, NAO FAZ SENTIDO A VERIFICAÇÃO PELA ARV DE MERKLE SEM ELA.
        DESSA FORMA, A VERIFICAÇÃO SEMPRE SERA FEITA A PARTIR DA CHAVE AGG"""
    # R: elliptic curve point
    # s: int/mpz
    # m: string
    # pub_key: elliptic curve point
    # pub_keys_entry: [pub_key_1,...,pub_key_k]
    # ec: elliptic curve
    # hash: hash function

    if aggregated_key is None:

        if pub_keys_entry is None:
            print("[V] No aggregated key or public key list provided")
            return False

        else:
            pub_keys = pub_keys_entry.copy()

            # sort L and calculate <L>
            if complete_pub_keys_list is None:
                public_key_l = calculate_l(pub_keys)
            else:
                pointsort.sort(pub_keys)
                public_key_l = calculate_l(complete_pub_keys_list)

            print(f"[V] sorted public keys: {pub_keys}")
            print('_' * 80)
            print(f'[V] <L> = {public_key_l}')

            # calculating ai = Hagg(L,Xi)
            a_dict = calculate_a_i(pub_keys, public_key_l, ec=ec, hash_function=h_agg)
            print(f'\nA DICT: {a_dict}\n')

            # calculating the aggregated key
            aggregated_key = calculate_aggregated_key(pub_keys, a_dict)
            print(f'\nAGGREGATED KEY: {aggregated_key}\n')
    else:
        if public_key_l is None:
            print("[V] Aggregated key provided but <L> wasn't provided")
            return False

    # computing the challenge c = Hsig(X', R, m)
    c = calculate_c(aggregated_key, r_point, m, ec=ec, hash_function=h_sig)
    print(f'\nCHALLENGE: {c}\n')

    # checking if sP = R + sum(ai*c*Xi) = R + c*X'
    left = s * ec.G
    print(f'\nsP: {left}\n')
    right = r_point + c * aggregated_key
    print(f'\nR + c*X: {right}\n')

    if left.x == right.x and left.y == right.y:
        return True
    else:
        return False


def aggregated_key_verification(aggregated_key, proof, complete_pub_keys_list=None, hash_function=hs.sha256,
                                pub_keys_entry=None, restrictions=None, root=None):
    key_ok = False

    if root is None:
        if complete_pub_keys_list is None:
            if pub_keys_entry is None:
                print('[V] ERROR: no key input provided for the merkle tree construction')
                return False

        merkle_tree = merkle.build_merkle_tree(pub_keys_entry, complete_public_key_list=complete_pub_keys_list,
                                               restrictions=restrictions, hash_function=hash_function)

        key_ok = merkle.verify(merkle_tree[0], aggregated_key, proof, hash_function=hash_function)

    else:

        key_ok = merkle.verify(root, aggregated_key, proof, hash_function=hash_function)

    if key_ok:
        return True
    else:
        return False


def musig_ver_with_key_verification(r_point, s, m, proof, aggregated_key=None, complete_pub_keys_list=None,
                                    ec=curve.secp256k1, h_agg=hs.sha256, h_sig=hs.sha256, h_tree=hs.sha256,
                                    pub_keys_entry=None, public_key_l=None, restrictions=None, root=None):

    """TODO: COLOCAR A CHAVE AGG COMO PARAMETRO OBRIGATORIO, NAO FAZ SENTIDO A VERIFICAÇÃO PELA ARV DE MERKLE SEM ELA.
    DESSA FORMA, A VERIFICAÇÃO SEMPRE SERA FEITA A PARTIR DA CHAVE AGG"""
    # R: elliptic curve point
    # s: int/mpz
    # m: string
    # pub_key: elliptic curve point
    # pub_keys: [pub_key_1,...,pub_key_k]
    # ec: elliptic curve

    agg_key_ok = aggregated_key_verification(aggregated_key, proof, complete_pub_keys_list=complete_pub_keys_list,
                                             hash_function=h_tree, pub_keys_entry=pub_keys_entry,
                                             restrictions=restrictions, root=root)

    if agg_key_ok:
        return musig_ver(r_point, s, m, aggregated_key=aggregated_key, complete_pub_keys_list=complete_pub_keys_list,
                         ec=ec, h_agg=h_agg, h_sig=h_sig, pub_keys_entry=pub_keys_entry, public_key_l=public_key_l)
    else:
        print("[V] Aggregated key is invalid")
        return False

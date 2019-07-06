import hashlib as hs
from fastecdsa import curve
import gmpy2 as gmp
from os import urandom, system
import keystorage
import pointsort


def calculate_c(hash, ec, pub_key, rpoint, public_key_l, m):
    """Realiza o calculo de c_i = H(X_i, R, <L>, m)"""
    c = hash()
    c.update((str(pub_key.x) + str(pub_key.y) + str(rpoint.x) + str(rpoint.y) + public_key_l + m).encode())
    #c.update((str(pub_key.x) + str(pub_key.y) + str(rpoint.x) + str(rpoint.y) + str(public_key_l) + m).encode())
    c = c.digest()  # size 48 bytes
    c = int.from_bytes(c, byteorder='little')
    return c % ec.q


def calculate_l(pub_keys):
    """Produz uma codificação única <L> de L={X_1,...,X_n}. Sendo <L> a conversão para string de L na ordem
     lexicográfica"""
    pointsort.sort(pub_keys)
    #l = hs.sha256()
    #l.update(str(pub_keys).encode())
    #return int.from_bytes(l.digest(), byteorder='little')
    return str(pub_keys)


def bellare_neven_multisig(m, keys_list, ec=curve.secp256k1, hash = hs.sha256):
    """Simula o esquema Bellare-Neven com o usuário operando como todos os signatários. Devem ser fornecidas uma
    mensagem a ser assinada e uma lista contendo o par de chaves privada/pública dos signatários. Retorna uma assinatura
    (R,s) relativa a mensagem m e o respectivo conjunto de chaves públicas."""
    # keys_list = [(priv_key,pub_key),...]
    i = 1
    r_list = []
    rpoint_list = []
    rpoint_sum = None

    keys_dict = {}
    pub_keys = []
    for key_pair in keys_list:
        pub_keys.append(key_pair[1])
        keys_dict[str(key_pair[1])] = key_pair[0]

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    pub_keys_l = calculate_l(pub_keys)

    # the r's are calculated after the sorting of pub_keys so the resulting r_list is sorted with relation to pub_keys
    for pub_key in pub_keys:

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
    for pub_key in pub_keys:
        c = calculate_c(hash, ec, pub_key, rpoint_sum, pub_keys_l, m)
        hash_list.append(c)
        print(f'c{i+1} = {c}')

        s = (gmp.mpz(keys_dict[str(pub_key)])*gmp.mpz(c) + gmp.mpz(r_list[i])) % ec.q
        signature_list.append(s)
        print(f's{i + 1} = {s}\n')
        s_sum = (s_sum + s) % ec.q
        i += 1

    print(f's = {s_sum}\n')
    print(f'Signature (R,s) is: ({rpoint_sum},{s_sum})\n')
    return rpoint_sum, s_sum


def bellare_neven_multisig_ver(R, s, m, pub_key_list, ec=curve.secp256k1, hash = hs.sha256):
    """Verifica uma assinatura (R,s) produzida a partir do esquema Bellare-Neven junto a mensagem m e multiset de chaves
    públicas pub_key_list. Caso (R,s) seja válida, é retornado True, caso contrário, False."""

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    pub_keys_l = calculate_l(pub_key_list)

    i = 0
    hash_list = []
    c_pub_key = None
    first = True

    for key in pub_key_list:
        c = calculate_c(hash, ec, key, R, pub_keys_l, m)
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


def test1():
    input('> TEST 1 ...')
    print('> RUNNING...')
    key1 = keystorage.import_keys('k2.pem')
    key2 = keystorage.import_keys('key2.pem')
    key3 = keystorage.import_keys('key4.pem')
    key4 = keystorage.import_keys('key90.pem')

    key_list = [key1, key2, key3, key4]
    pub_key_list = [key1[1], key2[1], key3[1], key4[1]]

    m = 'teste39826dasg7d9sbdsadteste343rfsafasf'

    R, s = bellare_neven_multisig(m, key_list)

    print('_'*80)
    print(f'>> Signature verification:')
    print(bellare_neven_multisig_ver(R, s, m, pub_key_list))
    # print('_' * 80)
    # print(f'>> Signature verification with the pub key list:')
    # print(naive_schnorr_musig_ver(R, s, m, pub_keys_list=pub_key_list))
    # print('_' * 80)
    # print(f'>> Signature verification with no key input:')
    # print(naive_schnorr_musig_ver(R, s, m))
    # print('_' * 80)
    print('END: TEST 1')


def main():
    system('clear')
    test1()


if __name__ == "__main__":
    main()
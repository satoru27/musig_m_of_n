import hashlib as hs
from fastecdsa import curve
import gmpy2 as gmp
from os import urandom, system
import keystorage


def naive_schnorr_musig(m, keys_list, ec=curve.secp256k1, hash = hs.sha256):
    """Simula o esquema Naive Schnorr Multi-signature para uma mensagem m com o usuário realizando o papel de todos
     os signatários do processo. Devem ser fornecidas em key_list todos os pares de chave pública e privada que farão
     parte do esquema de assinatura."""
    # key_list = [(priv_key,pub_key)]
    i = 1
    r_list = []
    rpoint_list = []
    rpoint_sum = None
    aggregated_key = None

    for keys in keys_list:
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
            aggregated_key = keys[1]
        else:
            rpoint_sum += rpoint
            aggregated_key += keys[1]

        i += 1

    print(f'Sum of all Ri is R = {rpoint_sum}')
    print(f'Sum of all public keys X is X\'= {aggregated_key} ')

    c = hash()
    c.update((str(aggregated_key.x) + str(aggregated_key.y) + str(rpoint_sum.x) + str(rpoint_sum.y) + m).encode())
    c = c.digest()  # size 48 bytes
    c = int.from_bytes(c, byteorder='little')
    c = c % ec.q  # necessario ?

    print(f'Hash result c = {c}')

    i = 1
    partial_signatures = []
    s = gmp.mpz(0)
    for keys in keys_list:
        s_i = (r_list[i-1] + gmp.mpz(c) * gmp.mpz(keys[0])) % ec.q
        partial_signatures.append(s_i)
        print(f'Partial signature s{i} = {partial_signatures[i-1]}')
        s = (s + s_i) % ec.q
        i += 1

    print(f'Sum of the signatures = {s}')

    return rpoint_sum, s, aggregated_key


def naive_schnorr_musig_ver(R, s, m, ec=curve.secp256k1, hash=hs.sha256, aggregated_key=None, pub_keys_list=None):
    """
    A verificação é a mesma do esquema de assinatura simples de schnorr caso seja fornecida a chave pública agregada,
    caso contrário ela é calculada a partir da lista de chaves públicas.
        Verify if sP = R + cX'
    """
    first = True
    if aggregated_key is None:
        if pub_keys_list is not None:
            for pub_key in pub_keys_list:
                if first:
                    aggregated_key = pub_key
                    first = False
                else:
                    aggregated_key += pub_key
        else:
            print("No key or key list provided")
            return False

    c = hash()
    c.update((str(aggregated_key.x) + str(aggregated_key.y) + str(R.x) + str(R.y) + m).encode())
    c = c.digest()  # size 48 bytes
    c = int.from_bytes(c, byteorder='little')
    c = c % ec.q

    left = s * ec.G
    right = R + c * aggregated_key

    if left.x == right.x and left.y == right.y:
        return True
    else:
        return False


def test1():
    input('>TEST 1 ...')
    key1 = keystorage.import_keys('k2.pem')
    key2 = keystorage.import_keys('key2.pem')
    key3 = keystorage.import_keys('key4.pem')
    key4 = keystorage.import_keys('key90.pem')

    key_list = [key1, key2, key3, key4]
    pub_key_list = [key1[1], key2[1], key3[1], key4[1]]

    m = 'teste39826dasg7d9sbdsadteste343rfsafasf'

    R, s, aggregated_key = naive_schnorr_musig(m, key_list)

    print('_'*80)
    print(f'>> Signature verification with the aggregated pub key:')
    print(naive_schnorr_musig_ver(R, s, m, aggregated_key=aggregated_key))
    print('_' * 80)
    print(f'>> Signature verification with the pub key list:')
    print(naive_schnorr_musig_ver(R, s, m, pub_keys_list=pub_key_list))
    print('_' * 80)
    print(f'>> Signature verification with no key input:')
    print(naive_schnorr_musig_ver(R, s, m))
    print('_' * 80)
    print('END: TEST 1')


def main():
    system('clear')
    test1()

if __name__ == "__main__":
    main()
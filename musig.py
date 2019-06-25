import hashlib as hs
from fastecdsa import curve
import gmpy2 as gmp
from os import urandom
import pointsort
from os import system
import keystorage


def calculate_l(pub_keys, hash = hs.sha256):
    """Produz uma codificação única <L> de L={X_1,...,X_n}. Ordenando L com base na ordem lexicográfica e produzindo
    <L> a partir do hash de L ordenado"""
    pointsort.sort(pub_keys)
    l = hash()
    l.update(str(pub_keys).encode())
    #return int.from_bytes(l.digest(), byteorder='little')
    return str(l.digest())


def calculate_a(public_key_l, pub_key, hash=hs.sha256, ec=curve.secp256k1):
    """Calcula a_i = H_agg(<L>, X_i)"""
    a = hash()
    a.update((public_key_l + str(pub_key)).encode())
    a = a.digest()  # size 48 bytes
    a = int.from_bytes(a, byteorder='little')
    #print('*'*80)
    #print(f'[CALCULATE A]: <L> = {public_key_l}, pub_key = {pub_key}, a = {a}')
    return a % ec.q


def calculate_aggregated_key(pub_keys, a_list):
    """Calcula a chave pública agregada X = \sum_{i=1}^{n} X_i"""
    i = 1
    first = True
    aggregated_key = None
    for key in pub_keys:
        if first:
            aggregated_key = a_list[0] * key
            first = False
            #print(f'X += a{i}*X{i}')
        else:
            aggregated_key += a_list[i] * key
            #print(f'X += a{i + 1}*X{i + 1}')
            i += 1
    
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


def calculate_t_commit(r_point, hash=hs.sha256):
    """Calcula t_i = H_com(R_i)"""
    t = hash()
    t.update((str(r_point)).encode())
    return t.digest()


def check_t_commit(r_point, t_commit, hash=hs.sha256):
    """Checa se o commit t_i' recebido é equivalente a t_i = H_com(R_i)"""
    calculated_t_commit = calculate_t_commit(r_point, hash=hash)

    if t_commit == calculated_t_commit:
        return True
    else:
        return False


def calculate_r_point_sum(r_point_list):
    """Calcula a soma R dos pontos R_i; R = \sum_{i=1}^{n} R_i"""
    r_point_sum = None
    first = True
    for r_point in r_point_list:
        if first:
            r_point_sum = r_point
            first = False
        else:
            r_point_sum += r_point

    return r_point_sum


def calculate_c(aggregated_key, r_point_sum, m, hash=hs.sha256, ec=curve.secp256k1):
    """Calcula c = H_sig(X,R,m), sendo X a chave pública agregada, R a soma dos pontos R_i e m a mensagem a ser
     assinada"""
    c = hash()
    c.update((str(aggregated_key) + str(r_point_sum) + m).encode())
    c = c.digest()  # size 48 bytes
    c = int.from_bytes(c, byteorder='little')
    return c % ec.q


def calculate_s_i(r, c, a, priv_key, ec=curve.secp256k1):
    """Calcula a assinatura parcial s_i = r_i + c * a_i * x_i, sendo x_i a respectiva chave privada."""
    return (gmp.mpz(r) + gmp.mpz(c) * gmp.mpz(a) * gmp.mpz(priv_key)) % ec.q


def calculate_s_sum(s_list, ec=curve.secp256k1):
    """Calcula a assinatura parcial s do grupo, tal que s = \sum_{i=1}^{n} s_i"""
    s = gmp.mpz(0)

    for partial_signature in s_list:
        s += partial_signature

    return s % ec.q


def musig(m, key_lst, ec=curve.secp256k1, h_com=hs.sha256, h_agg=hs.sha256, h_sig=hs.sha256):
    """
    Simula o esquema MuSig com o usuário operando como todos os signatários. Devem ser fornecidas uma mensagem m
    a ser assinada, uma lista contendo as chaves privadas e públicas dos signatários, uma curva elíptica e três
    funções de hash H_com, H_agg e H_sig.
    É retornado uma assinatura (R,s) (para m e a lista de chaves públicas L produzida com o esquema MuSig),
    a chave pública agregada resultante de L e a codificação única <L> de L
    """
    # my_key = (priv key, pub key)
    # key_lst = [(priv key1, pub key1), (priv key2, pub key2)]

    key_dict = {}
    pub_keys = []
    for key in key_lst:
        key_dict[str(key[1])] = key[0]
        pub_keys.append(key[1])

    # the order of <L> must be the same for all signers
    # <L> must be a unique encoding of L = {X1,...,Xn}
    public_key_l = calculate_l(pub_keys, hash=h_sig)
    print('_' * 80)
    print(f"[S] sorted public keys: {pub_keys}")

    total_signers = len(pub_keys)

    i = 0
    # computing ai = Hagg(L,Xi)
    a_list = []
    for pub_key in pub_keys:
        a = calculate_a(public_key_l, pub_key, hash=h_agg, ec=ec)
        a_list.append(a)

        i += 1

    print('_' * 80)
    print(f'[S] a_i list: {a_list}\n')

    #calculating X = sum(ai*Xi)
    aggregated_key = calculate_aggregated_key(pub_keys, a_list)

    # generate r1 and compute R1 = r1P
    # calculate and send Ri commitment
    r_list = []
    r_point_list = []
    commit_list = []

    for i in range(total_signers):
        r = calculate_r(ec=ec)
        r_list.append(r)

        r_point = calculate_r_point(r, ec=ec)
        r_point_list.append(r_point)

        t = calculate_t_commit(r_point, hash=h_com)
        commit_list.append(t)

    # checking the commited t with respective R
    # in this implementation this is redundant but will be necessary once the communication isn't centralized

    for i in range(total_signers):
        if not check_t_commit(r_point_list[i], commit_list[i], hash=h_com):
            print('_' * 80)
            print(f"[S] t_com({i}) not valid, aborting...")
            return 0, 0, 0, 0

    # computing R = sum(Ri)
    r_point_sum = calculate_r_point_sum(r_point_list)
    print('_' * 80)
    print(f'[S] R = {r_point_sum}\n')

    # computing the challenge c = Hsig(X', R, m)
    c = calculate_c(aggregated_key, r_point_sum, m, hash=h_sig, ec=ec)
    print('_' * 80)
    print(f'[S] c = {c}\n')

    # computing s1 = r1 + c*a1*x1 mod p
    s_list = []
    for i in range(total_signers):
        s_i = calculate_s_i(r_list[i], c, a_list[i], key_dict[str(pub_keys[i])])
        s_list.append(s_i)

        #print(f's{i+1} = {s_list[i]}')

    # computing s = sum(si) mod n
    s = calculate_s_sum(s_list, ec=ec)
    print('_' * 80)
    print(f'[S] s = {s}\n')
    # signature is (R,s)
    return r_point_sum, s, aggregated_key, public_key_l


def musig_ver(r_point_sum, s, m, ec=curve.secp256k1, aggregated_key=None, pub_keys=None, public_key_l=None,
              h_agg=hs.sha256, h_sig=hs.sha256):
    """
    Verifica uma assinatura (R,s) para a mensagem m e uma lista de chaves públicas L, produzida utilizando o esquema
    MuSig. A verificação toma como entrada uma assinatura (R,s), uma mensagem m, uma curva elíptica ec, duas funções de
    hash H_agg e H_sig e uma das duas opções abaixo:

    1) Uma chave pública agregada X relativa a L e uma codificação única <L> de L
    2) Uma lista de chaves públicas L

    No primeiro caso, a verificação ocorre como a verificação de uma assinatura simples de Schnorr
    No segundo caso, é gerado <L> a partir de L, calculados os a_i's e assim, calculada a chave pública agregada X

    Se a assinatura é válida, é retornado True, caso contrário, False.
    """

    # R: elliptic curve point
    # s: int/mpz
    # m: string
    # pub_key: elliptic curve point
    # pub_keys: [pub_key_1,...,pub_key_k]
    # ec: elliptic curve

    if aggregated_key is None:
        if pub_keys is None:
            print("[V] No aggregated key or public key list provided")
            return False
        else:
            # sort L and calculate <L>
            public_key_l = calculate_l(pub_keys, hash=h_sig)
            print(f"[V] sorted public keys: {pub_keys}")
            # calculate a_i
            a_list = []
            for pub_key in pub_keys:
                a_list.append(calculate_a(public_key_l, pub_key, hash=h_agg, ec=ec))

            print('_' * 80)
            print(f'[V] a_i list: {a_list}\n')

            # calculate the aggregated key
            aggregated_key = calculate_aggregated_key(pub_keys, a_list)
            print(f'[V] Aggregated key: {aggregated_key}')
    else:
        if public_key_l is None:
            print("[V] Aggregated key provided but <L> wasn't provided")
            return False

    # computing the challenge c = Hsig(X', R, m)
    c = calculate_c(aggregated_key, r_point_sum, m, hash=h_sig, ec=ec)
    print(f'[V] c = {c}\n')

    # checking if sP = R + sum(ai*c*Xi) = R + c*X'
    left = s*ec.G
    right = r_point_sum + c*aggregated_key

    if left.x == right.x and left.y == right.y:
        return True
    else:
        return False


def short_assert(value, expected_value, message):
    assert value == expected_value, message


def test1():
    input('> TEST 1 ...')
    print('> RUNNING...')
    key1 = keystorage.import_keys('k2.pem')
    key2 = keystorage.import_keys('key2.pem')
    key3 = keystorage.import_keys('key4.pem')
    key4 = keystorage.import_keys('key90.pem')

    key_list = [key1, key2, key3, key4]
    pub_key_list = [key1[1], key2[1], key3[1], key4[1]]

    m = 'testemusig39826dasg7d9sbdsadteste343rfsafasf'

    r_point_sum, s, aggregated_key, pub_key_l = musig(m, key_list, ec=curve.secp256k1, h_agg=hs.sha256, h_sig=hs.sha256)

    print('_'*80)
    print(f'>> Signature verification with aggregated key and <L>:')
    result = musig_ver(r_point_sum, s, m, ec=curve.secp256k1, h_agg=hs.sha256, h_sig=hs.sha256,
                       aggregated_key=aggregated_key, public_key_l=pub_key_l)
    short_assert(result, True, '1) Should be: True')
    print('PASS')

    print('_' * 80)
    print(f'>> Signature verification with the pub key list:')
    result = musig_ver(r_point_sum, s, m, ec=curve.secp256k1, h_agg=hs.sha256, h_sig=hs.sha256, pub_keys=pub_key_list)
    short_assert(result, True, '2) Should be: True')
    print('PASS')

    print('_' * 80)
    print(f'>> Signature verification with no key input:')
    result = musig_ver(r_point_sum, s, m, ec=curve.secp256k1, h_agg=hs.sha256, h_sig=hs.sha256)
    short_assert(result, False, '3) Should be: False')
    print('PASS')

    print('_' * 80)
    print(f'>> Signature verification with agg key and without <L>:')
    result = musig_ver(r_point_sum, s, m, ec=curve.secp256k1, h_agg=hs.sha256, h_sig=hs.sha256,
                       aggregated_key=aggregated_key)
    short_assert(result, False, '4) Should be: False')
    print('PASS')

    print('_' * 80)
    print(f'>> Signature verification with pub key list and <L>:')
    result = musig_ver(r_point_sum, s, m, ec=curve.secp256k1, h_agg=hs.sha256, h_sig=hs.sha256, pub_keys=pub_key_list,
                       public_key_l=pub_key_l)
    short_assert(result, True, '5) Should be: True')
    print('PASS')

    print('_' * 80)
    print(f'>> Signature verification with just <L>:')
    result = musig_ver(r_point_sum, s, m, ec=curve.secp256k1, h_agg=hs.sha256, h_sig=hs.sha256, public_key_l=pub_key_l)
    short_assert(result, False, '6) Should be: False')
    print('PASS')

    print('_' * 80)
    print(f'>> Signature verification with just everything:')
    result = musig_ver(r_point_sum, s, m, ec=curve.secp256k1, h_agg=hs.sha256, h_sig=hs.sha256,
                       aggregated_key=aggregated_key, pub_keys=pub_key_l, public_key_l=pub_key_l)
    short_assert(result, True, '7) Should be: True')
    print('PASS')

    print('_' * 80)
    print('END: TEST 1')


def main():
    system('clear')
    test1()


if __name__ == "__main__":
    main()
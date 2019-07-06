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


def calculate_l(pub_keys, hash=hs.sha256):
    """
    Produz uma codificação única <L> de L={X_1,...,X_n}. Ordenando L com base na ordem lexicográfica e produzindo
    <L> a partir do hash de L ordenado
    :param pub_keys: lista de chaves públicas dos signatários na forma [X_1,X_2,...,X_n]
    :param func hash: função de hash
    :return: string do hash de L ordenado lexicograficamente
    """
    pointsort.sort(pub_keys)
    l = hash()
    l.update(str(pub_keys).encode())
    return str(l.digest())


def calculate_a_i(pub_keys, unique_l, ec=curve.secp256k1, hash_function=hs.sha256):
    """
    Calcula a_i = H_agg(<L>,X_i) para cada X_i fornecido como entrada e retorna uma lista de a_i's com ordem relativa
    a ordem da lista de chaves públicas.

    :param list pub_keys: lista de chaves públicas dos signatários na forma [X_1,X_2,...,X_n]
    :param str unique_l: codificação única <L> do multiset L de todas as chaves públicas envolvidas na assinatura
    :param Curve ec: curva elíptica
    :param func hash_function: função de hash H_agg
    :return: lista de a_i's com ordenação relativa a pub_keys
    """
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
    """
    Calcula a chave pública agregada relativa às chaves públicas fornecidas como parâmetro.

    :param list pub_keys: lista de chaves públicas dos signatários na forma [X_1,X_2,...,X_n]
    :param dict a_dict: dicionário na forma {"X_1":a_1,...,"X_n":a_n}, com a_i = H_agg(<L>,X_i)
    :return: chave agregada X
    :rtype: Point
    """
    aggregated_key = a_dict[str(pub_keys[0])]*pub_keys[0]
    for key in pub_keys[1:]:
        aggregated_key += a_dict[str(key)]*key
    return aggregated_key


def calculate_r(ec=curve.secp256k1):
    """
    Obtém um r aleatório dentro da ordem da curva

    :param Curve ec: curva elíptica
    :return: inteiro aleátório 1 =< r =< p-1, sendo p a ordem da curva
    :rtype: int
    """
    """"""
    r = 0
    while r == 0:
        r = gmp.mpz_random(gmp.random_state(int.from_bytes(urandom(4), byteorder='little')), ec.q)
        r = r % ec.q
    return r


def calculate_r_point(r, ec=curve.secp256k1):
    """
    Calcula R_1 = r_1'*P, sendo P o ponto base da curva ec

    :param int r: inteiro obtido de forma aleatória dentro da ordem da curva
    :param Curve ec: curva elíptica
    :return: ponto R
    :rtype: Point
    """
    """"""
    return r * ec.G


def calculate_t_commit(r_point, hash_function=hs.sha256):
    """
    Calcula t_1 = H_com(R_1)

    :param Point r_point: ponto R
    :param function hash_function: função de hash H_com
    :return: hash resultante em hexadecimal
    :rtype: str
    """
    """Calcula t_i = H_com(R_i)"""
    t = hash_function()
    t.update((str(r_point)).encode())
    return t.hexdigest()


def prepare_package(user_pub_key, package):
    """
    Formata um pacote a ser enviado pela rede durante o protolo de assinatura

    :param Point user_pub_key: chave pública do signatário
    :param var package: compromisso t_i, ponto R_i ou assinatura parcial s_i
    :type var: int ou Point
    :return: str(pub_key)||SEPARATOR||str(package)
    :rtype: str
    """
    return str(user_pub_key) + SEPARATOR + str(package)


def point_from_str(input):
    """
    Cria um objeto ponto (de uma curva elíptica) a partir de uma string (formatada especficamente) que descreve um
     ponto de uma curva elíptica.
     É utilizado regex para a separação de parâmetros na string.

    :param input: string na forma "X: 'valor da coordenada x em hexadecimal'\nY: 'valor da coordenada x em hexadecimal'\n(On curve <'nome da curva'>)"
    :return: ponto da curva elíptica point.Point(x,y,curve)
    """
    x_value = re.search('X:(.*)\\nY:', input).group(1).strip(' ')
    y_value = re.search('Y:(.*)\\n\\(', input).group(1).strip(' ')
    curve_name = re.search('<(.*)>', input).group(1).strip(' ')

    #print(x_value)
    #print(y_value)
    #print(curve_name)

    return point.Point(int(x_value, 0), int(y_value, 0), CURVES[curve_name])

def validate(commit_rcv, r_point_rcv, hash_function = hs.sha256):
    """
    Verifica se t_i == H_com(R_i)

    :param commit_rcv: string na forma "pub_key_i|t_i"
    :param r_point_rcv: string na forma "pub_key_i'|R_i"
    :param hash_function: função de hash H_com
    :return: True se pub_key_i'==pub_key_i e t_i == H_com(R_i), False caso contrário.
    """
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
    """
    Verifica se os compromissos t_i dos co-signatários equivalem a t_i' = H_com(R_i), sendo R_i o respectivo
    ponto enviado pelo co-signatário. As listas dos compromissos t_i e de pontos R_i contém uma identificação da chave
    pública X_i do seu respectivo signatário.

    :param commit_list: lista com strings ["pub_key_1|t_1","pub_key_2|t_2", ... ,"pub_key_n|t_n"]
    :param r_point_list: lista com strings ["pub_key_1|R_1","pub_key_2|R_2", ... ,"pub_key_n|R_n"]
    :param hash_function: função de hash H_com
    :return: True se cada t_i'==t_i, False caso algum t_i' != t_i
    """
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
    """
    Converte uma lista contendo todos os R_i de cada signatário e suas respectivas chaves públicas em um dicionário
    contendo a string de uma chave pública como chave e seu respectivo R_i como valor.

    :param r_point_list: lista com strings ["pub_key_1|R_1","pub_key_2|R_2", ... ,"pub_key_n|R_n"]
    :return: dicionário {"pub_key_1":R_1,"pub_key_2"|R_2, ... ,"pub_key_n":R_n}
    """
    temp = {}
    for item in r_point_list:
        pub_key, r_point = item.split(SEPARATOR)
        r_point = point_from_str(r_point)
        temp[pub_key] = r_point

    return temp


def calculate_r_point_sum(r_point_dict, pub_keys):
    """
    Calcula a soma R dos pontos R_i de cada signatário tal que R =\sum_{i=1}^{n} R_i

    :param dict r_point_dict: dicionário dos pontos R_i na forma {"pub_key_1":R_1,"pub_key_2"|R_2, ... ,"pub_key_n":R_n}
    :param list pub_keys: lista de chaves públicas dos signatários na forma [X_1,X_2,...,X_n]
    :return: R = \sum_{i=1}^{n} R_i
    """
    # calculating the sum of the r points
    r_point = r_point_dict[str(pub_keys[0])]
    for key in pub_keys[1:]:
        r_point += r_point_dict[str(key)]
    return r_point


def calculate_s_i(r, c, a, priv_key, ec=curve.secp256k1):
    """
    Calcula s_1 = r_1 + c * a_1 * x_1

    :param int r: inteiro r do signatário
    :param int c: c = H_sig(X_agg, R, m), sendo X_agg a chave pública agregada, R a soma dos R_i dos signatário e m a mensagem
    :param int a: a_1 = H_agg(<L>,X_1), sendo X_1 a chave pública do signatário
    :param int priv_key: chave privada do signatário
    :param Curve ec: curva elíptica
    :return: assinatura parcial s_1 do signatario
    """
    return (gmp.mpz(r) + gmp.mpz(c) * gmp.mpz(a) * gmp.mpz(priv_key)) % ec.q


def s_list_to_dict(s_list):
    """
    Converte uma lista contendo todos os s_i de cada signatário e suas respectivas chaves públicas em um dicionário
    contendo a string de uma chave pública como chave e seu respectivo s_i como valor.

    :param s_list: lista com strings ["pub_key_1|s_1","pub_key_2|s_2", ... ,"pub_key_n|s_n"]
    :return: dicionário {"pub_key_1":s_1,"pub_key_2"|s_2, ... ,"pub_key_n":s_n}
    """
    temp = {}
    for item in s_list:
        pub_key, sig = item.split(SEPARATOR)
        temp[pub_key] = int(sig)
    return temp


def calculate_s(pub_keys, s_dict, ec=curve.secp256k1):
    """
    Calcula a assinatura parcial do grupo s = \sum_{i=1}^n s_i

    :param list pub_keys: lista de chaves públicas dos signatários na forma [X_1,X_2,...,X_n]
    :param dict s_dict: dicionário das assinaturas parciais dos signatários na forma {"pub_key_1":s_1,"pub_key_2"|s_2, ... ,"pub_key_n":s_n}
    :param Curve ec: curva elíptica
    :return: assinatura parcial s do grupo
    """
    s = gmp.mpz(0)
    for key in pub_keys:
        s += s_dict[str(key)]
    return s % ec.q


def calculate_c(aggregated_key, r_point, m, ec=curve.secp256k1, hash_function=hs.sha256):
    """
    Calcula o desafio c = H_sig(X, R, m)

    :param Point aggregated_key: chave pública agregada X = \sum_{i=1}^n a_i X_i
    :param Point r_point: ponto R = \sum_{i=1}^n R_i
    :param str m: mensagem a ser assinada
    :param Curve ec: curva elíptica
    :param func hash_function: função de hash H_sig
    :return: inteiro c = H_sig(X, R, m)
    """
    c = hash_function()
    c.update((str(aggregated_key) + str(r_point) + m).encode())
    c = c.digest()
    c = int.from_bytes(c, byteorder='little')
    return c % ec.q


def musig_distributed_with_key_verification(m, user_key, pub_keys_entry, address_dict, hostname, port,
                                            ec=curve.secp256k1, h_com=hs.sha256, h_agg=hs.sha256, h_sig=hs.sha256,
                                            h_tree=hs.sha256, complete_pub_keys_list=None, restrictions=None):
    """
    Implementação do esquema de multi-assinatura MuSig no cenário n-de-m (n signatários de um conjunto de m signatários).
    O signatário deve fornecer uma mensagem m a ser assinada, seu par de chaves privada/pública, as chaves públicas
    de seus co-signatários, o endereço (ip, porta) de cada um de seus co-signatários, o hostname, a curva elíptica
    a ser utilizada, quatro funções de hash, uma para a fase de comprometimento, outra para calcular a chave agregada,
    uma para calcular a assinatura e outra a ser utilizada na árvore de Merkle. Opcionalmente, caso a chave agregada
    não utilize todas as chaves públicas de L = {X_1,...,X_n}, ele deverá ser fornecido. Caso haja restrições de
    combinações de chaves de L, elas deverão ser fornecidas para a produção de uma árvore de Merkle apropriada.

    O protocolo de assinatura retorna a assinatura (R,s), a chave agregada utilizada na assinatura e uma prova de
    pertencimento desta chave a árvore de Merkle produzida a partir de L e das restrições.

    :param str m: mensagem a ser assinada
    :param tuple user_key: tupla contendo o par de chaves do signatário na forma (chave_privada, chave_pública)
    :param list pub_keys_entry: lista contendo todas as chaves públicas dos co-signatários participantes do protocolo
    :param dict address_dict: lista contendo todos os endereços dos co-signatários na forma
    :param string hostname: hostname/ip do signatário
    :param int port: porta do signatário
    :param Curve ec: curva elíptica
    :param func h_com: função de hash H_com utilizada na fase de comprometimento
    :param func h_agg: função de hash H_agg utilizada no calculo da chave agregada
    :param func h_sig: função de hash H_sig utilizada na assinatura
    :param func h_tree: função de hash H_tree utilizada na construção da árvore de Merkle
    :param list complete_pub_keys_list: lista contendo todas as chaves públicas de todos os membros do grupo
    :param list restrictions: lista de tuplas de chaves públicas contendo as restrições de combinações de chaves. Por exemplo, não devem ser combinadas as chaves X_1, X_2 e X_3 entre si e as chaves X_4 e X_5 entre si, logo restrictions = [(X_1,X_2,X_3),(X_4,X_5)]
    :return: assinatura (R,s), chave pública agregada X e prova P
    """
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
    ok = check_commits(commit_list, r_point_list, hash_function=h_com)
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

    if complete_pub_keys_list is None:
        complete_pub_keys_list = pub_keys.copy()

    print(f'COMPLETE PUB KEYS LIST:\n{complete_pub_keys_list}')

    merkle_tree = merkle.build_merkle_tree(complete_pub_keys_list, restrictions=restrictions, hash_function=h_tree)

    print('$'*80)
    print(f'MERKLE TREE:\n{merkle_tree}')
    print('$' * 80)

    proof = merkle.produce_proof(aggregated_key, merkle_tree, hash_function=h_tree)

    return r_point, partial_signature, aggregated_key, proof


def musig_ver(r_point, s, m, aggregated_key, ec=curve.secp256k1, h_sig=hs.sha256):
    """
    Verifica se uma assinatura (R,s) é válida para uma mensagem m e uma chave agregada, baseado no esquema MuSig.
    :param Point r_point: ponto R
    :param int s: assinatura parcial s
    :param str m: mensagem a ser assinada
    :param Point aggregated_key: chave pública agregada
    :param Curve ec: curva elíptica
    :param func h_sig: função de hash H_sig utilizada na assinatura
    :return: True se (R,s) é válida para m e a chave agregada, caso contrário, False
    """

    if (r_point is None) or (s is None) or (m is None) or (aggregated_key is None):
        print('[V] Missing parameters')
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


def aggregated_key_verification(aggregated_key, proof, root, hash_function=hs.sha256):
    """
    Verifica se a chave agregada é uma combinação válida do conjunto de chaves públicas utilizado na assinatura, por
    meio da prova apresentada junto a chave agregada e uma raiz íntegra da árvore de Merkle construída a partir das
    combinações válidas das chaves públicas.

    :param Point aggregated_key: chave pública agregada
    :param list proof: prova de que a chave pública agregada é uma combinação válida de chaves públicas dos signatários
    :param bytes root: raiz íntegra da árvore de hash de todas as combinações válidas de chaves públicas dos signatários
    :param func hash_function: função de hash H_tree utilizada na construção da árvore de Merkle
    :return: True se a chave agregada é válida, caso contrário, False
    """

    if (root is None) or (aggregated_key is None) or (proof is None):
        print('[V] ERROR: missing parameters')
        return False

    else:

        if merkle.verify(root, aggregated_key, proof):
            return merkle.verify(root, aggregated_key, proof, hash_function=hash_function)
        else:
            print('[V] KEY_FAIL: aggregated key is invalid')
            return False


def musig_ver_with_key_verification(r_point, s, m, proof, aggregated_key, root, ec=curve.secp256k1, h_sig=hs.sha256,
                                    h_tree=hs.sha256):
    """
    Executa a verificação da chave pública agregada, e, caso ela seja uma combinação válida de chaves públicas, verifica
    a assinatura em questão, retornando o resultado das verificações.

    :param Point r_point: ponto R
    :param int s: assinatura parcial s
    :param str m: mensagem a ser assinada
    :param list proof: prova de que a chave pública agregada é uma combinação válida de chaves públicas dos signatários
    :param Point aggregated_key: chave pública agregada
    :param bytes root: raiz íntegra da árvore de hash de todas as combinações válidas de chaves públicas dos signatários
    :param Curve ec: curva elíptica
    :param func h_sig: função de hash H_sig utilizada na assinatura
    :param func h_tree: função de hash H_tree utilizada na construção da árvore de Merkle
    :return: True se a chave agregada é válida e se a assinatura (R,s) é válida para os parametros fornecidos, caso contrário, False.
    """

    agg_key_ok = aggregated_key_verification(aggregated_key, proof, root, hash_function=h_tree)

    if agg_key_ok:
        return musig_ver(r_point, s, m, aggregated_key, ec=ec, h_sig=h_sig,)
    else:
        print("[V] Aggregated key is invalid")
        return False

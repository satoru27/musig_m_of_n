import binarytree as bt
import hashlib as hs
import threading
from fastecdsa import curve
from itertools import combinations
#from math import log2
import pointsort
import keystorage

VISUAL = False


def build_tree(leafs, tree, hash_function=hs.sha256):
    """Constrói recursivamente uma árvore binária que utiliza a notação de lista. É providenciado também uma opção
    controlada pela variável global VISUAL que permite que sejam adicionados na árvore apenas uma parcela inicial
    dos valores de hash para que árvore possa ser visualizada no terminal com a função binarytree.build(tree)"""
    # using the array format of a tree as the output: https://en.wikipedia.org/wiki/Binary_tree#Arrays

    if len(leafs) == 1:
        # if len(leafs) == 1 then leafs[0] is the root of the tree and the recursion should stop
        if VISUAL:
            tree.append(int.from_bytes(leafs[0], byteorder='little') // (10 ** 70))
            # the above version of the append is to be used if you want the visual representation of the tree as the binarytree library only takes a number as the input
        else:
            tree.append(leafs[0])
        return

    next_level = []
    i = 0
    while i < len(leafs):
        next_level.append(leaf_hash(leafs[i], leafs[i+1], hash_function=hash_function))
        i += 2

    build_tree(next_level, tree, hash_function=hash_function)
    for leaf in leafs:
        if VISUAL:
            tree.append(int.from_bytes(leaf, byteorder='little') // (10 ** 70))
            # the above version of the append is to be used if you want the visual representation of the tree as the binarytree library only takes a number as the input
        else:
            tree.append(leaf)


def calculate_aggregated_keys(leafs, unique_l, hash_function=hs.sha256):
    """Calcula todas as chaves agregadas possíveis a partir de uma lista contendo todas as chaves públicas a serem
    utilizadas, sem restrições de combinações"""
    # calculate all the possible aggregated keys, including 2-of-n, 3-of-n etc
    # input := list of public keys
    # output := list of all possible aggregated keys in a specific order

    out = []
    n = len(leafs)

    for i in range(1, n+1):
        comb_set = combinations(leafs, i)
        for subset in comb_set:
            # print(80 * '-')
            # print(f'SUBSET:\n{subset}')
            subset_len = len(subset)
            if subset_len == 1:
                #out.append(subset[0])
                continue
            else:
                # print(f'SUBSET LEN: {subset_len}')
                # calculate a for the subset
                subset_a = calculate_a(subset, unique_l, hash_function=hash_function) # using curve.secp256k1 by default
                # print(f'SUBSET A: \n{subset_a}')
                temp = subset_a[0]*subset[0]
                for j in range(1, subset_len):
                    temp += subset_a[j]*subset[j] # X' = a1*X1 + ... + an*Xn
                out.append(temp)

    return out


def threaded_hashes(input, hash_function=hs.sha256):
    """Dada uma lista (input) como entrada, são criadas threads para o cálculo de do hash de cada um dos valores
    presentes na lista. Como a lista é ordenada e deseja-se manter essa mesma ordenação de valores para o hash desses
    valores, é fornecido como entrada da thread um indice que indica a sua posição na lista para que a saída seja
    reorganizada, uma vez que a ordem de finalização das threads é incerta."""
    # calculate hashes in parallel
    # input := list of values to be hashed
    # output := list of hashed values

    input_len = len(input)
    thread_list = []
    output = []
    for i in range(input_len):
        thread = threading.Thread(target=thread_hash, args=(input[i], i, output, hash_function))
        thread_list.append(thread)
        thread.start()

    for thread in thread_list:
        thread.join()

    return output


def thread_hash(input, index, output, hash_function=hs.sha256):
    """Calcula o valor hash de uma entrada e adiciona uma tupla desse hash junto ao indice fornecido na lista de
     saída"""
    h = hash_function()
    h.update((str(input)).encode())
    h = h.digest()
    output.append((index, h))


def leaf_hash(input1, input2, hash_function=hs.sha256):
    """Calcula o hash de um nó pai utilizando valores de hash dos seus filhos"""
    h = hash_function()
    h.update(input1)
    h.update(input2)
    return h.digest()


def sort_hashes(input):
    """Ordena uma lista de valores de hash cada qual com um prefixo correspondente a sua posição na lista"""
    # sort a list of hashes in the following format (prefix, hash)
    # the hash order needs to be the same for all the the signers

    if len(input) > 1:
        mid = len(input)//2
        left = input[:mid]
        right = input[mid:]

        sort_hashes(left)
        sort_hashes(right)

        i, j, k = 0, 0, 0

        while i < len(left) and j < len(right):
            # print(f'right {right[j][0]} left {right[j][0]}')
            if right[j][0] > left[i][0]:
                input[k] = left[i]
                i += 1
            else:
                input[k] = right[j]
                j += 1
            k += 1

        while i < len(left):
            input[k] = left[i]
            i += 1
            k += 1

        while j < len(right):
            input[k] = right[j]
            j += 1
            k += 1


def clear_hash_list(input):
    """A partir de uma lista com valores de hash ordenados pelo seu prefixo obtida através da função sort_hashes
    é gerada uma nova lista contendo apenas os valores de hash ordenados"""
    out = []
    for item in input:
        out.append(item[1])
    return out


def calculate_a(subset, unique_l, ec=curve.secp256k1, hash_function=hs.sha256):
    """Calcula o valor de a_i = H_agg(L, X_i)"""
    # PUB KEYS MUST BE SORTED BEFOREHAND
    # IF THE COMPLETE SET IS ORDERED THEN THE SUBSETS ARE ORDERED
    # input =: subset of n public keys
    # output =: [Hagg(<Ln>,X1),Hagg(<Ln>,X2),...,Hagg(<Ln>,Xn)]

    subset_a = []
    for key in subset:
        a = hash_function()
        a.update((unique_l + str(key)).encode())
        a = a.digest()
        a = int.from_bytes(a, byteorder='little')
        a = a % ec.q
        subset_a.append(a)

    print(f'SUBSET_A: {subset_a}')

    return subset_a


def calculate_l(pub_keys, hash_function=hs.sha256):
    """Produz uma codificação única <L> de L={X_1,...,X_n}. Ordenando L com base na ordem lexicográfica e produzindo
    <L> a partir do hash de L ordenado"""
    pointsort.sort(pub_keys)
    l = hash_function()
    l.update(str(pub_keys).encode())
    #return int.from_bytes(l.digest(), byteorder='little')
    return str(l.digest())


def build_merkle_tree(complete_public_key_list, restrictions=None, hash_function=hs.sha256):
    """Constrói a árvore de Merkle a partir de um conjunto de chaves públicas, considerando possíveis restrições de
    combinações"""

    unique_l = calculate_l(complete_public_key_list, hash_function=hash_function)

    if restrictions is None:
        aggregated_keys = calculate_aggregated_keys(complete_public_key_list, unique_l, hash_function=hash_function)
    else:
        aggregated_keys = calculate_aggregated_keys_with_restrictions(complete_public_key_list, restrictions, unique_l,
                                                                      hash_function=hash_function)

    hash_list = threaded_hashes(aggregated_keys, hash_function=hash_function)

    sort_hashes(hash_list)

    hash_list = clear_hash_list(hash_list)

    adjust_leafs_for_binary_tree(hash_list)

    merkle_tree = []
    build_tree(hash_list, merkle_tree, hash_function=hash_function)

    return merkle_tree


def standard_hash(value, hash_function=hs.sha256):
    """Realiza o calculo de hash da entrada e fornece o seu valor em formato de b-string"""
    h = hash_function()
    h.update((str(value)).encode())
    return h.digest()


def produce_proof(key, tree, hash_function=hs.sha256):
    """Produz uma prova de que a chave pública agregada (key) pertence a árvore (binária) de Merkle representada em
    formato de lista. É calculado o hash da chave pública agregada, identificado o índice desse hash na lista da
    árvore, esse índice é então fornecido para a função recursiva tree_search, junto a árvore de Merkle e uma lista
    vazia onde serão adicionados os nós que compõem a prova."""

    key_hash = standard_hash(key, hash_function=hash_function)

    print(80 * '-')
    print(f'Key hash = {key_hash}')

    key_index = None
    total_nodes = len(tree)
    i = -1

    # a busca sera feita a partir do final da arvore no formato de lista
    # uma vez que o hash das chaves se encontram no final da lista
    # O(n) n := numero de combinacoes de chaves
    while i > (total_nodes*(-1)):
        if tree[i] == key_hash:
            key_index = total_nodes + i # index = len(tree) - reverse position
            break
        i -= 1

    print(80 * '-')
    print(f'Key index = {key_index}')

    proof = []

    tree_search(key_index, tree, proof)

    return proof


def tree_search(index, tree, output):
    """Constrói uma prova (output) que indica que uma folha (cujo indice é fornecida na primeira execução)
    faz parte da árvore de Merkle fornecida, percorrendo recursivamente a árvore binária (tree) expressa em forma de
    lista, identificando o nó pai do nó correspondente ao índice fornecido (index), adicionando os dois filhos desse
    nó pai a prova output e realizando esse processo no nível superior da árvore, fornecendo o índice do nó pai como
     a nova entrada index, parando a recursão quando é identificado que o nó analisado é a raiz."""

    if index == 0:
        print('INDEX IS ROOT')
        return

    if index is None:
        print('KEY HASH NOT FOUND')
        return

    parent_index = (index - 1)//2 # // already makes the floor

    print(80 * '-')
    print(f'PARENT INDEX:{parent_index} - {tree[parent_index]}\nCHILD1 INDEX:{2*parent_index + 1} - {tree[2*parent_index + 1]}\nCHILD2 INDEX:{2*parent_index + 2} - {tree[2*parent_index + 2]}')

    first_child = tree[2*parent_index + 1]
    second_child = tree[2*parent_index + 2]

    output.append(first_child)
    output.append(second_child)

    tree_search(parent_index, tree, output)


def verify(root, key, proof, hash_function=hs.sha256):
    """Verifica se a raiz calulada a partir da prova e da chave pública agregada é equivalente a raiz integra da árvore
    de Merkle contruída a partir de combinações permitidas de chaves públicas"""
    hash_value = standard_hash(key, hash_function=hash_function)
    proof_len = len(proof)
    i = 0
    print(80 * '-')
    print(f'VERIFICATION')
    while i < proof_len:
        print(f'HASH VALUE: {hash_value}\nPROOF {i}: {proof[i]}\nPROOF {i+1}: {proof[i+1]}')
        if hash_value == proof[i] or hash_value == proof[i+1]:
            hash_value = leaf_hash(proof[i], proof[i + 1], hash_function)
            i += 2
            print(f'{i-2} OK - {hash_value}')
            print(80 * '-')
            # the last hash calculated will be the proof root
        else:
            print(f'{i} X')
            print(80 * '-')
            print(f'FAIL -> PROOF MISMATCH')
            return False

    if root == hash_value:
        print(80 * '-')
        print(f'PASS -> KEY IS VALID')
        return True
    else:
        print(80 * '-')
        print(f'FAIL -> ROOT MISMATCH')
        return False


def ispoweroftwo(value):
    """Checa se o valor dado como entrada é uma potência de dois"""
    if value > 0 and (value & value-1) == 0:
        return True
    else:
        return False


def adjust_leafs_for_binary_tree(entry_list):
    """Checa se o número de entradas na lista apresentada como a lista que contem as folhas é uma potencia de dois
     para que seja montada uma arvore binaria, caso seja, não sao realizadas mudanças, caso não seja, o último
     valor é copiado e adicionado ao final da lista até que o número de entradas na lista seja uma potência de dois"""
    if ispoweroftwo(len(entry_list)):
        return True

    size = len(entry_list)
    i = 1

    while size > 2**i:
        i += 1

    k = 2**i - size

    last_value = entry_list[-1]

    for j in range(k):
        entry_list.append(last_value)

    if ispoweroftwo(len(entry_list)):
        return True
    else:
        return False


def sort_restriction(restrictions):
    """Ordena internamente as tuplas de restrições fornecidas para que mantenha-se um padrão de identificação de um
    subset, uma vez que uma vez que (x,y) != (y,x), porém dentro da nossa interpretação não importa a ordem em que os
    elementos de um subset são apresentados."""
    # restrictions := [(key1),(key1,key2),...]
    # there is a great chance that the restrictions are unordered with relation to the subsets, so we need to
    # internally sort them

    ordered_restrictions = []

    for restriction in restrictions:
        # print(80 * '-')
        # print(f'RESTRICTION:\n{restriction}')
        temp = []
        for item in restriction:
            temp.append(item)
        pointsort.sort(temp)
        # print(f'SORTED:\n{temp}')
        # print(f'TUPLE AGAIN:\n{tuple(temp)}')
        ordered_restrictions.append(tuple(temp))

    return ordered_restrictions


def calculate_aggregated_keys_with_restrictions(leafs, restrictions, unique_l, hash_function=hs.sha256):
    """Calcula todas as chaves agregadas possíveis a partir de uma lista contendo todas as chaves públicas a serem
        utilizadas, considerando as restrições de combinações fornecidas."""
    # calculate all the possible aggregated keys, including 2-of-n, 3-of-n etc
    # input := list of public keys
    # output := list of all possible aggregated keys in a specific order

    # restrictions must be in the form
    ordered_restrictions = sort_restriction(restrictions)

    out = []
    n = len(leafs)

    for i in range(1, n+1):
        comb_set = combinations(leafs, i)
        for subset in comb_set:
            print(80 * '-')
            print(f'SUBSET:\n{subset}')
            print(f'RESTRICTIONS:\n{ordered_restrictions}')
            if subset in ordered_restrictions:
                out.append(None)
            else:
                subset_len = len(subset)
                print(f"SUBSET LEN = {subset_len}")
                if subset_len == 1:
                    #out.append(subset[0])
                    #out.append(None)
                    continue

                else:
                    # print(f'SUBSET LEN: {subset_len}')
                    # calculate a for the subset
                    subset_a = calculate_a(subset, unique_l, hash_function=hash_function) # using curve.secp256k1 by default
                    # print(f'SUBSET A: \n{subset_a}')
                    temp = subset_a[0]*subset[0]
                    for j in range(1, subset_len):
                        temp += subset_a[j]*subset[j] # X' = a1*X1 + ... + an*Xn
                    out.append(temp)

    i = 0
    for item in out:
        j = i-1
        if item is None:
            while out[j] is None:
                j -= 1 # achar o primeiro elemento diferente de None anterior ao None atual
                       # o while e necessario pois se out[0] = None a solucao seria colocar o ultimo elemento
                       # de out no lugar, mas e se esse elemento por None tambem ? Por simplicidade
                       # acredito que esta e a melhor maneira. Mas fora esse caso, o programa nao ira entrar no while
                       # uma vez que i-1 sera um valor diferente de None
            out[i] = out[j]
        i += 1

    return out


def main():
    k1 = keystorage.import_keys('key4.pem')
    k2 = keystorage.import_keys('key90.pem')
    k3 = keystorage.import_keys('key2.pem')

    list = [k1[1], k2[1], k3[1]]

    print(list)

    # PUB KEYS MUST BE SORTED

    # out = calculate_aggregated_keys(list)
    #
    # out = threaded_hashes(out)
    # print(out)
    #
    # print(80*'-')
    # sort_hashes(out)
    # print(out)
    #
    # out = clear_hash_list(out)
    # print(80 * '-')
    # print(out)
    # print(f'LEN -> {len(out)}')
    #
    # adjust_leafs(out)
    # print(80 * '-')
    # print(out)
    # print(f'LEN -> {len(out)}')

    #tree = build_merkle_tree(list)
    tree = build_merkle_tree(list, restrictions=[(list[1],list[2])])

    #print(80 * '-')
    #print(f'TREE: \n{tree}')

    #proof = produce_proof(list[0], tree)

    #print(80 * '-')
    #print(f'PROOF = {proof}')

    #result = verify(tree[0], list[0], proof)


    root = bt.build(tree)
    print(root)





if __name__ == "__main__":
    main()
import binarytree as bt
import hashlib as hs
import threading
from fastecdsa import curve
from itertools import combinations
from math import log2
import pointsort
import keystorage

VISUAL = False


def build_tree(leafs, tree):
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
        next_level.append(leaf_hash(leafs[i], leafs[i+1]))
        i += 2

    build_tree(next_level, tree)
    for leaf in leafs:
        if VISUAL:
            tree.append(int.from_bytes(leaf, byteorder='little') // (10 ** 70))
            # the above version of the append is to be used if you want the visual representation of the tree as the binarytree library only takes a number as the input
        else:
            tree.append(leaf)


def adjust_leafs(leafs):
    number_of_entrys = len(leafs)
    while not (log2(number_of_entrys).is_integer()):
        # repeat the last entry until the the number of leafs is a power of two
        leafs.append(leafs[-1])
        number_of_entrys = len(leafs)


def calculate_aggregated_keys(leafs):
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
                out.append(subset[0])
            else:
                # print(f'SUBSET LEN: {subset_len}')
                # calculate a for the subset
                subset_a = calculate_a(subset) # using curve.secp256k1 by default
                # print(f'SUBSET A: \n{subset_a}')
                temp = subset_a[0]*subset[0]
                for j in range(1, subset_len):
                    temp += subset_a[j]*subset[j] # X' = a1*X1 + ... + an*Xn
                out.append(temp)

    return out


def threaded_hashes(input):
    # calculate hashes in parallel
    # input := list of values to be hashed
    # output := list of hashed values

    input_len = len(input)
    thread_list = []
    output = []
    for i in range(input_len):
        thread = threading.Thread(target=hash, args=(input[i], i, output))
        thread_list.append(thread)
        # thread.daemon = Trueec=curve.secp256k1
        thread.start()

    for thread in thread_list:
        thread.join()

    return output


def hash(input, index, output):
    h = hs.sha256()
    h.update((str(input)).encode())
    h = h.digest()
    output.append((index, h))


def leaf_hash(input1, input2):
    h = hs.sha256()
    h.update(input1)
    h.update(input2)
    return h.digest()


def sort_hashes(input):
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
    out = []
    for item in input:
        out.append(item[1])
    return out


def calculate_a(subset, ec=curve.secp256k1):
    # PUB KEYS MUST BE SORTED BEFOREHAND
    # IF THE COMPLETE SET IS ORDERED THEN THE SUBSETS ARE ORDERED
    # input =: subset of n public keys
    # output =: [Hagg(<Ln>,X1),Hagg(<Ln>,X2),...,Hagg(<Ln>,Xn)]

    # making the <Ln>
    # subset_l = ''
    # for key in subset:
    #     subset_l = subset_l + '|' + str(key)

    # gambiarra temporaria
    # str(tuple) != str(subset)
    # logo, como no musig o str(keys) e uma lista e aqui str(keys) e uma tupla, gera diferença
    temp = []
    for item in subset:
        temp.append(item)
    subset_l = str(temp)
    print(80*'-')
    print(f'SUBSET: {temp}')

    subset_a = []
    for key in subset:
        a = hs.sha256()
        a.update((subset_l + str(key.x) + str(key.y)).encode())
        a = a.digest()  # size 48 bytes
        a = int.from_bytes(a, byteorder='little')
        a = a % ec.q
        subset_a.append(a)

    print(f'SUBSET_A: {subset_a}')

    return subset_a


def build_merkle_tree(keys, sorted_keys=False, restrictions=None):
    if not sorted_keys:
        pointsort.sort(keys)

    if restrictions is None:
        aggregated_keys = calculate_aggregated_keys(keys)
    else:
        aggregated_keys = calculate_aggregated_keys_with_restrictions(keys, restrictions)

    hash_list = threaded_hashes(aggregated_keys)

    sort_hashes(hash_list)

    hash_list = clear_hash_list(hash_list)

    adjust_leafs(hash_list)

    merkle_tree = []
    build_tree(hash_list, merkle_tree)

    return merkle_tree


def standard_hash(value):
    h = hs.sha256()
    h.update((str(value)).encode())
    return h.digest()


def produce_proof(key, tree):
    key_hash = standard_hash(key)

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


def verify(root, key, proof):
    hash_value = standard_hash(key)
    proof_len = len(proof)
    i = 0
    print(80 * '-')
    print(f'VERIFICATION')
    while i < proof_len:
        print(f'HASH VALUE: {hash_value}\nPROOF {i}: {proof[i]}\nPROOF {i+1}: {proof[i+1]}')
        if hash_value == proof[i] or hash_value == proof[i+1]:
            hash_value = leaf_hash(proof[i], proof[i + 1])
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


def print_tree(tree):
    pass


# ------------------ TESTING BUILD TREE WITH RESTRICTIONS ---------------------

def sort_restriction(restrictions):
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


def calculate_aggregated_keys_with_restrictions(leafs, restrictions):
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
                if subset_len == 1:
                    out.append(subset[0])
                else:
                    # print(f'SUBSET LEN: {subset_len}')
                    # calculate a for the subset
                    subset_a = calculate_a(subset) # using curve.secp256k1 by default
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

    tree = build_merkle_tree(list)
    #tree = build_merkle_tree(list,restrictions=[(list[1], list[2])])

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
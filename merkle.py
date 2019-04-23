import binarytree as bt
import hashlib as hs
import threading
from fastecdsa import curve
from itertools import combinations
from math import log2
import pointsort
import keystorage

VISUAL = True


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
            #print(subset)
            # calculate a for the subset
            subset_len = len(subset)
            subset_a = calculate_a(subset) # using curve.secp256k1 by default
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
    subset_l = ''
    for key in subset:
        subset_l = subset_l + '|' + str(key)

    subset_a = []
    for key in subset:
        a = hs.sha256()
        a.update((subset_l + str(key.x) + str(key.y)).encode())
        a = a.digest()  # size 48 bytes
        a = int.from_bytes(a, byteorder='little')
        a = a % ec.q
        subset_a.append(a)

    return subset_a


def build_merkle_tree(keys, sorted_keys=False):
    if not sorted_keys:
        pointsort.sort(keys)

    aggregated_keys = calculate_aggregated_keys(keys)

    hash_list = threaded_hashes(aggregated_keys)

    sort_hashes(hash_list)

    hash_list = clear_hash_list(hash_list)

    adjust_leafs(hash_list)

    merkle_tree = []
    build_tree(hash_list, merkle_tree)

    return merkle_tree


def produce_proof():
    pass


def verify():
    pass


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

    root = bt.build(tree)
    print(root)





if __name__ == "__main__":
    main()
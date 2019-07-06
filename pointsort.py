def sort(pub_key_list):
    """Ordena um multiset de chaves públicas pub_key_list com base na ordem lexicográfica utilizando o merge sort"""
    # sort the public key list L into a unique encoding <L>
    # the lexicographical order will be used
    # merge sort will be used
    # http://interactivepython.org/courselib/static/pythonds/SortSearch/TheMergeSort.html

    if len(pub_key_list) > 1:
        mid = len(pub_key_list)//2
        left = pub_key_list[:mid]
        right = pub_key_list[mid:]

        sort(left)
        sort(right)

        i, j, k = 0, 0, 0

        while i < len(left) and j < len(right):
            if compare_points(left[i], right[j]) == 1:
                pub_key_list[k] = left[i]
                i += 1
            else:
                pub_key_list[k] = right[j]
                j += 1
            k += 1

        while i < len(left):
            pub_key_list[k] = left[i]
            i += 1
            k += 1

        while j < len(right):
            pub_key_list[k] = right[j]
            j += 1
            k += 1


def compare_points(p1, p2):
    """Compara dois pontos de uma mesma curva elíptica com base na ordem lexicográfica, analisando primeiro a
    a coordenada x dos pontos, caso elas sejam iguais, é comparada a coordenada y dos pontos.
    Se P1 > P2, então é retornado 0.
    Se P2 > P1, então é retornado 1.
    Se P1 == P2, então é retornado 2.
    """
    # compare two of the same elliptic curve
    # first P1.x is compared with P2.x
    # if they are equal, then look at P1.y and P2.y
    # if P1 > P2 is true, then return 0
    # if P1 < P2 is true, then return 1
    # if P1 == P2, then return 2

    if p1.x > p2.x:
        return 0

    elif p2.x > p1.x:
        return 1

    elif p1.y > p2.y:
        return 0

    elif p2.y > p1.y:
        return 1

    else:
        return 2

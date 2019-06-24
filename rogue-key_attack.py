import keystorage
from os import system


def rogue_key_attack(adversary_key, pub_keys_list):
    """Simula um rogue-key attack a partir da chave pública do adversário (aquele que realiza o ataque) e as chaves
    públicas dos co-signatários honestos, calculando a chave utilizada pelo adversário no ataque (rogue-key), a chave
    pública agregada resultante e por fim, comparando a chave pública resultante com a real chave pública do adversário,
    caso estas forem iguais, o ataque foi bem sucedido, uma vez que a chave pública agregada depende apenas da chave
    privada do adversário."""

    print(f'Target aggregated key value is: {adversary_key}')
    print('_' * 80)
    print(f'Co-signers public keys: {pub_keys_list}')

    first = True
    pub_keys_sum = None

    for key in pub_keys_list:
        if first:
            pub_keys_sum = key
            first = False
        else:
            pub_keys_sum += key

    print('_' * 80)
    print(f'Sum of other public keys is: {pub_keys_sum}')
    pub_keys_sum_inv = -pub_keys_sum

    print('_' * 80)
    print(f'Inverse of the sum of target public keys is: {pub_keys_sum_inv}')
    rogue_key = adversary_key + pub_keys_sum_inv

    print('_' * 80)
    print(f'Rogue key value: {rogue_key}')

    aggregated_key = rogue_key + pub_keys_sum
    print('_' * 80)
    print(f'Final aggregated_key result: {aggregated_key}')

    equal = (aggregated_key.x == adversary_key.x) and (aggregated_key.y == adversary_key.y)
    print('_' * 80)
    print(f'Aggregated key is equal to adversary key: {equal}')

    return rogue_key


def test1():
    input('>TEST 1 ...')
    adversary_keys = keystorage.import_keys('k2.pem')
    key2 = keystorage.import_keys('key2.pem')
    key3 = keystorage.import_keys('key4.pem')
    key4 = keystorage.import_keys('key90.pem')

    pub_key_list = [key2[1], key3[1], key4[1]]

    rogue_key = rogue_key_attack(adversary_keys[1], pub_key_list)


def main():
    system('clear')
    test1()


if __name__ == "__main__":
    main()
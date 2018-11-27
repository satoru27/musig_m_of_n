import gmpy2 as gmp
import math as m
from gmpy2 import mpz


def random_prime():
    x = gmp.mpz_urandomb(gmp.random_state(), 1024)
    if gmp.is_prime(x):
        return x
    else:
        return gmp.next_prime(x)


def find_q(p):#otimizar para que seja possivel calcular com o random_prime
    found = False
    n = mpz(p-1)
    q = mpz(n/10000)
    q = mpz(1)
    qn = gmp.next_prime(q)
    r = mpz(0)

    # qr + 1 = p -> qr = p -1 -> p-1 mod q == 0
    # acha o maior q para determinado p
    while qn < p:
        if n%qn == 0:
            if qn > q:
                q = qn
                r = n/q

        qn = gmp.next_prime(qn)

    return q, r


def find_h(r, p):
    h = mpz(1)

    while h < p:
        if mpz(m.pow(h, r)) % p != 1:
            break
        else:
            h = h + 1

    return h

def schnorr_group():
    # https://en.wikipedia.org/wiki/Schnorr_group
    # testing with small numbers, after that, a suitable p should be used (with a large p)

    #p = random_prime()
    #p = mpz(55661)
    p = mpz(72109)
    print(f'p = {p}')

    # we must find p = qr + 1
    q, r = find_q(p)
    print(f'q = {q}\nr = {r}')

    # we must find h^r != 1 (mod p)
    h = find_h(r, p)
    print(f'h = {h}')

    # the generator g = h^r (mod p)
    g = pow(h, r) % p
    print(f'g = {g}')

    # show the cyclic subgroup G of Zp, generated using g^i, where i = 1,2,3... until g^k = g^0 = 1
    n = g
    print('{', end="")
    while n != 1:
        print(f'{n},', end="")
        n = (n * g) % p
    print('}')


def main():
    schnorr_group()

if __name__ == "__main__":
    main()



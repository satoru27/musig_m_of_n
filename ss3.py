import gmpy2 as gmp
from gmpy2 import mpz
import hashlib as hs
import random

def random_prime():
    x = gmp.mpz_urandomb(gmp.random_state(random.randint(0, 367263292)), 1024)
    if gmp.is_prime(x):
        return x
    else:
        return gmp.next_prime(x)

def find_q(p):#otimizar para que seja possivel calcular com o random_prime
    found = False
    n = mpz(p-1)
    q = mpz(n/2)
    #q = mpz(1)
    qn = gmp.next_prime(q)
    r = mpz(0)

    # qr + 1 = p -> qr = p -1 -> p-1 mod q == 0
    # acha o maior q para determinado p
    while qn < p:
        if n%qn == 0:
            if qn > q:
                q = qn
                r = mpz(n/q)

        qn = gmp.next_prime(qn)

    return q, r


def find_h(r, p):
    h = mpz(1)

    while h < p:
        if mpz(gmp.powmod(h, r, p)) != 1:
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
    #print(f'p = {p}')

    # we must find p = qr + 1
    q, r = find_q(p)
    #print(f'q = {q}\nr = {r}')

    # we must find h^r != 1 (mod p)
    h = find_h(r, p)

    # the generator g = h^r (mod p)
    g = gmp.powmod(h, r, p)

    return p, q, g


def define_group():
    # q = gmp.mpz_urandomb(gmp.random_state(random.randint(0, 367263292)), 1024)
    # if not gmp.is_prime(q):
    #     q = gmp.next_prime(q)
    #q = mpz(72109)
    q = mpz(17)
    g = gmp.mpz_random(gmp.random_state(random.randint(0, 367263292)), q-1)

    return q, g



def generate_keys(q, g): # where p is the order of the group generate by g
    x = gmp.mpz_random(gmp.random_state(random.randint(0, 367263292)), q)
    while x == 0:
        x = gmp.mpz_random(gmp.random_state(random.randint(0, 367263292)), q)
    y = gmp.powmod(g, x, q)

    return x, y

def sign_message(q, g, x, m):
    k = gmp.mpz_random(gmp.random_state(random.randint(0, 367263292)), q)
    while k == 0:
        k = gmp.mpz_random(gmp.random_state(random.randint(0, 367263292)), q)
    r = gmp.powmod(g, k, q)
    e = hs.sha256()
    e.update(str(r).encode() + m.encode())
    e = mpz(e.hexdigest(), base=16) % q
    s = (k - x*e)# por alguma razao se colocar o %q no s ele falha

    print(f's = {s}\ne = {e}\nk = {k}')

    return s, e


def verify_signature(g, s, q, X, e, m):
    rv = (gmp.powmod(g, s, q) * gmp.powmod(X, e, q)) % q
    ev = hs.sha256()
    ev.update(str(rv).encode() + m.encode())
    ev = mpz(ev.hexdigest(), base=16) % q

    print(f'e = {e}')
    print(f'ev = {ev}')

    if e == ev:
        return True
    else:
        return False



def main():
    p, q, g = schnorr_group()
    #print(f'p={type(p)} \nq={type(q)} \nh={type(h)} \ng={type(g)}')
    #print(f'p = {p}\ng = {g}')
    print(f'q = {q}\ng = {g}')
    x, y = generate_keys(q, g)
    print(f'priv = {x}\npub = {y}')
    #print(f'priv = {type(x)}\npub = {type(X)}')

    m = "Hello World!"

    s, e = sign_message(q, g, x, m)
    # print(f'R = {R}\ns = {s}\nc = {c}')

    print(verify_signature(g, s, q, y, e, m))

    print(verify_signature(g, s, q, mpz(622), e, m))

    #print(verification)

if __name__ == "__main__":
    main()

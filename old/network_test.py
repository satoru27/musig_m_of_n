import p2pnetwork
import sys

# def send_t(setup_tuple):
#     key = setup_tuple[0]
#     address = setup_tuple[1]
#     t = setup_tuple[2]
#     signer_comm = SignerSocket()
#     signer_comm.connect(address)
#     signer_comm.send_msg(t+':'+key)
#     #signer_comm.close()
#
# def multi_thread_receive_t(address_dict):
#     n = len(address_dict)
#     signer_comm = SignerSocket()
#     signer_comm.bind()
#     pool = ThreadPool()
#     t_lst = pool.map(signer_comm.receive_setup, range(n))
#     pool.close()
#     pool.join()
#     return t_lst

# signer 1: key90,'127.0.0.1', 2436
# signer 2: key2, '127.0.0.1', 2437
# signer 3: key4, '127.0.0.1', 2438

ADDR_LST = [('127.0.0.1', 2436), ('127.0.0.1', 2437), ('127.0.0.1', 2438), ('127.0.0.1', 2439)]

SIG1_ADDR = ('127.0.0.1', 2436)
SIG2_ADDR = ('127.0.0.1', 2437)
SIG3_ADDR = ('127.0.0.1', 2438)
SIG4_ADDR = ('127.0.0.1', 2439)

SIG1_MSG = '@@_T1_@@'
SIG2_MSG = '**_T2_**'
SIG3_MSG = '&&_T3_&&'
SIG4_MSG = '!!_T4_!!'


def sig1():
    return p2pnetwork.p2p_get(SIG1_ADDR, ADDR_LST, SIG1_MSG)


def sig2():
    return p2pnetwork.p2p_get(SIG2_ADDR, ADDR_LST, SIG2_MSG)


def sig3():
    return p2pnetwork.p2p_get(SIG3_ADDR, ADDR_LST, SIG3_MSG)


def sig4():
    return p2pnetwork.p2p_get(SIG4_ADDR, ADDR_LST, SIG4_MSG)


def main():
    temp = None
    if sys.argv[1] == '1':
        temp = sig1()
    elif sys.argv[1] == '2':
        temp = sig2()
    elif sys.argv[1] == '3':
        temp = sig3()
    elif sys.argv[1] == '4':
        temp = sig4()

    print(temp)


if __name__ == "__main__":
    main()

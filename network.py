import socket
from multiprocessing.dummy import Pool as ThreadPool
import time

MSGLEN = 1024


class SignerSocket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

        self.pub_key_list = []
        self.n = 0
        self.address_dict = {}
        # 'pub_key':('ip','port')
        self.t = None

    def set_t(self, t):
        self.t = t

    def set_pub_key_list(self, pub_keys):
        if isinstance(pub_keys, list):
            self.pub_key_list = pub_keys
            self.n = len(pub_keys)
        else:
            print('Pub key is not a list')

    def set_address_dict(self, address_dict):
        if isinstance(address_dict, dict):
            self.address_dict = address_dict
        else:
            print('Address dict is not a dict')

    def bind(self, host_name='localhost', port=2436):
        host = socket.gethostbyname(host_name)
        self.sock.bind((host, port))
        print(f'Binded at {host} : {port}')

    def listen(self, n=1):
        #print('Listening')
        self.sock.listen(n)

    def accept(self):
        return self.sock.accept()

    def receive_msg(self, target_socket):
        # self.listen()
        # arget_socket, target_address = self.accept()
        # necessario listen e depois accept da conexao
        chunks = []
        bytes_received = 0
        while bytes_received < MSGLEN:
            chunk = target_socket.recv(min(MSGLEN - bytes_received, 2048))
            if chunk == b'':
                raise RuntimeError("Socket connection broken")
            chunks.append(chunk)
            bytes_received += len(chunk)
            return b''.join(chunks)

    def connect(self, addr):
        # # addr = (ip,port)
        self.sock.connect(addr)

    def send_msg(self, msg):
        # necessario connect antes
        msg = msg.encode('utf-8')
        total_sent = 0
        msg_len = len(msg)
        while total_sent < msg_len:
            sent = self.sock.send(msg[total_sent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            total_sent += sent

    def receive_setup(self, id_list):
        self.listen()
        target_socket, target_address = self.accept()
        msg = self.receive_msg(target_socket)
        print(msg)
        return msg

    def receive_t(self):
        pass

    def send_r(self):
        pass

    def receive_r(self):
        pass


def send_t(setup_tuple):
    print('Sending...')
    address = setup_tuple[0]
    t = setup_tuple[1]
    signer_comm = SignerSocket()
    counter = 0
    while counter < 100:
        try:
            signer_comm.connect(address)
        except socket.error as error:
            print(f"Connection Failed **BECAUSE:** {error}")
            print(f"Attempt {counter} of 100")
            print(f'Sleeping for 2s...')
            time.sleep(2)
            counter += 1
    signer_comm.send_msg(t)
    #signer_comm.close()


def multi_thread_send_t(iterable):
    # iterable = [(address1, commit1), (address2, commit2), ...]
    pool = ThreadPool(len(iterable))
    pool.map(send_t, iterable)
    pool.close()
    pool.join()


def multi_thread_receive_t(address_dict, host_name, port, result_queue):
    print('Receiving...')
    n = len(address_dict)
    signer_comm = SignerSocket()
    signer_comm.bind(host_name = host_name, port= port)
    pool = ThreadPool()
    t_lst = pool.map(signer_comm.receive_setup, range(n))
    pool.close()
    pool.join()
    result_queue.put(t_lst)

def multi_thread_server(n, id_list, result_queue):
    signer_comm = SignerSocket()
    signer_comm.bind()
    pool = ThreadPool(n)
    results = pool.map(signer_comm.receive_setup, id_list)
    pool.close()
    pool.join()
    result_queue.put(results)






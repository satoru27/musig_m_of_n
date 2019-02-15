import socket
import threading
import sys
import time
import os

REQUEST_STRING = 'send_package'
CONTINUE_STRING = 'OK'
RETRY_MAX = 1000
PCKG_SIZE = 2048

# Investigar o pq do erro que ocorre mas nao acontece nada e o programa segue normalmente
# Error: [Errno 9] Bad file descriptor
# Exiting...
#
#

# server connects and sends package to the clients
class Server:
    def __init__(self, peer_list, package, my_addr):
        # peer_list includes all the addresses
        # the commit or R to be sent
        ## print(peer_list)
        self.peers = peer_list.copy()
        self.peers.remove(my_addr)
        self.package = package
        self.sent_counter = 0
        self.peers_number = len(self.peers)

        # define the socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.connections = []

        self.sock.bind(my_addr)

        self.sock.listen(1)

        # print("-" * 10 + "Server Running" + "-" *10)

        self.run()

    def run(self):
        # i = 0
        # while i < RETRY_MAX:
        # i += 1

        for k in range(self.peers_number):
            connection, address = self.sock.accept()
            # print(f'Connected to: {address}')
            self.connections.append(connection)

        # if not (address in self.peers):
        #     # print('Invalid Connection')
        #     connection.close()
        #     continue

        thread_list = []
        ## print(self.connections)
        for connection in self.connections:
            thread = threading.Thread(target=self.handler, args=(connection,))
            thread_list.append(thread)
            thread.daemon = True

        for thread in thread_list:
            thread.start()

        # for thread in thread_list:
        #     thread.join()

        i = 0
        while i < RETRY_MAX:
            i += 1
            if self.sent_counter == self.peers_number:
                break
            else:
                time.sleep(1)

        # print('-' * 10 + 'FINISHED SENDING PACKAGES' + '-' * 10)

        for connection in self.connections:
            thread = threading.Thread(target=self.send_permission, args=(connection,))
            thread_list.append(thread)
            # thread.daemon = True
            thread.start()

        #self.sock.shutdown(socket.SHUT_RDWR)
        # a forma correta seria esperar o join, porem parece que o socket bloqueia no recv, testar depois
        # necessario pq se nao na hora de receber o R o socket nao consegue conectar no mesmo endereco
        self.sock.close()



    def handler(self, connection):
        try:
            while True:
                # server receives the message
                data = connection.recv(PCKG_SIZE)

                if data.decode('utf-8') == REQUEST_STRING:
                    # print('-'*10 + 'SENDING PACKAGE' + '-'*10)
                    connection.send(self.package.encode('utf-8'))
                    self.sent_counter += 1

        except Exception as e:
            # print(f'Error: {e}\nExiting...')
            sys.exit()

    def send_permission(self, connection):
        # print('-' * 10 + 'SENDING OK' + '-' * 10)
        connection.send(CONTINUE_STRING.encode('utf-8'))
        connection.close()



# clients wait for the server and receives its package
class Client:
    def __init__(self, target_address):

        self.continue_permission = False

        self.target_address = target_address

        # define the socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        i = 0
        while i < RETRY_MAX:
            i += 1
            try:
                self.sock.connect(target_address)
            except Exception as e:
                # print(f'Caught exception: {e}')
                time.sleep(1)
                continue
            break

        request_thread = threading.Thread(target=self.send_package_request)
        request_thread.daemon = True
        request_thread.start()

        self.package = None

        i = 0
        while i < RETRY_MAX:
            i += 1
            self.package = self.receive_package()

            if not self.package:
                # print('-' * 10 + 'SERVER FAILED' + '-' * 10)
                break
            else:
                break

        i = 0
        while i < RETRY_MAX:
            i += 1
            self.receive_ok()

            if self.continue_permission:
                break

    def send_package_request(self):
        self.sock.send(REQUEST_STRING.encode('utf-8'))

    def receive_package(self):
        # print('-' * 10 + 'RECEIVING PACKAGE' + '-' * 10)
        # print(f'FROM: {str(self.target_address)}')
        package = self.sock.recv(PCKG_SIZE).decode('utf-8')
        # print(package)
        return package

    def receive_ok(self):
        # print('-' * 10 + 'WAITING FOR CONTINUE PERMISSION' + '-' * 10)
        package = self.sock.recv(PCKG_SIZE).decode('utf-8')
        if package == CONTINUE_STRING:
            self.continue_permission = True
            # print('> OK')


def p2p_get(my_addr, peer_list, package):
    #os.system('clear')
    # peer list order must be based on the order of the peers public keys, which is in a unique encoding L
    # peer_list = (ip,port)
    if not isinstance(package, str):
        package = str(package)

    if not isinstance(peer_list, list):
        # print('Peer list is invalid')
        sys.exit(0)
    # print(f'PEER LIST = {peer_list}')
    # print(f'MY ADDR = {my_addr}')
    peer_queue = peer_list.copy()
    rcv_list = []

    while peer_queue:
        ## print('!!!!!!!!!!!'+str(peer_list)+'!!!!!!!!!!!')
        if peer_queue[0] == my_addr:
            # act as server
            peer_queue.pop(0)
            server = Server(peer_list, package, my_addr)
            # keep the order of the received objects
            rcv_list.append(package)

        else:
            # act as client
            client = Client(peer_queue.pop(0))
            rcv_list.append(client.package)

    # print(f'AFTER PEER LIST = {peer_list}')

    return rcv_list


def r_point_converter():
    pass
import socket
import threading
import sys
import time
import os

SEND_FLAG = '<SEND_PKG>'
OK_FLAG = '<PKG_OK>'
CONTINUE_FLAG = '<CONTINUE>'

RETRY_MAX = 1000
PCKG_SIZE = 2048

# Investigar o pq do erro que ocorre mas nao acontece nada e o programa segue normalmente
# Error: [Errno 9] Bad file descriptor
# Exiting...
#
#

# server connects and sends package to the clients
class Server:
    """Implentação do servidor multi-thread que irá recebe conexões de múltiplos clientes e envia para eles o seu
    pacote (commit_1, R_1, s_1). Os signatários tomam turnos atuando como servidores. Quando um signatário atua como
    servidor, ele envia o seu pacote para cada um de seus co-signatários atuando como clientes. É necessário um
    consenso sobre a ordem de quando atuar como servidor e quando atuar como cliente"""
    def __init__(self, peer_list, package, my_addr):
        # peer_list includes all the addresses
        # the commit or R to be sent
        ## print(peer_list)
        self.peers = peer_list.copy()
        self.peers.remove(my_addr)
        self.package = package
        self.sent_counter = 0
        self.peers_number = len(self.peers)
        self.thread_list = []

        # define the socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.connections = []

        self.server_socket.bind(my_addr)

        self.server_socket.listen(1)

        # print("-" * 10 + "Server Running" + "-" *10)

        self.run()

    def run(self):
        """Prepara uma thread para receber a conexão de cada co-signatário"""
        # run the separated threads
        for peer in range(self.peers_number):
            print('*** Creating threads ***')
            thread = threading.Thread(target=self.handler)
            self.thread_list.append(thread)

        for thread in self.thread_list:
            print('*** Starting threads ***')
            thread.start()

        for thread in self.thread_list:
            thread.join()

        self.server_socket.close()

    def handler(self):
        """Função que é executada por cada thread criada em run(), recebe a conexão de um co-signatário, envia para
        ele o pacote, recebe a confirmação de recebimento do pacote, envia a permissão para o cliente continuar
        com a sua execução, espera todos os outros co-signatários enviarem a confirmação de recebimento do pacote
        e encerra a conexão com o co-signatário"""
        print('*** Handler initiated ***')
        connection_socket, connection_address = self.listen_phase()

        ok = self.wait_for_request(connection_socket, connection_address)
        if not ok:
            return

        self.send_pckg(connection_socket, connection_address)

        ok = self.receive_pckg_ok(connection_socket, connection_address)
        if not ok:
            return

        self.send_continue(connection_socket, connection_address)

        while self.sent_counter != self.peers_number:
            print(f'<Waiting for other peers to finish...>')
            time.sleep(1)

        self.end_connection(connection_socket, connection_address)


    def listen_phase(self):
        """Escuta por pedidos de conexão dos co-signatários"""
        print(f'<Listening for incoming connections...')
        connection, address = self.server_socket.accept()
        print(f'<Listen Phase: accepted connection {connection} from {address}>')
        return connection, address

    def wait_for_request(self, connection_socket, connection_address):
        """Espera, do cliente, o pedido de envio do pacote"""
        print(f'<Waiting for request from: {connection_address}>')
        request = receive_package(connection_socket)
        print(f'<Received {request} from {connection_address}>')
        if request == SEND_FLAG:
            return True
        else:
            return False

    def send_pckg(self, connection_socket, connection_address):
        """Envia o pacote para o cliente"""
        print(f'<Sending \"{self.package}\" to {connection_address}>')
        send_package(connection_socket, self.package)

    def receive_pckg_ok(self, connection_socket, connection_address):
        """Recebe do cliente a confirmação de recebimento do pacote"""
        print(f'<Waiting for ok from: {connection_address}>')
        ok = receive_package(connection_socket)
        print(f'<Received {ok} from {connection_address}>')
        if ok == OK_FLAG:
            return True
        else:
            return False

    def send_continue(self, connection_socket, connection_address):
        """Envia para o cliente a permissão para prosseguir"""
        print(f'<Sending {CONTINUE_FLAG} to {connection_address}>')
        send_package(connection_socket, CONTINUE_FLAG)
        self.sent_counter += 1

    def end_connection(self, connection_socket, connection_address): #should the client do this ?
        """Encerra a conexão com o cliente"""
        print(f'<Closing connection with {connection_address}>')
        connection_socket.shutdown(1)
        connection_socket.close()
        print(f'<Closed connection with {connection_address}>')


# clients wait for the server and receives its package
class Client:
    """Classe do cliente que conecta-se com o servidor para receber o pacote (commit_i, R_i ou s_i) do signatário
    atuando como servidor"""
    def __init__(self, target_address):
        self.continue_permission = False
        self.target_address = target_address
        self.connection_socket = None
        self.package = None
        self.run()

    def run(self):
        """Executa a rotina do cliente. Realiza a configuração da conexão, envia o pedido pelo pacote do servidor,
        recebe o pacote do servidor, envia sua confirmação de recebimento e espera pela permissão para prosseguir"""
        self.connection_setup()
        self.send_request()
        self.package = self.receive_pckg()
        self.send_ok()
        self.receive_continue()

    def connection_setup(self):
        """Realiza a conexão com o co-signatário atuando como servidor"""
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        i = 0
        while i < RETRY_MAX:
            i += 1
            try:
                print(f'<Trying to connect to {self.target_address}>')
                self.connection_socket.connect(self.target_address)
            except Exception as e:
                print(f'<Caught connection exception: {e}>')
                time.sleep(1)
                continue
            break

    def send_request(self):
        """Envia o pedido pelo pacote do co-signatário atuando como servidor"""
        print(f'<Sending {SEND_FLAG} to {self.target_address}>')
        send_package(self.connection_socket, SEND_FLAG)

    def receive_pckg(self):
        """Recebe o pacote do co-signatário atuando como servidor"""
        print(f'<Waiting for package from: {self.target_address}>')
        package = receive_package(self.connection_socket)
        print(f'<Received \"{package}\" from {self.target_address}>')
        return package

    def send_ok(self):
        """Envia a confirmação de recebimento para o co-signatário atuando como servidor"""
        print(f'<Sending {OK_FLAG} to {self.target_address}>')
        send_package(self.connection_socket, OK_FLAG)

    def receive_continue(self):
        """Recebe do co-signatário atuando como servidor, a permissão de continuar a sua execução"""
        print(f'<Waiting for permission to continue from: {self.target_address}>')
        ok = receive_package(self.connection_socket)
        print(f'<Received {ok} from {self.target_address}>')
        if ok == CONTINUE_FLAG:
            return True
        else:
            return False


def p2p_get(my_addr, peer_list, package):
    """Executa os clientes e servidores baseados na ordem de peer_list. Utilizando peer_list como uma fila, se o
    endereço da ponta da fila e o endereço my_addr do signatário são os mesmos, então o signatário deve atuar como
    servidor, caso contrário ele atua como cliente"""
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
            # act as server -> sends his package to clients upon request
            peer_queue.pop(0)
            print(f'** {my_addr} acting as a server **')
            server = Server(peer_list, package, my_addr)
            # keep the order of the received objects
            rcv_list.append(package)

        else:
            # act as client -> receives package from server upon request
            print(f'** {my_addr} acting as a client **')
            client = Client(peer_queue.pop(0))
            rcv_list.append(client.package)

    # print(f'AFTER PEER LIST = {peer_list}')

    return rcv_list


def receive_package(sock):
    """Recebe um pacote através do socket (sock) e o decodifica"""
    print("<<RECEIVE>>\n")
    # fragments = []
    # while True:  # while not done
    #     chunk = sock.recv(PCKG_SIZE)
    #     print(f'<<CHUNK: {chunk}>>')
    #     if not chunk.decode('utf-8'):
    #         break
    #     fragments.append(chunk)
    #
    # return ''.join(fragments)
    return sock.recv(PCKG_SIZE).decode('utf-8')


def send_package(sock, package):
    """Envia o pacote (package) codificado para o socket (sock)"""
    print("<<SEND>>\n")
    # try:
    #     sock.sendall(package)
    # except Exception as e:
    #     print(f'Caught exception: {e}')
    #     print(f'Exiting...')
    #     sys.exit(0)
    sock.sendall(package.encode('utf-8'))

# -*- encoding=utf-8 -*-


import threading
import socket
import time

from server.socket_server import TCPServer
from handler.base_handler import StreamRequestHandler


class TestBaseRequestHandler(StreamRequestHandler):

    # 具体处理的逻辑
    def handle(self):
        msg = self.readline()
        print('Server recv msg: '+msg)
        time.sleep(1)
        self.write_content(msg)
        self.send()


# 测试SocketServer
class SocketServerTest:

    def run_server(self):
        tcp_server = TCPServer(('127.0.0.1', 8888), TestBaseRequestHandler)
        tcp_server.serve_forever()

    def client_connect(self):
        client = socket.socket()
        client.connect(('127.0.0.1', 8888))
        client.send(b'hello tcpserver\r\n')
        msg = client.recv(1024)
        print('client '+msg.decode())

    def gen_clients(self, num):
        clients = []
        for i in range(num):
            client_thread = threading.Thread(target=self.client_connect)
            clients.append(client_thread)
        return clients

    def run(self):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()

        clients = self.gen_clients(10)
        for client in clients:
            client.start()

        server_thread.join()
        for client in clients:
            client.join()


if __name__ == '__main__':
    SocketServerTest().run()


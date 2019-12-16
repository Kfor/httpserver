# -*- encoding=utf-8 -*-
import socket
import threading


class TCPServer:

    def __init__(self, server_address, handler_class):
        self.server_address = server_address
        self.HandlerClass = handler_class  # 用来处理请求的类
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_shutdown = False

    # 服务器的启动函数
    def serve_forever(self):
        self.socket.bind(self.server_address)
        self.socket.listen(10)
        while not self.is_shutdown:
            # 1. 接受请求
            request, client_address = self.get_request()
            # 2. 处理请求
            try:
                self.process_request_multi(request, client_address)
            except Exception as e:
                print(e)

    # 接受请求
    def get_request(self):
        return self.socket.accept()

    # 处理请求
    def process_request(self, request, client_address):
        handler = self.HandlerClass(self, request, client_address)
        handler.handle()
        handler.close()  # 在并发的执行时，需要在每一个执行之后关闭，而不能等待处理结束之后执行（会导致套接字提前关闭）

    # 多线程处理
    def process_request_multi(self, request, client_address):
        t = threading.Thread(target=self.process_request, args=(request, client_address))
        t.start()

    # 关闭服务器
    def close_request(self, request):
        request.shutdown(socket.SHUT_WR)
        request.close()

    def shutdown(self):
        self.is_shutdown = True

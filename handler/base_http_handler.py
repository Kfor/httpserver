# -*- encoding=utf-8 -*-


import logging

from handler.base_handler import StreamRequestHandler

logging.basicConfig(level=logging.DEBUG)


class BaseHTTPRequestHandler(StreamRequestHandler):

    def __init__(self, server, request, client_address):
        self.method = None
        self.path = None
        self.version = None
        self.headers = None
        self.body = None
        StreamRequestHandler.__init__(self, server, request, client_address)

    # 请求的处理
    def handle(self):
        try:
            # 1. 解析请求
            if not self.parse_request():
                return
            # 2. 方法执行
            method_name = "do_" + self.method
            if not hasattr(self, method_name):  # 检测是否存在
                # TODO 发送错误
                return
            method = getattr(self, method_name)
            method()  # 应答报文的封装
            self.send()  # 发送结果
        except Exception as e:
            logging.exception(e)

    # 请求的解析
    def parse_request(self):
        # 解析请求行
        first_line = self.readline()
        words = first_line.split()
        # 请求方法，请求的地址，请求的HTTP版本
        self.method, self.path, self.version = words
        # 解析请求头
        self.headers = self.parse_headers()
        # 解析请求内容
        key = "Content-Length"
        if key in self.headers.key():
            # 请求内容的长度
            body_length = int(self.headers[key])
            self.body = self.read(body_length)
        return True

    def parse_headers(self):
        headers = {}
        while True:
            line = self.readline()
            # 如果是空行的话，就是结束了
            if line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                headers[key] = value
            else:
                break
        return headers

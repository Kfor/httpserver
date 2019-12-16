# -*- encoding=utf-8 -*-


import logging

from handler.base_handler import StreamRequestHandler
from util import date_time_string

logging.basicConfig(level=logging.DEBUG)


class BaseHTTPRequestHandler(StreamRequestHandler):

    def __init__(self, server, request, client_address):
        self.method = None
        self.path = None
        self.version = None
        self.headers = None
        self.request_line = None
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
                self.write_error(404, 'wtf')
                self.send()
                return
            method = getattr(self, method_name)
            method()  # 应答报文的封装
            self.send()  # 发送结果
        except Exception as e:
            logging.exception(e)

    def do_GET(self):
        msg = '<h1>hello world</h1>'
        self.write_response(200, 'Sucess')
        self.write_header('Content-Length', len(msg))
        self.end_header()
        self.write_content(msg)
        self.send()

    # 请求的解析
    def parse_request(self):
        # 解析请求行
        first_line = self.readline()
        self.request_line = first_line
        words = first_line.split()
        print('words', words)
        # 请求方法，请求的地址，请求的HTTP版本
        self.method, self.path, self.version = words
        # 解析请求头
        self.headers = self.parse_headers()
        # 解析请求内容
        key = "Content-Length"
        if key in self.headers.keys():
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

    # 写入应答头
    def write_header(self, key, value):
        msg = '%s: %s\r\n' % (key, value)
        self.write_content(msg)
        pass

    default_http_version = 'HTTP/1.1'

    # 写入响应
    def write_response(self, code, msg=None):
        logging.info('%s, code: %s.' % (self.request_line, code))
        if msg is None:
            msg = self.responses[code][0]
        # 状态行
        response_line = "%s %d %s\r\n" % (self.default_http_version, code, msg)
        self.write_content(response_line)
        # 应答头
        self.write_header('Server', '%s: %s' % (self.server.server_name, self.server.server_version))
        self.write_header('Date', date_time_string())

    DEFAULT_ERROR_TEMPLATE = r'''
    <head><title>Error response</title></head><body><h1>Error</h1>
    <p>Error code: %(code)d.</p><p>Message: %(message)s.</p><p>explanation: %(explain)s</p>
    </body>
    '''

    responses = {
        100: ('Continue', 'Request received, please continue'),
        101: ('Switching Protocols',
              'Switching to new protocol; obey Upgrade header'),

        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted',
              'Request accepted, processing continues off-line'),
        203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
        204: ('No Content', 'Request fulfilled, nothing follows'),
        205: ('Reset Content', 'Clear input form for further input.'),
        206: ('Partial Content', 'Partial content follows.'),

        300: ('Multiple Choices',
              'Object has several resources -- see URI list'),
        301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('See Other', 'Object moved -- see Method and URL list'),
        304: ('Not Modified',
              'Document has not changed since given time'),
        305: ('Use Proxy',
              'You must use proxy specified in Location to access this '
              'resource.'),
        307: ('Temporary Redirect',
              'Object moved temporarily -- see URI list'),

        400: ('Bad Request',
              'Bad request syntax or unsupported method'),
        401: ('Unauthorized',
              'No permission -- see authorization schemes'),
        402: ('Payment Required',
              'No payment -- see charging schemes'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
              'Specified method is invalid for this resource.'),
        406: ('Not Acceptable', 'URI not available in preferred format.'),
        407: ('Proxy Authentication Required', 'You must authenticate with '
                                               'this proxy before proceeding.'),
        408: ('Request Timeout', 'Request timed out; try again later.'),
        409: ('Conflict', 'Request conflict.'),
        410: ('Gone',
              'URI no longer exists and has been permanently removed.'),
        411: ('Length Required', 'Client must specify Content-Length.'),
        412: ('Precondition Failed', 'Precondition in headers is false.'),
        413: ('Request Entity Too Large', 'Entity is too large.'),
        414: ('Request-URI Too Long', 'URI is too long.'),
        415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
        416: ('Requested Range Not Satisfiable',
              'Cannot satisfy request range.'),
        417: ('Expectation Failed',
              'Expect condition could not be satisfied.'),

        500: ('Internal Server Error', 'Server got itself in trouble'),
        501: ('Not Implemented',
              'Server does not support this operation'),
        502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
        503: ('Service Unavailable',
              'The server cannot process the request due to a high load'),
        504: ('Gateway Timeout',
              'The gateway server did not receive a timely response'),
        505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
    }

    # 写入错误请求的结果
    def write_error(self, code, msg=None):
        s_msg, l_msg = self.responses[code]
        if msg:
            s_msg = msg
        response_content = self.DEFAULT_ERROR_TEMPLATE % {
            'code': code,
            'message': s_msg,
            'explain': l_msg
        }
        self.write_response(code, msg)
        # 请求头-应答内容之间的 空行
        self.end_header()
        self.write_content(response_content)

    def end_header(self):
        self.write_content('\r\n')

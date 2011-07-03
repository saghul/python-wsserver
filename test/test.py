# coding=utf8

# Copyright (C) 2011 Saúl Ibarra Corretgé <saghul@gmail.com>
#

import sys
sys.path.insert(0, '..')

from optparse import OptionParser
from wsserver import WebSocketServer, WSClientSocket


class MyWSClientSocket(WSClientSocket):

    def message_received(self, data):
        print '-- Received data: %s' % data
        self.queue_send(data)


class MyWebSocketServer(WebSocketServer):
    client_cls = MyWSClientSocket
    handler = '/test'


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--use-ssl', action='store_true', dest='use_ssl', default=False)
    options, args = parser.parse_args()

    if options.use_ssl:
        ws_server = MyWebSocketServer(9999, use_ssl=True, cert='cert.pem', key='key.pem')
    else:
        ws_server = MyWebSocketServer(9999)
    print 'Starting WebSocketServer... SSL is %s' % ('enabled' if options.use_ssl else 'disabled')
    ws_server.start()

    while True:
        c = raw_input('> ')
        if c == 'quit':
            break
        if c:
            ws_server.send_all(c)
    print 'Stopping WebSocketServer...'
    ws_server.stop()
    print 'WebSocketServer stopped'


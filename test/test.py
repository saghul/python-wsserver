# coding=utf8

# Copyright (C) 2011 Saúl Ibarra Corretgé <saghul@gmail.com>
#

import sys
sys.path.insert(0, '..')

from wsserver import WebSocketServer


if __name__ == '__main__':
    ws_server = WebSocketServer(9999, handler='/test')
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


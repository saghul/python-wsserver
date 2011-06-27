# coding=utf8

# Copyright (C) 2011 Saúl Ibarra Corretgé <saghul@gmail.com>
#

# Modified from original in: http://mumrah.posterous.com/websockets-in-python

__version__ = '0.0.1'

import select
import struct
import socket
import hashlib
import os
import re
import Queue

from threading import Event, Thread


READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
READ_WRITE = READ_ONLY | select.POLLOUT


class WSServerSocket(object):
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setblocking(0)

    def bind(self):
        self._socket.bind((self._ip, self._port))
        self._socket.listen(5)

    def accept(self):
        return self._socket.accept()

    def fileno(self):
        return self._socket.fileno()

    def close(self):
        self._socket.close()


class WSClientSocket(object):
    _digit_re = re.compile(r'[^0-9]')
    _spaces_re = re.compile(r'\s')
    _req_line_re = re.compile('^GET (?P<handler>.*) .*\\r\\n')
    _handshake = (
        "HTTP/1.1 101 Web Socket Protocol Handshake\r\n"
        "Upgrade: WebSocket\r\n"
        "Connection: Upgrade\r\n"
        "WebSocket-Origin: %(origin)s\r\n"
        "WebSocket-Location: ws://%(address)s:%(port)s%(handler)s\r\n"
        "Sec-Websocket-Origin: %(origin)s\r\n"
        "Sec-Websocket-Location: ws://%(address)s:%(port)s%(handler)s\r\n"
        "\r\n"
    )
    def __init__(self, sock, handler):
        self._socket = sock
        self._socket.setblocking(0)
        self.handler = handler
        self.handshaken = False
        self.write_queue = Queue.Queue()
        self.headers = ''
        self.data = ''

    def send(self, data):
        self._socket.send(data)

    def recv(self, bufsize):
        return self._socket.recv(bufsize)

    def fileno(self):
        return self._socket.fileno()

    def close(self):
        self._socket.close()

    def _queue_send(self, data):
        try:
            self.write_queue.put_nowait(data)
        except Queue.Full:
            pass

    def queue_send(self, data):
        self._queue_send('\x00%s\xff' % data)

    def data_received(self, data):
        if not self.handshaken:
            if data.startswith('GET'):
                match = self._req_line_re.match(data)
                if not (match and match.groupdict()['handler'] == self.handler):
                    self.close()
                    return
            self.headers += data
            if self.headers.find('\r\n\r\n') != -1:
                parts = self.headers.split('\r\n\r\n', 1)
                self.headers = parts[0]
                if self.do_handshake(self.headers, parts[1]):
                    self.handshaken = True
        else:
            self.data += data
            msgs = self.data.split('\xff')
            self.data = msgs.pop()
            for msg in msgs:
                if msg[0] == '\x00':
                    self.message_received(msg[1:])

    def do_handshake(self, header, key=None):
        part_1 = part_2 = origin = None
        for line in header.split('\r\n')[1:]:
            name, value = line.split(': ', 1)
            if name.lower() == "sec-websocket-key1":
                key_number_1 = int(self._digit_re.sub('', value))
                spaces_1 = len(self._spaces_re.findall(value))
                if spaces_1 == 0:
                    return False
                if key_number_1 % spaces_1 != 0:
                    return False
                part_1 = key_number_1 / spaces_1
            elif name.lower() == "sec-websocket-key2":
                key_number_2 = int(self._digit_re.sub('', value))
                spaces_2 = len(self._spaces_re.findall(value))
                if spaces_2 == 0:
                    return False
                if key_number_2 % spaces_2 != 0:
                    return False
                part_2 = key_number_2 / spaces_2
            elif name.lower() == "host":
                host, _ = value.split(':', 1)
            elif name.lower() == "origin":
                origin = value
        server_ip, server_port = self._socket.getsockname()
        if part_1 and part_2:
            challenge = struct.pack('!I', part_1) + struct.pack('!I', part_2) + key
            response = hashlib.md5(challenge).digest()
            handshake = self._handshake % {
                'origin': origin,
                'address': host,
                'port': server_port,
                'handler': self.handler
            }
            handshake += response
        else:
            # Not using challenge-response
            handshake = self._handshake % {
                'origin': origin,
                'address': host,
                'port': server_port,
                'handler': self.handler
            }
        self._queue_send(handshake)    # Note the _ !
        return True

    def message_received(self, data):
        print 'Message received: ',data


class WebSocketServer(Thread):

    def __init__(self, port, address='', handler='/'):
        self.server = WSServerSocket(address, port)
        self.fd_map = { self.server.fileno(): self.server }
        self.handler = handler
        self._poller = select.poll()
        self._poller.register(self.server, READ_ONLY)
        self._pipe = os.pipe()
        self._poller.register(self._pipe[0], select.POLLIN)
        self._stop_event = Event()
        Thread.__init__(self)
        self.daemon = True

    def start(self):
        self.server.bind()
        Thread.start(self)

    def run(self):
        while not self._stop_event.is_set():
            events = self._poller.poll()
            for fd, flag in events:
                if fd == self._pipe[0]:
                    # Stop requested
                    for client in (client for client in self.fd_map.values() if client is not self.server):
                        self._poller.unregister(client)
                        client.close()
                    self.fd_map = {}
                    break
                socket = self.fd_map[fd]
                if flag & (select.POLLIN | select.POLLPRI):
                    # Ready to read
                    if socket is self.server:
                        sock, addr = socket.accept()
                        client = WSClientSocket(sock, self.handler)
                        self.fd_map[client.fileno()] = client
                        self._poller.register(client, READ_WRITE)
                    else:
                        data = socket.recv(1024)
                        if data:
                            socket.data_received(data)
                        else:
                            self.fd_map.pop(fd)
                            self._poller.unregister(socket)
                            socket.close()
                elif flag & select.POLLHUP:
                    # Client hung up
                    self.fd_map.pop(fd)
                    self._poller.unregister(socket)
                    socket.close()
                elif flag & select.POLLOUT:
                    # Ready to send
                    try:
                        data = socket.write_queue.get_nowait()
                    except Queue.Empty:
                        pass
                    else:
                        socket.send(data)
                elif flag & select.POLLERR:
                    # Error
                    self.fd_map.pop(fd)
                    self._poller.unregister(socket)
                    socket.close()

    def stop(self):
        self._stop_event.set()
        os.write(self._pipe[1], 'stop')
        Thread.join(self)
        self._poller.unregister(self._pipe[0])
        os.close(self._pipe[0])
        os.close(self._pipe[1])
        self._poller.unregister(self.server)
        self.server.close()

    def send_all(self, msg):
        [client.queue_send(msg) for client in (client for client in self.fd_map.values() if client is not self.server)]



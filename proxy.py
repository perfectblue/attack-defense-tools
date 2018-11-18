#!/usr/bin/env python2

# Hacky firewall proxy that forwards a port while intercepting bidirectional traffic
# To be used in place of an iptables NAT chain rule, etc.
# - team@perfect.blue

import traceback
import socket
import threading
import struct, time,sys, traceback, errno, datetime
import BaseHTTPServer
import base64

def thread(target, args):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()
    return t

def forward(from_sock, to_sock):
    buf = '_'
    while buf:
        buf = from_sock.recv(1024)
        print buf
        to_sock.send(buf)

def handle_client(from_sock, fromaddr, remote_host, remote_port, i):
    from_addr, port = fromaddr
    print 'New connection from %s:%s' % (from_addr, port)
    to_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    to_sock.connect((remote_host, remote_port))
    thread(target=forward, args=(from_sock, to_sock))
    thread(target=forward, args=(to_sock, from_sock))

def serve(local_host, local_port, remote_host, remote_port):
    bindsocket = socket.socket()
    bindsocket.bind((local_host, local_port))
    bindsocket.listen(5)
    print 'Forwarding [%s:%d] <-> [%s:%d] ...' % (local_host, local_port, remote_host, remote_port)
    i = 0
    try:
        while True:
            newsocket, fromaddr = bindsocket.accept()
            newsocket.settimeout(60.0)
            thread(target=handle_client, args=(newsocket, fromaddr, remote_host, remote_port, i))
            i += 1
    except KeyboardInterrupt:
        bindsocket.shutdown(socket.SHUT_RDWR)
        bindsocket.close()

def start():
    thread(target=serve, args=('127.0.0.1', 8000, 'irc.freenode.net', 6667))

start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    time.sleep(1)

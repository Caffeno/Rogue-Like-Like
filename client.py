#!/usr/bin/env python3

import types
import socket
import selectors
from keytracker import KBHit
import os

sel = selectors.DefaultSelector()

def start_con(HOST, PORT):
    server_address = (HOST, PORT)
    print('starting connection to ', server_address)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_address)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(recv=b"", send=b"", serverresponse="", connected=False)
    sel.register(sock, events, data=data)

def srvc_con(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        data.recv = sock.recv(1024)
        if data.recv == b"end":
            sel.unregister(sock)
            sock.close()
        else:
            serverresponse = data.recv.decode('ascii')
            os.system('clear')
            print(serverresponse)
            data.recv = b''
    if mask & selectors.EVENT_WRITE:
        if data.send:
            sent = sock.send(data.send)
            data.send = data.send[sent:]
            if not data.connected:
                data.connected = True


#TODO: Fix server crash on client disconect
KB = KBHit()
start_con('127.0.0.1', 11111)
name = ""
done = False
while not done:
    char = KB.check_input()
    if char and ord(char) != 10:
        name += char
        print(char, end='', flush=True)
        
    events = sel.select(timeout=0)
    for key, mask in events:
        if char and ord(char) == 10:
            key.data.send = name.encode('ascii')
        srvc_con(key, mask)
        if key.data.connected:
            done = True
   

while True:
    events = sel.select(timeout=0)
    for key, mask in events:
        action = KB.check_input()
        if action:
            key.data.send = action.encode('ascii')
        srvc_con(key, mask)

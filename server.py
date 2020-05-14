#!/usr/bin/env python3

import socket
import selectors
import time
import types
from world import World
sel = selectors.DefaultSelector()

HOST = '127.0.0.1'
PORT = 11111

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()
print('listening on ', (HOST, PORT))
sock.setblocking(False)

sel.register(sock, selectors.EVENT_READ, data=None)

def acc_wrapper(sock):
    userconnection, useraddress = sock.accept()
    userconnection.setblocking(False)
    print('accepting connection from ', useraddress)
    data = types.SimpleNamespace(useraddress=useraddress, binin=b"", binout=b"What is your name?\n", player_id="", last_send=time.time(), action="", connected=False)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(userconnection, events, data=data)

def srvc_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if not data.player_id:
        if mask & selectors.EVENT_READ:
            receive_data = sock.recv(1024)
            if receive_data != b'\xff\xf4\xff\xfd\x06' or receive_data != b'exit\n\r':
                data.player_id = receive_data.replace(b"\n", b"").replace(b"\r", b"").decode('ascii')
            else:
                sel.unregister(sock)
                sock.close()
                
    else:
        if mask & selectors.EVENT_READ:
            receive_data = sock.recv(1024)
            print(receive_data)
            if receive_data != b'\xff\xf4\xff\xfd\x06' and receive_data != b'exit\n\r':
                data.binin = receive_data.replace(b"\n", b"").replace(b"\r", b"")
                data.action = data.binin.decode('ascii')
                print(data.action)
            else:
                sel.unregister(sock)
                sock.close()
                
    if mask & selectors.EVENT_WRITE:
        if data.binout:
            print('Echoing, ', repr(data.binout), ' to ', data.useraddress)
            sent = sock.send(data.binout)
            data.binout = data.binout[sent:]

W = World()
lasttick = time.time()
while True:
    now = time.time()
    if now - lasttick >= 0.05:
        print('tick')
        W.tick(now)
        lasttick = now
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            acc_wrapper(key.fileobj)
        else:
            if now - key.data.last_send > 0.05 and key.data.player_id:
                key.data.binout = W.getmaptosend(key.data.player_id)
                key.data.last_send = now
            srvc_connection(key, mask)
            if key.data.action:
                print('Setting action to {}'.format(key.data.action))
                W.setplayeraction(key.data.player_id, key.data.action)
                key.data.action = ""
            if not key.data.connected and key.data.player_id:
                W.addplayer(key.data.player_id)
                key.data.connected = True




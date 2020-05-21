#!/usr/bin/env python3

import socket
import selectors
import time
import types
from world import World
import json
import zlib

sel = selectors.DefaultSelector()

HOST = '127.0.0.1'
PORT = 33333

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
    data = types.SimpleNamespace(useraddress=useraddress, namerequested=False, binin=b"", binout=b"", player_id="", last_send=time.time(), action="", connected=False)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(userconnection, events, data=data)

def srvc_connection(key, mask):
    #Seperate into a send and receive Methods
    sock = key.fileobj
    data = key.data
    if not data.player_id:
        if mask & selectors.EVENT_READ:
            try:
                receive_data = sock.recv(1024)
            except:
                sel.unregister(sock)
                sock.close()
                return
            if receive_data != b'\xff\xf4\xff\xfd\x06' or receive_data != b'exit\n\r':
                data.player_id = receive_data.replace(b"\n", b"").replace(b"\r", b"").decode('utf-8')
            else:
                sel.unregister(sock)
                sock.close()
                return
                
    else:
        if mask & selectors.EVENT_READ:
            try:
                receive_data = sock.recv(1024)
            except:
                sel.unregister(sock)
                sock.close()
                return
            if receive_data != b'\xff\xf4\xff\xfd\x06' and receive_data != b'exit\n\r':
                data.binin = receive_data.replace(b"\n", b"").replace(b"\r", b"")
                data.action = data.binin.decode('utf-8')
            else:
                sel.unregister(sock)
                sock.close()
                return
                
    if mask & selectors.EVENT_WRITE:
        if data.binout:
            print('Echoing, ', repr(data.binout), ' to ', data.useraddress)
            sent = sock.send(data.binout)
            data.binout = b''

W = World()
lasttick = time.time()
update = ""

while True:
    now = time.time()
    if now - lasttick >= 0.05:
        print('tick')
        W.tick(now)
        lasttick = now
        update = W.bundlegroupdata()
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            acc_wrapper(key.fileobj)
        else:
            #Clean this loop up so its easier to follow and make changes to
            if not key.data.namerequested:
                data = 'What is your name?'
                jsondata = json.dumps(data)
                compresseddata = zlib.compress(jsondata.encode('utf-8'))
                key.data.binout = compresseddata
                key.data.namerequested = True
            if key.data.connected and update:
                print(update)
                rawplayerdata = W.bundleevents(update, key.data.player_id) 
                jsonpdata = json.dumps(rawplayerdata)
                compressedpdata = zlib.compress(jsonpdata.encode('utf-8'))
                key.data.binout = compressedpdata
            srvc_connection(key, mask)
            if key.data.action:
                print('Setting action to {}'.format(key.data.action))
                W.setplayeraction(key.data.player_id, key.data.action)
                key.data.action = ""
            if not key.data.connected and key.data.player_id:
                W.addplayer(key.data.player_id)
                key.data.connected = True
    update = ""




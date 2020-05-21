#!/usr/bin/env python3

import time
import types
import socket
import selectors
from keytracker import KBHit
import os
from world import World
from entityclasses import Player
import sys
import json
import zlib

class Client:
    def __init__(self, HOST, PORT):
        self.sel = selectors.DefaultSelector()
        self.start_con(HOST, PORT)
        self.eventlog = []
        self.player = Player(None, None , [None, None, None], None)
        self.display = []
        for x in range(20):
            self.display.append('')

    def start_con(self, HOST, PORT):
        server_address = (HOST, PORT)
        print('starting connection to ', server_address)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_address)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(recv=b"", send=b"", textneeded=True, player_id="", connected=False, message="")
        self.sel.register(sock, events, data=data)
    
    def srvc_con(self, key, mask):
        #This is more like what the server should be like
        #Could still be seperated into send and receive methods
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            data.recv = sock.recv(1024)
            if data.recv == b"end":
                sel.unregister(sock)
                sock.close()
                return
        if mask & selectors.EVENT_WRITE:
            if data.send:
                sent = sock.send(data.send)
                data.send = data.send[sent:]
                #move this so there can be a check from the server if the client is connected
                if not data.connected:
                    data.connected = True

    #I'm going to make the response from the server always be in the form of a compressed json dict
    #I will check to see if a corrisponding dict key is is there and process that data accordingly
    def parseResponse(self, serverresponse, world, key):
        jsondata = zlib.decompress(serverresponse)
        data = json.loads(jsondata)
        if type(data) == dict:
            world.clupdateplayers(data['players'])
            #world.clupdatemonsters(resp[1])
            #world.clupdateloot(resp[2])
            if 'events' in data.keys():
                self.updateevents(data['events'])
        else:
            print(data)
            
    def updateevents(self, events):
        for x in range(len(events)):
            self.eventlog.insert(0, events[x])
        if len(self.eventlog) > 6:
            self.eventlog = self.eventlog[:6]
        
    #Make this "updatedisplay()" handle showing client text input, and client action prompt
    def printmap(self, region, MP):
        for x in range(21):
            sys.stdout.write("\033[F") #back to previous line
        for x in range(20 - len(region)):
            region.append("")
        events = self.prepevents()
        for x in range(20 - len(events)):
            events.append("")
        for x in range(20 - len(MP)):
            MP.append("")
        for x in range(20):
            line = region[x] + MP[x] + events[x]
            sys.stdout.write("\033[K") #back to previous line
            print(line)
            self.display[x] = line
        
    def entertext(self, text, char, key):            
        if char:
            charlen = len(char)
            if charlen == 1 and ord(char) != 10 and char != ',' and char != ';' and char != ':' and ord(char) != 127:
                text += char
                print(char, end='', flush=True)
            elif charlen == 1 and ord(char) == 127:
                print('\r', end='', flush=True)
                sys.stdout.write("\033[K") #clear line 
                text = text[:len(text) - 1]
                print(text, end='', flush=True)
            elif charlen == 1 and ord(char) == 10 and text:
                key.data.send = text.encode('utf-8')
                W.addplayer(text)
                #why is this in more than one spot? remove so check can be seperate
                key.data.connected = True
                key.data.textneeded = False
                key.data.player_id = text
                text = ""
        return text

    #good
    def prepevents(self):
        events = []
        events.append('')
        events.append('')
        events.append('  Events:')
        for e in self.eventlog:
            events.append('    -' + e)
        return events


#TODO: Fix server crash on client disconect
KB = KBHit()
client = Client('127.0.0.1', 33333)
text = ""
W = World()
os.system('clear')
lastdraw = time.time()
while True:
    now = time.time()
    events = client.sel.select(timeout=0)
    for key, mask in events:
        char = KB.check_input()
        if key.data.textneeded:
            text = client.entertext(text, char, key)
        elif char and len(char) > 1:
            key.data.send = char.encode('utf-8')
        elif char and len(char) == 1 and ord(char) == 10:
            key.data.textneeded = True

        client.srvc_con(key, mask)
           
        if key.data.recv != b'':
            client.parseResponse(key.data.recv, W, key)
            key.data.recv = b""
        if key.data.connected and now - lastdraw >= 0.05:
            MP = W.getmaptodraw(key.data.player_id)
            statregion = W.getstatregion(key.data.player_id)
            client.printmap(statregion, MP)
            lastdraw = now

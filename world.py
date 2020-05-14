#!/usr/bin/env python3

from entityclasses import Entity, Mob, Player
import random
import yaml
from pprint import pprint

class World:
    def __init__(self):
        self.activemaps = []
        #TODO: make event queue by player self.events = []
        self.loadmaps()
        self.players = {}   

    def loadmaps(self):
        f = open('data/smallermaps.yaml', 'r')
        dirtymaps = yaml.load(f, Loader=yaml.FullLoader)['Maps']
        pprint(dirtymaps)
        f.close()
        self.maps = {}
        self.mapplayercounts = {}
        self.playersbymap = {}
        for M in dirtymaps:
            print(M)
            pprint(dirtymaps[M])
            brokenmap = dirtymaps[M].splitlines()
            pprint(brokenmap)
            self.playersbymap[M] = []
            arraymap = []
            for line in brokenmap:
                arr = []
                for char in range(len(line)):
                    arr.append(line[char])
                arraymap.append(arr)
            for line in arraymap:
                print(line)
            print('arrmap')
            pprint(arraymap)
            self.maps[M] = arraymap
            self.mapplayercounts[M] = 0
            print(M)
            print(self.mapplayercounts)
        self.mapsize = (len(self.maps[M][0]), len(self.maps[M]))
        pprint(self.maps)

    def addplayer(self, player_id):
        startscreen = (random.randint(1, 2), random.randint(1, 2))
        Mname = 'map{},{}'.format(startscreen[0], startscreen[1])
        if startscreen[0] == 1:
            startx = 1
        else:
            startx = self.mapsize[0] - 2
        if startscreen[1] == 1:
            starty = 1
        else:
            starty = self.mapsize[1] - 2
        self.players[player_id] = Player(5, 4, [Mname, startx, starty], player_id)
        self.mapplayercounts[Mname] += 1
        if self.mapplayercounts[Mname] == 1:
            self.activemaps.append(Mname)
        self.playersbymap[Mname].append(player_id)
        #self.events.append('Player {} has connected'.format(player_id))
        
    def playeractions(self, now):
        if self.players:
            for M in self.activemaps:
                for P in self.playersbymap[M]:
                    with self.players[P] as player:
                        if player.ready(now):
                            action = player.getaction()
                            if action != '':
                                vector = self.DtoV(action)
                                playerlocation = player.getlocation()
                                xaftermove = playerlocation[1] + vector[0]
                                yaftermove = playerlocation[2] + vector[1]
                                if self.mapsize[0] <= xaftermove or xaftermove < 0 or yaftermove < 0 or self.mapsize[1] <= yaftermove:
                                    self.changescreens(P, vector, now)
                                elif int(self.maps[M][yaftermove][xaftermove]) <= 0:
                                    player.move(vector, now)
                                    player.action = ""
                                    newlocation = player.getlocation()
                                        
                                    #TODO: Handle attacking and picking things up and map transitions (probably going to be funtion calls)

    def changescreens(self, player_id, vector, now): 
        with self.players[player_id] as player:
            player.move(vector, now)
            player.action = ""
            location = player.getlocation()
            oldmap = location[0]
            self.mapplayercounts[oldmap] -= 1
            if self.mapplayercounts[oldmap] == 0:
                self.playersbymap[oldmap].remove(player_id)

            mapposition = oldmap[3:].split(',')
            for i in range(len(mapposition)):
                mapposition[i] = int(mapposition[i]) + vector[i]
            newmap = 'map{},{}'.format(mapposition[0], mapposition[1])
            player.chscreen(self.mapsize, newmap)
            self.mapplayercounts[newmap] += 1
            self.playersbymap[newmap].append(player_id)
            if self.mapplayercounts[newmap] == 1:
                self.activemaps.append(newmap)
            
            
                                
    def getmaptosend(self, player_id):
        #TODO: go through list of entities and apply to squares
        if player_id not in self.players.keys():
            return ''
        player = self.players[player_id]
        pprint(self.players)
        playerlocation = player.getlocation()
        Mname = playerlocation[0]
        print('get map {}'.format(Mname))
        
        MP = self.maps[Mname]
        pprint(MP)
        MPcopy = []
        for line in MP:
            MPcopy.append(list(line))
        pprint(MPcopy)
        for P in self.playersbymap[Mname]:
            if P == player_id:
                char = '@'
            else:
                char = 'P'
            playerentity = self.players[P]
            entlocation = playerentity.getlocation()
            print(entlocation)
            MPcopy[entlocation[2]][entlocation[1]] = char
        #TODO: check for other entities to add to the map
        mapstring = '\n'
        for j in range(len(MPcopy)):
            mapline = ''
            for i in range(len(MPcopy[0])):
                nextchar = MPcopy[j][i]
                if nextchar == '0':
                    mapline += '_'
                elif nextchar == '1':
                    mapline += '#'
                else: 
                    mapline += nextchar
                print(i, j)
            mapline += '\n'
            print(mapline)
            mapstring += mapline
        encodedmap = mapstring.encode('ascii')
        return encodedmap
   
                    
    def setplayeraction(self, player_id, action):
        print('setting {} action to {}'.format(player_id, action))
        with self.players[player_id] as player:
            player.setaction(action)

    def tick(self, now):
        self.playeractions(now)
                
    def DtoV(self, direction):
        if direction == 'up':
            return (0, -1)
        elif direction == 'down':
            return (0, 1)
        elif direction == 'right':
            return (1, 0)
        elif direction == 'left':
            return (-1, 0)
        else:
            return None


if __name__ == "__main__":
    W = World()    

#!/usr/bin/env python3

from entityclasses import Entity, Mob, Player
import random
import yaml
from pprint import pprint
from maps import Map

class World:

    def __init__(self):
        self.activemaps = []
        #TODO: make event queue by player self.events = []
        self.loadmaps()
        self.players = {}
        self.directionkey = {}
       
        self.directionkey['up'] = 0
        self.directionkey['down'] = 1
        self.directionkey['right'] = 2
        self.directionkey['left'] = 3

    def loadmaps(self):
        f = open('data/justrightmaps.yaml', 'r')
        dirtymaps = yaml.load(f, Loader=yaml.FullLoader)['Maps']
        pprint(dirtymaps)
        f.close()
        self.maps = {}
        for M in dirtymaps:
            MP = Map(M, dirtymaps[M])
            self.maps[M] = MP

    def addplayer(self, player_id):
        M = 'North-West_Shore'
        self.players[player_id] = Player(5, 4, [M, 1, 1], player_id)
        with self.maps[M] as MP:
            activate = MP.addplayer(player_id)
            if activate:
                self.activemaps.append(M)
        for P in self.players:
            with self.players[P] as player:
                player.addevent('Player {} has connected'.format(player_id))
        
    def playeractions(self, now):
        if self.players: #if not so its less indented
            for M in self.activemaps:
                #map specific action function(M)
                grid = self.populatemap(M) #add a map key to return {'2': ('p', player_id) '3': ('m', monster_id)} OR {(4, 7): ('p', player_id) }
                with self.maps[M] as MP:
                    mapplayers = MP.getplayers()
                    size = MP.getsize()
                    for P in mapplayers:
                        #do player action function (P, grid, gridkey, size)
                        with self.players[P] as player:
                            if player.ready(now):
                                action = player.getaction()
                                if action != '':
                                    vector = self.DtoV(action)
                                    playerlocation = player.getlocation()
                                    xaftermove = playerlocation[1] + vector[0]
                                    yaftermove = playerlocation[2] + vector[1]
                                    if size[0] <= xaftermove or xaftermove < 0 or yaftermove < 0 or size[1] <= yaftermove:
                                        self.changescreensrel(P, vector, now)
                                   
                                    elif int(grid[yaftermove][xaftermove]) <= 0:
                                        player.move(vector, now)
                                        player.clearaction()
                                        
                                    #TODO: Handle attacking and picking things up and map transitions (probably going to be funtion calls)

    def changescreensrel(self, player_id, vector, now): 
        with self.players[player_id] as player:
            oldlocation = player.getlocation()
            player.move(vector, now)
            oldmap = oldlocation[0]
            with self.maps[oldmap] as OMP:
                connections = OMP.getconnections()
                newmap = connections[self.directionkey[player.getaction()]]
            player.clearaction()
            with self.maps[newmap] as NMP:
                player.chscreenrel(NMP.getsize(), newmap)
            self.updatemaplocations(player_id, oldmap, newmap)
            with self.players[player_id] as player:
                player.addevent('Entering {}'.format(newmap))
            

    def updatemaplocations(self, player_id, oldmap, newmap):
            with self.maps[oldmap] as OMP:
                deactivate = OMP.removeplayer(player_id)
                if deactivate:
                    self.activemaps.remove(oldmap)
            with self.maps[newmap] as NMP:
                activate = NMP.addplayer(player_id)
                if activate:
                    self.activemaps.append(newmap)
            
    def populatemap(self, M):
        occupied = []
        entityorder = []
        #TODO: For each monster and loot piece
        with self.maps[M] as MP:
            
            players = MP.getplayers()
            #player loop function{
            for P in players:
                with self.players[P] as pl:
                    ploc = pl.getlocation()
                    occupied.append((ploc[1], ploc[2]))
                    entityorder.append(('p', P))
            #}
            #monster loop function
            #loot loop funtion
            grid = MP.getmap()
            populatedmap = []
            for j in range(len(grid)):
                line = []
                for i in range(len(grid[0])):
                    char = grid[j][i]
                    objcount = occupied.count((i, j))
                    for k in range(objcount):
                        entpos = occupied.index((i, j))
                        ent = entityorder[entpos]
                        occupied.remove((i, j))
                        entityorder.remove(ent)
                        if ent[0] == 'p':
                            char = '5'
                        else:
                            char = '4'
                    line.append(char)
                populatedmap.append(line)
            return populatedmap
                                
    def getmaptodraw(self, player_id):
        if player_id not in self.players.keys():
            return ''
        player = self.players[player_id]
        playerlocation = player.getlocation()
        M = playerlocation[0]

        popmap = self.populatemap(M)
        
        prettymap = ['', '']
        for j in range(len(popmap)):
            line = ''
            for i in range(len(popmap[0])):
                space = popmap[j][i]
                if space == '0':
                    line += '_'
                elif space == '1':
                    line += '#'
                elif space == '5':
                    if (playerlocation[1], playerlocation[2]) == (i, j):
                        line += '@'
                    else:
                        line += 'P'
                        #TODO: increment so different other players have different labels
                else:
                    #TODO: add monster values too
                    line += '?'
            prettymap.append(line)
        prettymap.append('')
        prettymap.append('')
        prettymap.append('')
        return prettymap
   
    def getstatregion(self, player_id):
        player = self.players[player_id]
        region = []
        loc = player.getlocation()
        M = loc[0]
        #add centered{
        halfname = len(M) // 2
        line = ''
        for x in range(20 - halfname):
            line += ' '
        line += M
        blank = '            '
        region.append(line)
        region.append(blank)
        #}
        region.append(blank)
        #addstat(label, value, region){
        region.append(' Name:      ')
        line = '  ' + player_id
        if len(line) > 12:
            line = line[:12]
        for x in range(12 - len(line)):
            line += ' '
        region.append(line)
        region.append(blank)
        #return region}
        region.append(' HP:        ')
        HP = player.getHP()
        line = '  {}/{}'.format(HP[0], HP[1])
        for x in range(12 - len(line)):
            line += ' '
        region.append(line)
        region.append(blank)
        region.append(' Weapon:    ')
        equip = player.getequip()
        weap = equip['weapon']
        line = '  {}'.format(weap)
        for x in range(12 - len(line)):
            line += ' '
        region.append(line)
        for x in range(18 - len(region)):
            region.append(blank)

        dest = player.getdestination()
        halfdest = len(dest) // 2
        line = ''
        for x in range(20 - halfdest):
            line += ' '
        line += dest
        return region
        
    def bundlegroupdata(self):
        #TODO: Make Json and compress
        data = {}   
        data['players'] = {}
        #playerbundling
        for P in self.players:
            with self.players[P] as player:
                data['players'][P] = {}
                data['players'][P]['location'] = player.getlocation()
                data['players'][P]['HP'] = player.getHP()
                data['players'][P]['equipment'] = player.getequip()

        #TODO: loop through monsters
        #TODO: loop through loot
        print(data)
        return data #send data and not json so events can be added to the players individualy

    def bundleevents(self, data, player_id):
        with self.players[player_id] as player:
            print(data, '\n data')
            data['events'] = player.getevents()
        return data
        


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

    def clupdateplayers(self, playerdata):
        for player in playerdata:
            if player not in self.players.keys():
                self.addplayer(player)
            self.udplayer(playerdata[player], player)
 
    def udplayer(self, data, player):
        with self.players[player] as P:
            oldlocation = P.getlocation()
            P.setlocation(data['location'])
            P.setHP(data['HP'][0], data['HP'][1])
            if 'equip' in data.keys():
                P.setequip(data['equip'])
            newlocation = P.getlocation()
            if newlocation[0] != oldlocation[0]:
               self.updatemaplocations(player, oldlocation[0], newlocation[0])
            


if __name__ == "__main__":
    W = World()    

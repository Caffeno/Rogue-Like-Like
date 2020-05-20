#!/usr/bin/env python3 

class Map:
    def __init__(self, name, mapdata):
        maplines = mapdata['map'].splitlines()

        self.Mname = name
        self.connections = mapdata['connections']
        self.players = []
        self.playercount = 0        
        #TODO: Monsters, Loot, spawn locations stairs
        self.mapsize = (len(maplines[0]), len(maplines))

        self.map = []
        for j in range(len(maplines)):
            line = []
            for i in range(len(maplines[0])):
                line.append(maplines[j][i])
            self.map.append(line)
        
    def addplayer(self, player_id):
        self.players.append(player_id)
        self.playercount += 1
        if self.playercount == 1:
            return True
        return False

    def removeplayer(self, player_id):
        if player_id in self.players:
            self.players.remove(player_id)
            self.playercount -= 1
            if self.playercount == 0:
                return True
        return False

    def getplayers(self):
        return self.players

    def getconnections(self):
        return self.connections

    def getsize(self):
        return self.mapsize

    def getmap(self):
        return self.map

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

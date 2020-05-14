#!/usr/bin/env python3

import time

class Entity:
    def __init__(self, location, name):
        self.spawntime = time.time()
        self.age = 0
        self.M = location[0]
        self.x = location[1]
        self.y = location[2]
        self.name = name
    def set_blocking(self, val):
        self.blocking = val

    def getlocation(self):
        return [self.M, self.x, self.y]

    def getage(self):
        now = time.time()
        return self.age - now

    def getblocking(self):
        return self.blocking
    
    def __enter__(self):
        return self
   
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class Mob(Entity):
    def __init__(self, HP, speed, location, name):
        self.health = HP
        self.speed = speed
        super().set_blocking(True)
        super().__init__(location, name)
        self.laststep = time.time()
 
    def modifyHP(self, value):
        self.HP += value

    def getHP(self):
        return HP

    def move(self, vector, now):
        if self.speed != 0 and 1 / (self.speed) <=  (now - self.laststep):
            self.x += vector[0]
            self.y += vector[1]
            self.laststep = now

    def chscreen(self, mapsize, newmap):
        self.x = self.x % mapsize[0]
        self.y = self.y % mapsize[1]
        self.M = newmap
        print(self.x, ',', self.y)
            
class Player(Mob):
    def __init__(self, HP, speed, location, name):#, inventory, equipment):
        super().__init__(HP, speed, location, name)
        self.inventory = {}
        self.inventory['money'] = 0 
        self.equipment = {}
        self.equipment['weapon'] = 'Dagger'
        self.action = ""

    def pickup(self, loot):
         self.inventory['money'] += loot

    def setaction(self, action):
        if action == 'up' or action == 'down' or action == 'left' or action == 'right':
            self.action = action
        
    def getaction(self):
        return self.action
    
    def ready(self, now):
        if self.speed != 0 and 1 / self.speed <= now - self.laststep:
            return True
        return False


from ursina import Entity, time
from ursina.ursinamath import Vec2, Vec3
import math


class DaynightCycle:
    def __init__(self):
        self.time_since_start = 0
        self.day_period = 30*60 # seconds
        self.MONSTER_SPAWNING_INTENSITY = 0.3
        self.MAX_MONSTERS = 30
        self.DAY_UNTIL_MAX_MONSTERS = 5

    def day_light_intensity(self):
        return math.cos(2*math.pi*self.time_since_start/(self.day_period)) ** 2

    def calculate_monster_count(self):
        return (self.MAX_MONSTERS)/(1+math.e**(-1*(10*(self.time_since_start/(self.DAY_UNTIL_MAX_MONSTERS*self.day_period))-4)))


    def update(self):
        self.time_since_start+=time.dt

        #If it is night.
        if self.day_light_intensity()<self.ONSTER_SPAWNING_INTENSITY:
            self.spawn_monsters()

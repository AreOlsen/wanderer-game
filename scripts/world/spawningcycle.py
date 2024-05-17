from ursina import Entity, time
from ursina.ursinamath import Vec2, Vec3
import math

##
# DAY NIGHT CYCLE CLASS - THIS IS FOR NEXT GAME UPDATE.
# MIND: NOT IMPLEMENTED FULLY - THIS IS FOR THE NEXT GAME UPDATE. 
##
class DaynightCycle:
    #INIT THE INFO ABOUT THE DAY AND NIGHT CYCLE.
    def __init__(self):
        self.time_since_start = 0
        self.day_period = 30*60 # seconds
        self.MONSTER_SPAWNING_INTENSITY = 0.3
        self.MAX_MONSTERS = 30
        self.DAY_UNTIL_MAX_MONSTERS = 5

    
    #GET THE CURRENT DAYLIGHT INTENSITY.
    def day_light_intensity(self):
        return math.cos(2*math.pi*self.time_since_start/(self.day_period)) ** 2


    #CALCULATE HOW MANY MONSTERS TO SPAWN - RUNS AT NIGHT.
    def calculate_monster_count(self):
        return (self.MAX_MONSTERS)/(1+math.e**(-1*(10*(self.time_since_start/(self.DAY_UNTIL_MAX_MONSTERS*self.day_period))-4)))


    #UPDATE THE DAYNIGHT INFO EACH FRAME.
    def update(self):
        self.time_since_start+=time.dt

        #SPAWN IF NIGHT.
        if self.day_light_intensity()<self.MONSTER_SPAWNING_INTENSITY:
            monsters_to_spawn = self.spawn_monsters()

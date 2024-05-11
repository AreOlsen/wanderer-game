from ursina import Entity, mouse
from ursina.ursinamath import Vec3
import math

class HoldingItem(Entity):
    def __init__(self, texture:str, offset:Vec3, min_angle=0, max_angle=360, size=0.1, **kwargs):
        super().__init__(
            texture=texture,
            size=size,
            position=Vec3(0,1,-0.001)+offset,
            double_sided=True,
        )
        self.min_angle=min_angle
        self.max_angle=max_angle
        for key, val in kwargs.items():
            setattr(self, key, val)

    def calculate_angle_item(self):
        mos_pos = mouse.position
        delta = mos_pos - self.position
        angle = math.acos((delta.x)/((delta.x**2+delta.y**2+delta.z**2)**0.5))
        if angle<self.min_angle:
            angle=self.min_angle
        elif angle>self.max_angle:
            angle=self.max_angle
        return angle

class Food(HoldingItem):
    def __init__(self, hp_increase, player):
        super().__init__()
        self.player = player
        self.hp_increase

    def input(self,key):
        if key=="e":
            self.player.health+=self.hp_increase


class HandheldWeapon(HoldingItem):
    """This is a handheld item."""
    def __init__(self, range):
        super().__init__()
        self.range = range


class Gun(HoldingItem):
    """Gun, this can shoot."""

class InventoryItem(HoldingItem):
    def __init__(self, **kwargs):
        super().__init__()
        for key, val in kwargs.items():
            setattr(self, key, val)

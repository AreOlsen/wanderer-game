from ursina.ursinamath import Vec2
from ursina import Entity, time
import math


class MovingObject(Entity):
    def __init__(
        self,
        velocity=Vec2((0, 0)),
        acc_ex_grav=Vec2((0, 0)),
        gravity=-9.81,
        rotate_y=False,
        rotate_x=False,
        **kwargs,
    ):
        super().__init__()
        self.gravity = gravity
        self.velocity = velocity
        self.acceleration = acc_ex_grav
        self.rotate_y = rotate_y
        self.rotate_x = rotate_x
        self.collider = "mesh"

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        self.update_vel_pos()
        self.update_rotation()

    def update_vel_pos(self):
        acc_incl_grav = self.acceleration + Vec2(0, -abs(self.gravity))
        self.position += self.velocity * time.dt + 0.5 * acc_incl_grav * time.dt**2
        self.velocity += acc_incl_grav * time.dt

    # def update_rotation(self):
    #    #We want to rotate the whole thing.

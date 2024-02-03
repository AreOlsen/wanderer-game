from ursina.ursinamath import Vec2, Vec3
from ursina import Entity, time, raycast, distance_2d
import math
import numpy as np

class MovingObject(Entity):
    def __init__(
        self,
        velocity=Vec2((0, 0)),
        acc_ex_grav=Vec2((0, 0)),
        gravity=-9.81,
        rotate=False,
        **kwargs,
    ):
        super().__init__()
        self.gravity = gravity
        self.velocity = velocity
        self.acceleration = acc_ex_grav
        self.rotate = rotate
        self.collider = "mesh"
        self.texture = None
        self.acc_incl_grav = self.acceleration + Vec2(0, -abs(self.gravity))

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        self.update_vel_pos()
        self.rotate()
        self.collisions()

    def update_vel_pos(self):
        self.velocity += self.acc_incl_grav * time.dt
        self.position += self.velocity * time.dt
        
    def rotate_texture(self):
        if self.rotate:
            angle = 0
            if self.velocity.x!=0:
                angle = -math.atan(self.velocity.y/self.velocity.x)*180/math.pi
            self.rotation = Vec3(0,0,angle)
    
    def collisions(self):
        #We need to check the next position if it collides so we can prevent it before it happens.
        hit_info = self.intersects()
        #If we are colliding.
        if hit_info.hit:
            back = Vec2(0,0)
            for ent in hit_info.entities:
                dist = ent.world_position-self.world_position
                if abs(dist.y) < abs((ent.scale.y + self.world_position.y)/2):
                    back.y = np.sign(dist.y)
                elif abs(dist.x) < abs((ent.scale.x + self.world_position.x)/2):
                    back.x = np.sign(dist.x)
            self.position+=-1*self.velocity*time.dt
            self.velocity*=(Vec2(1,1)-back)
            print(Vec2(1,1)-back)



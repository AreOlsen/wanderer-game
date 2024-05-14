from ursina.ursinamath import Vec2, Vec3
from ursina import Entity, time, raycast, distance_2d, BoxCollider, destroy, scene
import math
import numpy as np
import copy


class MovingObject(Entity):
    def __init__(
        self,
        velocity=Vec2((0, 0)),
        acc_ex_grav=Vec2((0, 0)),
        gravity=-9.81,
        rotate=False,
        bounce_upwards=False,
        bounce_downwards=False,
        bounce_left=False,
        bounce_right=False,
        parent_on_hit=False,
        collides=False,
        destroy_on_hit = False,
        damage_on_collision=0,
        player=None,
        chunk_ents = [],
        **kwargs,
    ):
        super().__init__()

        self.gravity = gravity
        self.velocity = velocity
        self.bounce_upwards = bounce_upwards
        self.bounce_downwards = bounce_downwards
        self.bounce_left = bounce_left
        self.bounce_right = bounce_right
        self.acceleration = acc_ex_grav
        self.collides = collides
        self.rotate = rotate
        self.texture = None
        self.parent_on_hit = parent_on_hit
        self.destroy_on_hit = destroy_on_hit
        self.acc_incl_grav = self.acceleration + Vec2(0, -abs(self.gravity))
        self.damage_on_collision = damage_on_collision
        self.player=player
        self.chunk_ents = chunk_ents
        for key, value in kwargs.items():
            setattr(self, key, value)

        #This is set afterwards as scale can be changed in kwargs and colliders requires scale.
        self.collider = BoxCollider(self, center=(0, 0, 0), size=(self.scale_x, self.scale_y, 0))

    def update(self):
        self.update_vel()
        self.rotate_texture()
        if self.collides:
            self.collisions()
        self.update_pos()

    def update_vel(self):
        self.velocity += self.acc_incl_grav * time.dt

    def update_pos(self):
        self.position += self.velocity * time.dt

    def rotate_texture(self):
        if self.rotate:
            angle = 0
            if self.velocity.x != 0:
                angle = -math.atan(self.velocity.y / self.velocity.x) * 180 / math.pi
            self.rotation = Vec3(0, 0, angle)

    def check_next_collision(self):
        next_hit_ent = Entity(
            position=self.position + self.velocity * time.dt,
        )
        next_hit_ent.collider = BoxCollider(
            next_hit_ent, center=self.collider.center, size=self.collider.size
        )
        hit = copy.copy(next_hit_ent.intersects(ignore=(self, next_hit_ent)))
        destroy(next_hit_ent)
        return hit

    def collision_y(self):
        y_next = self.check_next_collision()
        if y_next.hit:
            if hasattr(y_next.entity, "health"):
                y_next.entity.health -= self.damage_on_collision
            if self.parent_on_hit:
                self.parent = y_next.entity
            diff = y_next.world_point - self.position
            normal_vector = -1 * Vec2(np.sign(diff.x), np.sign(diff.y))
            # Stop velocity y direction.
            bounce_up = self.bounce_upwards and normal_vector.y == 1
            bounce_down = self.bounce_downwards and normal_vector.y == -1
            self.velocity = Vec3(
                self.velocity.x,
                (
                    abs(self.velocity.y)
                    if bounce_up
                    else -abs(self.velocity.y) if bounce_down else 0
                ),
                0,
            )
            if (
                diff.y < -normal_vector.y * (self.collider.size[1]) / 2
                and bounce_up == False
            ):
                self.position = Vec2(
                    self.position.x,
                    normal_vector.y * 0.0001
                    + y_next.world_point.y
                    + (self.collider.size[1]) / 2,
                )

            if self.destroy_on_hit:
                self.chunk_ents.remove(self)
                destroy(self)

    def collision_x(self):
        x_next = self.check_next_collision()
        if x_next.hit:
            if hasattr(x_next.entity, "health"):
                x_next.entity.health -= self.damage_on_collision
            if self.parent_on_hit:
                self.parent = x_next.entity
            # Stop velocity x direction.
            diff = x_next.world_point - self.position
            normal_vector = -1 * Vec2(np.sign(diff.x), np.sign(diff.y))
            bounce_left = self.bounce_left and normal_vector.x == -1
            bounce_right = self.bounce_right and normal_vector.x == 1
            self.velocity = Vec3(
                (
                    abs(self.velocity.x)
                    if bounce_right
                    else -abs(self.velocity.y) if bounce_left else 0
                ),
                self.velocity.y,
                0,
            )

            if self.destroy_on_hit:
                self.chunk_ents.remove(self)
                destroy(self)

    def collisions(self):
        # We need to check the next y position and check if intersection.
        # Then repeat after y position for the x position, we can't do both at the same time.
        # This is to due to the fact that we can fall left down into the ground and then just be stuck when walking.
        # Parent_on_hit makes it such that the object will be stuck in the thing. I.e the arrow gets stuck in the ground.
        # Y.
        self.collision_y()
        # X.
        self.collision_x()

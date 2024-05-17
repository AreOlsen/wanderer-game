from ursina.ursinamath import Vec2, Vec3
from ursina import Entity, time, raycast, distance_2d, BoxCollider, destroy, scene
import math
import numpy as np
import copy

###
# MOVING OBJECT.
###
class MovingObject(Entity):
    #INIT THE MOVING OBJECT CLASS AND THE DIFFERENT FORMS OF IT.
    #SOME MOVING OBJECTS MIGHT WANT TO BOUNCE, SOME NOT, THIS TAKES ALL THAT INTO ACCOUNT.
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
        scale_x=1,
        scale_y=1,
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
        self.scale_x=scale_x
        self.scale_y=scale_y
        self.scale = Vec3(scale_x,scale_y,0)
        
        #ANY OTHER VALUES THAT IS NOT A PARAMETER GIVEN.
        for key, value in kwargs.items():
            setattr(self, key, value)

        #THIS IS SET AFTERWARDS AS SCALE MIGHT BE SET IN *KWARGS.
        self.collider = BoxCollider(self, center=(0, 0, 0), size=(self.scale_x, self.scale_y,0))


    #UPDATE 
    def update(self):
        #UPDATE SPEED.
        self.update_vel()
        #CHECK IF ROTATION IS REQUIRED. - USEFUL FOR HANDHELD WEAPONS.
        self.rotate_texture()
        #CHECK FOR COLLISIONS.
        if self.collides:
            self.collisions()
        #UPDATE THE POSITION.
        self.update_pos()
        #CHECK IF OBJECT NEEDS TO BE SREMOVED.
        self.check_if_death()


    #UPDATE THE VELOCITY BASED ON THE ACCELERATION - KINEMATIC FORMULA.
    def update_vel(self):
        self.velocity += self.acc_incl_grav * time.dt


    #UPDATE THE POSITION BASED ON THE VELOCITY - KINEMATIC FORMULA.
    def update_pos(self):
        self.position += self.velocity * time.dt


    #CHECK IF THE ITEM NEEDS TO BE DELETED AS IT HAS NO HEALTH LEF.T
    def check_if_death(self):
        #NOT ALL MOVING OBJECTS HAS HEALTH - BUT SOME MIGHT.
        if hasattr(self, "health"):
            if self.health<=0:
                self.chunk_ents.remove(self)
                destroy(self)


    #IF THE MOVING OBJECT NEEDS TO BE ROTATED.
    #THIS IS THE CASE FOR ARROWS AND SUCH.
    def rotate_texture(self):
        if self.rotate:
            angle = 0
            if self.velocity.x != 0:
                angle = -math.atan(self.velocity.y / self.velocity.x) * 180 / math.pi
            self.rotation = Vec3(0, 0, angle)

    #CHECK IF THE NEXT POSITION WILL BE COLLIDING.
    #WE CHECK BEFORE AS WE DONT WANT TO ENTER THE COLLIDING OBJECT - WE STOP BEFORE ENTERING.
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
    

    #CHECK FOR ANY COLLISIONS IN THE Y DIRECTION IN THE NEXT POSITION.
    def collision_y(self):
        y_next = self.check_next_collision()
        if y_next.hit:
            #NOT ALL MOVING OBJECTS SHOULD INTERACT WITH THE PLAYER. 
            if hasattr(y_next.entity, "intersects_with_player") and hasattr(self, "inventory"):
                if y_next.entity.intersects_with_player == False:
                    return
            #IF THE MOVING OBJECT HAS HEALTH WE REMOVE DAMAGE ON COLLISION.
            if hasattr(y_next.entity, "health"):
                y_next.entity.health -= self.damage_on_collision
            #IF WE WANT TO SET PARENT ON HIT - THIS IS FOR ARROWS AND SUCH GETTING STUCK IN THE OBJECT.
            if self.parent_on_hit:
                self.parent = y_next.entity
            #GET INFORMAITON ABOUT COLLISION.
            diff = y_next.world_point - self.position
            normal_vector = -1 * Vec2(np.sign(diff.x), np.sign(diff.y))
            bounce_up = self.bounce_upwards and normal_vector.y == 1
            bounce_down = self.bounce_downwards and normal_vector.y == -1
            #IF BOUNCE WE CHANGE VELOCITY DIRECTION - ELSE STOP.
            self.velocity = Vec3(
                self.velocity.x,
                (
                    abs(self.velocity.y)
                    if bounce_up
                    else -abs(self.velocity.y) if bounce_down else 0
                ),
                0,
            )
            #MOVE TO ABOVE OBJECT AS TO NOT BE STUCK INSIDE.
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

            #IF WE WANT TO DESTROY THE MOVING OBJECT ON HIT.
            #THIS IS FOR BULLETS AND SUCH.
            if self.destroy_on_hit:
                self.chunk_ents.remove(self)
                destroy(self)


    #CHECK FOR ANY COLLISIONS IN THE X DIRECTION IN THE NEXT POSITION.
    def collision_x(self):
        x_next = self.check_next_collision()
        if x_next.hit:
            #NOT ALL MOVING OBJECTS SHOULD INTERACT WITH THE PLAYER. 
            if hasattr(x_next.entity, "intersects_with_player") and hasattr(self, "inventory"):
                if x_next.entity.intersects_with_player == False:
                    return
            #IF THE MOVING OBJECT HAS HEALTH WE REMOVE DAMAGE ON COLLISION.
            if hasattr(x_next.entity, "health"):
                x_next.entity.health -= self.damage_on_collision
            #IF WE WANT TO SET PARENT ON HIT - THIS IS FOR ARROWS AND SUCH GETTING STUCK IN THE OBJECT.
            if self.parent_on_hit:
                self.parent = x_next.entity
            #GET INFORMATION ABOUT COLLISION.
            diff = x_next.world_point - self.position
            normal_vector = -1 * Vec2(np.sign(diff.x), np.sign(diff.y))
            bounce_left = self.bounce_left and normal_vector.x == -1
            bounce_right = self.bounce_right and normal_vector.x == 1
            #IF BOUNCE WE CHANGE VELOCITY DIRECTION - ELSE STOP.
            self.velocity = Vec3(
                (
                    abs(self.velocity.x)
                    if bounce_right
                    else -abs(self.velocity.y) if bounce_left else 0
                ),
                self.velocity.y,
                0,
            )

            #IF WE WANT TO DESTROY THE MOVING OBJECT ON HIT.
            #THIS IS FOR BULLETS AND SUCH.
            if self.destroy_on_hit:
                self.chunk_ents.remove(self)
                destroy(self)


    #CHECK FOR ANY COLLISIONS.
    def collisions(self):
        # We need to check the next y position and check if intersection.
        # Then repeat after y position for the x position, we can't do both at the same time.
        # This is to due to the fact that we can fall left down into the ground and then just be stuck when walking.
        
        # Y COLLISION CHECK.
        self.collision_y()
        # X COLLISION CHECK.
        self.collision_x()

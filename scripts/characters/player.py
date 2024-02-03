from ursina import Entity, camera, time, held_keys, BoxCollider, Animation, Animator, Shader
from ursina.ursinamath import Vec2, Vec3
from scripts.moving_object import MovingObject


class Player(MovingObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scale = 1
        self.collider = BoxCollider(self, center=(0,0,0), size=(0.7,0.7,0))
        self.double_sided = True
        self.animator = Animator(
            animations= {
                "idle":Animation("textures/player/idle/sprite", fps=6, autoplay=True, loop=True, parent=self, scale=self.scale),
                "up_jump":Animation("textures/player/jump/up/sprite", fps=6, autoplay=True, loop=True, parent=self, scale=self.scale),
                "down_jump":Animation("textures/player/jump/down/sprite", fps=6, autoplay=True, loop=True, parent=self, scale=self.scale),
                "running":Animation("textures/player/running/sprite", fps=6, autoplay=True, loop=True, parent=self, scale=self.scale),
            }
        )
        self.animator.state = "idle"

    def update(self):
        camera.position = (self.world_position.x, self.world_position.y+1.5*self.scale.y, camera.position.z)
        if held_keys["d"]:
            self.velocity = Vec2(1, self.velocity.y)
            self.animator.state = "running"
            self.scale=Vec3(abs(self.scale.x),self.scale.y,self.scale.z)
        elif held_keys["a"]:
            self.velocity = Vec2(-1, self.velocity.y)
            self.animator.state = "running"
            self.scale=Vec3(-1*abs(self.scale.x),self.scale.y,self.scale.z)
        elif held_keys["space"]:
            self.velocity = Vec2(0, 1)
        else:
            self.velocity = Vec2(0,self.velocity.y)
            if self.velocity.y == 0:
                self.animator.state = "idle"
            elif self.velocity.y > 0:
                self.animator.state = "up_jump"
            elif self.velocity.y < 0:
                self.animator.state = "down_jump"
        self.update_vel_pos()
        self.collisions()

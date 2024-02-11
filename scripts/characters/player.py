from ursina import (
    Entity,
    camera,
    time,
    held_keys,
    BoxCollider,
    Animation,
    Animator,
)
from ursina.ursinamath import Vec2, Vec3
from scripts.moving_object import MovingObject


class Player(MovingObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scale = 1
        self.collider = BoxCollider(self, center=(0, 0, 0), size=(0.5, 0.7, 0))
        self.double_sided = True
        self.animator = Animator(
            animations={
                "idle": Animation(
                    "textures/player/idle/sprite",
                    fps=6,
                    autoplay=True,
                    loop=True,
                    parent=self,
                    scale=self.scale,
                ),
                "up_jump": Animation(
                    "textures/player/jump/up/sprite",
                    fps=6,
                    autoplay=True,
                    loop=True,
                    parent=self,
                    scale=self.scale,
                ),
                "down_jump": Animation(
                    "textures/player/jump/down/sprite",
                    fps=6,
                    autoplay=True,
                    loop=True,
                    parent=self,
                    scale=self.scale,
                ),
                "running": Animation(
                    "textures/player/running/sprite",
                    fps=6,
                    autoplay=True,
                    loop=True,
                    parent=self,
                    scale=self.scale,
                ),
            }
        )
        self.animator.state = "idle"

    def update(self):
        camera.position = (
            self.world_position.x,
            self.world_position.y + 1.5 * self.scale.y,
            camera.position.z,
        )
        self.handle_movement()
        self.update_vel()
        self.collisions()
        self.update_pos()

    def handle_movement(self):
        # We don't want to shwo animations mid air for x movement.
        if self.velocity.y == 0:
            if held_keys["space"]:
                self.velocity = Vec2(self.velocity.x, 4)
            elif held_keys["d"]:
                self.animator.state = "running"
            elif held_keys["a"]:
                self.animator.state = "running"
            else:
                self.animator.state = "idle"
                self.velocity = Vec3(0, self.velocity.y, 0)
        # Change animation for jumping and such.
        if self.velocity.y > 0:
            self.animator.state = "up_jump"
        elif self.velocity.y < 0:
            self.animator.state = "down_jump"
        # We allow x movement in air, but we don't show animation then (we are falling).
        if held_keys["d"]:
            self.velocity = Vec2(1, self.velocity.y)
            self.scale = Vec3(abs(self.scale.x), self.scale.y, self.scale.z)
        elif held_keys["a"]:
            self.velocity = Vec2(-1, self.velocity.y)
            self.scale = Vec3(-1 * abs(self.scale.x), self.scale.y, self.scale.z)

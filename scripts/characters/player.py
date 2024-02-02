from ursina import Entity, camera, time, held_keys
from ursina.ursinamath import Vec2
from scripts.moving_object import MovingObject


class Player(MovingObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = "quad"
        self.scale = 1
        self.texture = "textures/player/mario_test.png"
        self.collider = "mesh"
        self.collision = True

    def update(self):
        camera.position = (self.position.x, self.position.y, camera.position.z)
        if held_keys["d"]:
            self.velocity = Vec2(1, self.velocity.y)
        elif held_keys["a"]:
            self.velocity = Vec2(-1, self.velocity.y)
        else:
            self.velocity = Vec2(0, self.velocity.y)
        self.update_vel_pos()

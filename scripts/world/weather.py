from ursina import Entity, time, camera, destroy
from ursina.ursinamath import Vec2
from scripts.moving_object import MovingObject
import math
import random


class Weather(Entity):
    def __init__(
        self,
        spawning_rate,
    ):
        self.spawning_rate = spawning_rate
        self.parts = []
        self.SPAWNING_OFFSET = 10

    def update(self):
        num_spawn = min(1, math.ceil(self.spawning_rate * time.dt))
        # This will just ensure that we are always spawning above the screen.
        x_width = 2 * camera.position.z * math.tan(math.radians(camera.fov / 2))
        y_spawn_height = (
            x_width / (2 * camera.aspect_ratio_getter()) + self.SPAWNING_OFFSET
        )

        y_despawn_height = -y_spawn_height - 2 * self.SPAWNING_OFFSET
        for i in range(num_spawn):
            rand_x = random(-x_width / 2, x_width / 2)
            pos = Vec2(rand_x, y_spawn_height)

        # Despawn all non-visible weather particles (such as raindroplets).
        for i in self.parts:
            if i.position.y < camera.y + y_despawn_height:
                destroy(i)

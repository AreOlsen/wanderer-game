from ursina import time, destroy
from scripts.moving_object import MovingObject
from ursina.ursinamath import Vec2
import math


class Particle(MovingObject):
    def __init__(
        self,
        texture,
        vel=(0, 0),
        gravity=-0.9,
        scale=1,
        min_scale=0.05,
        time_duration=3,
        fade=True,
        lessen_size=True,
        model="quad",
    ):
        super().__init__(gravity=gravity, velocity=vel)
        self.model = model
        self.texture = texture
        self.min_scale = min_scale
        self.start_scale = scale
        self.scale_x = scale
        self.time_duration = time_duration
        self.fade = fade
        self.lessen_size = lessen_size
        destroy(self, time_duration)

    def update(self):
        if self.lessen_size:
            # Lessen the size.
            cur_scale_factor = (self.min_scale / self.start_scale) ** (
                1 / self.time_duration * time.dt
            )
            self.scale_x *= cur_scale_factor
        if self.fade:
            cur_fade_factor = 0.001 ** (1 / self.time_duration * time.dt)
            self.alpha *= cur_fade_factor
        self.update_vel_pos()

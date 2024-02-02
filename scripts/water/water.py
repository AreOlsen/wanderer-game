from ursina import Sprite, time, texture
from ursina.ursinamath import Vec2
import math


class Water(Sprite):
    def __init__(
        self,
        side_fall_length=0.5,
        start_wave_height=0.125,
        start_wave_period=0.75,
        wave_height_coefficient=0.5,
        wave_period_coefficient=0.25,
        num_waves=3,
        seed=math.random(-(2**7), 2**7) ** kwargs,
    ):
        self.side_fall_length = side_fall_length
        self.start_wave_height = start_wave_height
        self.start_wave_period = start_wave_period
        self.wave_height_coefficient = wave_height_coefficient
        self.wave_period_coefficient = wave_period_coefficient
        self.seed = seed
        self.num_waves = num_waves
        self.time_lasted = 0
        super().__init__()
        for key, value in kwargs:
            setattr(self, key, value)

    def push_up_acc(self, position):
        # Hooke's law but twisted a little: a=k*x, instead of F=k*x.
        # In reality should be buoyancy, b_f=p_f*V*g, but this gives weird gameplay.
        K = 13
        distance_from_top_water = self.scale.y * 0.5 + self.position.y - position.y
        if distance_from_top_water < self.scale.y:
            a = K * distance_from_top_water
            return Vec2(0, a)
        return Vec2(0, 0)

    def water_height_point(self, x_point):
        amp = 0
        for wave_i in range(1, self.num_waves + 1):
            cur_wave_amp = self.start_wave_height * self.wave_height_coefficient ** (
                wave_i - 1
            )
            cur_wave_period = self.start_wave_period * self.wave_period_coefficient ** (
                wave_i - 1
            )
        return amp

    def get_water_texture(self):
        new_texture = Texture()

    def update(self):
        self.time_lasted += time.dt
        self.Texture = get_water_texture()

from scripts.objects.particle import Particle
from ursina import Entity, time
from ursina.ursinamath import Vec2
import math
import random


###
# PARTICLE EMITTER CLASS FOR FIREPLACES AND SUCH.
# NOT CURRENTLY UTILIZED - BUT WILL BE USED IN NEXT UPDATE.
###
class ParticleEmitter(Entity):
    #INIT THE PARTICLE EMITTER.
    def __init__(
        self,
        position,
        particle_texture,
        fade=True,
        lessen_size=True,
        forever=True,
        time_duration=4,
        particle_duration_range=(1.5, 2),
        spawn_radius=0.1,
        spawn_size_range=(0.2, 0.3),
        despawn_size=0.05,
        gravity=-0.9,
        particle_spawn_rate=10,
        vel_range_x=(-0.4, 0.4),
        vel_range_y=(1, 3),
    ):
        super().__init__()
        #INFO ABOUT THE PARTICLE EMITTER.
        self.fade = fade
        self.lessen_size = lessen_size
        self.duration = time_duration
        self.particle_spawn_rate = particle_spawn_rate
        self.forever = forever
        self.particle_texture = particle_texture
        self.particle_duration_range = particle_duration_range
        self.spawn_radius = spawn_radius
        self.gravity = gravity
        self.vel_range_x = vel_range_x
        self.vel_range_y = vel_range_y
        self.spawn_size_range = spawn_size_range
        self.despawn_size = despawn_size
        self.position = position
        self.time_lasted = 0


    #SPAWN INT THE PARTICLES.
    def spawn_particles(self):
        #NUMBER OF PARTICLES TO SPAWN.
        number_to_spawn = math.ceil(self.particle_spawn_rate * time.dt)
        for i in range(number_to_spawn):
            
            #GET THE PARTICLE POSITION.
            spawn_theta = random.random() * 2 * math.pi
            distance_circle = self.spawn_radius * random.random()
            spawn_pos = Vec2(
                distance_circle * math.cos(spawn_theta),
                distance_circle * math.sin(spawn_theta),
            )

            # PARTICLE SIZE.
            scale = random.uniform(self.spawn_size_range[0], self.spawn_size_range[1])

            # PARTICLE SPEED.
            velocity = Vec2(
                random.uniform(self.vel_range_x[0], self.vel_range_x[1]),
                random.uniform(self.vel_range_y[0], self.vel_range_y[1]),
            )

            # PARTICLE LIFETIME.
            particle_duration = random.uniform(
                self.particle_duration_range[0], self.particle_duration_range[1]
            )

            # SPAWN THE PARTICLE.
            new_par = Particle(
                self.particle_texture,
                spawn_pos,
                velocity,
                self.gravity,
                scale,
                self.despawn_size,
                particle_duration,
                self.fade,
                self.lessen_size,
            )
            new_par.parent = self
            self.children.append(new_par)


    #UPDATE - SPAWN IN THE NECESSARY PARTICLES.
    def update(self):
        if self.forever or self.time_lasted <= self.time_duration:
            self.spawn_particles()
            self.time_lasted += time.dt

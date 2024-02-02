from ursina import *
from scripts.objects.particle_emitter import ParticleEmitter
from scripts.world.world import World
from scripts.characters.player import Player
from scripts.world.background import Background

app = Ursina(title="Wanderer.", vsync=False, development_mode=False, borderless=False)

# world = World()
# player = Player(gravity=-9.81, position=(0, 10))
bg = Background(10)
print(camera.position)
app.run()

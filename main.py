from ursina import *
from scripts.objects.particle_emitter import ParticleEmitter
from scripts.world.world import World
from scripts.characters.player import Player
from scripts.world.background import Background

app = Ursina(title="Wanderer.", icon='wanderer_w_icon.ico', vsync=False, development_mode=False, borderless=False)

# world = World()
player = Player(gravity=-1, position=(0, 0))
bg = Background(10,0.9)
w = World()

app.run()

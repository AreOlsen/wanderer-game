from ursina import *
from scripts.objects.particle_emitter import ParticleEmitter
from scripts.world.world import World
from scripts.characters.player import Player
from scripts.world.background import Background
from scripts.hud.corners import Corners
from scripts.hud.mini_map import Minimap
from scripts.hud.inventory import Inventory

app = Ursina(
    title="Wanderer.",
    icon="wanderer_w_icon.ico",
    vsync=False,
    development_mode=True,
    borderless=False,
)

player = Player(gravity=-6, position=(0, 50))
bg = Background(10, 20, 4)
w = World("test1")
corners = Corners()
inv = Inventory()
# mini = Minimap()
# audio = Audio(sound_file_name="sounds/music/titlescreen.mp3", loop=True, autoplay=True)
app.run()

from ursina import *
from scripts.objects.particle_emitter import ParticleEmitter
from scripts.world.world import World
from scripts.characters.player import Player
from scripts.world.background import Background
from scripts.hud.corners import Corners
from scripts.hud.mini_map import Minimap
from scripts.hud.inventory import Inventory, InventoryItem
from scripts.monsters.monster import Monster
from ursina.ursinamath import Vec2

app = Ursina(
    title="Wanderer.",
    icon="wanderer_w_icon.ico",
    vsync=False,
    development_mode=True,
    borderless=False,
)

player = Player(gravity=-6, position=(0, 10))
bg = Background(10, 20, 4)
w = World("test1")
corners = Corners()
monst = Monster(position=Vec2(0, 5))
# inv = Inventory()
# mini = Minimap()
# invI = InventoryItem("textures/items/sword.png","Sword", "Majestic, isn't it?", 0.1)
# audio = Audio(sound_file_name="sounds/music/titlescreen.mp3", loop=True, autoplay=True)
app.run()

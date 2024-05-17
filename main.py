from ursina import *
from scripts.objects.particle_emitter import ParticleEmitter
from scripts.world.world import World
from scripts.characters.player import Player
from scripts.world.background import Background
from scripts.hud.corners import Corners
from scripts.hud.mini_map import Minimap
from scripts.objects.item import HoldingItem
from scripts.hud.gamestate import State, Statechanger
from scripts.hud.inventory import Inventory, InventoryItem
from scripts.monsters.monster import Monster
from ursina.ursinamath import Vec2
from scripts.hud.menus.settings_menu import SettingsMenu
from scripts.hud.menus.game_menus import GameMenu
from scripts.hud.menus.main_menu import MainMenu
from scripts.hud.menus.load_games_menu import LoadGameMenu
from scripts.hud.menus.new_game_menu import NewGameMenu

### 
# INIT GAME.
###
app = Ursina(
    title="Wanderer.",
    icon="wanderer_w_icon.ico",
    vsync=False,
    development_mode=True,
    borderless=False,
)


###
# MENUS.
###
state_changer = Statechanger()
START_MENU=MainMenu(state_changer)
state_changer.add_state(START_MENU,"start_menu")
GAME_MENU=GameMenu(state_changer)
state_changer.add_state(GAME_MENU,"game_menu")
SETTINGS_MENU=SettingsMenu(state_changer)
state_changer.add_state(SETTINGS_MENU,"settings_menu")
LOAD_MENU=LoadGameMenu(state_changer)
state_changer.add_state(LOAD_MENU,"load_game_menu")
NEW_GAME_MENU=NewGameMenu(state_changer)
state_changer.add_state(NEW_GAME_MENU,"new_game_menu")
state_changer.choose_state("start_menu")

###
# TEMPORARY MUSIC. COMMENT OUT music FOR NO MUSIC.
###
music = Audio(sound_file_name="sounds/music/titlescreen.mp3",volume=0.2, autoplay=True, loop=True)

###
# RUN GAME.
###
app.run()

from scripts.hud.menus.menu_baseframe import MenuState
from scripts.hud.menus.menu_buttons import RedirectButton, QuitButton
from scripts.hud.menus.game_title import Gametitle
from ursina import Entity, camera, Sprite, application
from ursina.ursinamath import Vec2, Vec3
import math

###
# MAIN MENU STATE.
###
class MainMenu(MenuState):
    def __init__(self, state_changer):
        super().__init__()
        TITLE = Gametitle(scale=1,parent=camera.ui)
        PLAY = RedirectButton(texture="textures/hud/board.png", scale_x=0.3,scale_y=0.1, to_state="game_menu", state_changer=state_changer, text="Play")
        #It is planned that the current keybinds menu will have settings, hence it is for the time being called settings.
        SETTINGS = RedirectButton(texture="textures/hud/board.png", scale_x=0.3,scale_y=0.1, to_state="settings_menu", state_changer=state_changer, text="Keybinds")
        QUIT = QuitButton(texture="textures/hud/board.png", scale_x=0.3,scale_y=0.1, text="Exit")
        self.add_element(SETTINGS)
        self.add_element(PLAY)
        self.add_element(QUIT)
        self.add_element(TITLE)

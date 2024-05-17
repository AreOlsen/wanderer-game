from scripts.hud.menus.menu_baseframe import MenuState
from scripts.hud.menus.menu_buttons import RedirectButton, QuitButton
from scripts.hud.menus.game_title import Gametitle
from ursina import Entity, camera, Sprite
from ursina.ursinamath import Vec2, Vec3
import math

###
# GAME MENU (NEW OR LOAD GAME) STATE.
###
class GameMenu(MenuState):
    def __init__(self, state_changer):
        super().__init__()
        TITLE = Gametitle(scale=1,parent=camera.ui)
        NEW_GAME = RedirectButton(texture="textures/hud/board.png", scale_x=0.3,scale_y=0.1, to_state="new_game_menu", state_changer=state_changer, text="New game")
        LOAD_GAME = RedirectButton(texture="textures/hud/board.png", scale_x=0.3,scale_y=0.1, to_state="load_game_menu", state_changer=state_changer, text="Load game")
        self.BACK = RedirectButton(texture="textures/hud/board.png", scale_x=0.3,scale_y=0.1, to_state="start_menu", state_changer=state_changer, text="Back")
        self.BACK.position = Vec3(-0.7,0.4,-1)
        self.BACK.parent = camera.ui
        self.add_element(NEW_GAME)
        self.add_element(TITLE)
        self.add_element(LOAD_GAME)


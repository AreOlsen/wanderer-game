from scripts.hud.menus.menu_baseframe import MenuState
from scripts.hud.menus.menu_buttons import RedirectButton, QuitButton, LoadGameButton
from scripts.hud.menus.game_title import Gametitle
from ursina import Entity, camera, Sprite
from ursina.ursinamath import Vec2, Vec3
import math
import os

###
# LOAD GAME MENU STATE.
###
class LoadGameMenu(MenuState):
    def __init__(self, state_changer):
        super().__init__()
        for save_file in os.listdir("data/world_saves/"):
            save_file,_ = os.path.splitext(save_file)
            self.add_element(LoadGameButton(texture="textures/hud/board.png", scale_x=0.3,scale_y=0.1, save_name=save_file, state_changer=state_changer, text=save_file))
        self.BACK = RedirectButton(texture="textures/hud/board.png", scale_x=0.3,scale_y=0.1, to_state="start_menu", state_changer=state_changer, text="Back")
        self.BACK.parent = camera.ui
        self.BACK.position = Vec3(-0.7,0.4,-1)


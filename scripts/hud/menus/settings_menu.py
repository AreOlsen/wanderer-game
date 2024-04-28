from scripts.hud.menus.menu_baseframe import MenuState
from scripts.hud.menus.menu_buttons import RedirectButton, QuitButton, LoadGameButton
from scripts.hud.menus.game_title import Gametitle
from ursina import Entity, camera, Sprite, camera
from ursina.ursinamath import Vec2, Vec3
import math
import os

class SettingsMenu(MenuState):
    def __init__(self, state_changer):
        super().__init__(button_distance=0)
        self.add_element(Entity(model="quad", texture="textures/hud/board.png", scale_x=0.7,scale_y=0.7, parent=camera.ui))
        self.add_element(Entity(model="quad", texture="textures/hud/actions.png", scale_x=0.5, scale_y=0.55, parent=camera.ui))
        self.BACK = RedirectButton(texture="textures/hud/board.png", scale_x=0.3,scale_y=0.1, to_state="start_menu", state_changer=state_changer, text="Back")
        self.BACK.parent = camera.ui
        self.BACK.position = Vec3(-0.7,0.4,-1)

        #AT THIS MOMENT IN TIME, WE ARE A LITTLE LIMITED BY URSINA'S ABILITIES.
        #WE CANNOT MODIFY MUCH INFORMATION, SUCH AS FOV, OR KEYBINDS. 
        #HENCE FOR THE TIME BEING A KEYBINDINGS DISPLAY WILL SHOW.
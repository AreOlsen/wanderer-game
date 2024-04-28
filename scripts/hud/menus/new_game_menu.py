from scripts.hud.menus.menu_baseframe import MenuState
from scripts.hud.menus.menu_buttons import RedirectButton, QuitButton, LoadGameButton, InputButtonField, ButtonChoice, NewGameButton
from scripts.hud.menus.game_title import Gametitle
from ursina import Entity, camera, Sprite
from ursina.ursinamath import Vec2, Vec3
import math
import os

class NewGameMenu(MenuState):
    def __init__(self, state_changer):
        super().__init__()
        TITLE = Gametitle(scale=1,parent=camera.ui)
        self.BACK = RedirectButton(texture="textures/hud/board.png", scale_x=0.3,scale_y=0.1, to_state="start_menu", state_changer=state_changer, text="Back")
        self.BACK.parent = camera.ui
        self.BACK.position = Vec3(-0.7,0.4,-1)
        SAVE_NAME = InputButtonField(texture="textures/hud/board.png", scale_x=0.3,scale_y=0.1, text="Save name")
        SEED = InputButtonField(texture="textures/hud/board.png", scale_x=0.3,scale_y=0.1, text="Seed")
        CHOICES = ButtonChoice(("Easy", "Medium", "Hard"), texture="textures/hud/board.png", min_choice=1, max_choice=1)
        #PURIFY SEED.
        _seed = "0"
        for char in SEED.text:
            if char.isdigit():
                _seed+=char
            else:
                _seed+="0"
        _seed=int(_seed)
        NEW_GAME = NewGameButton(texture="textures/hud/board.png", scale_x=0.3,scale_y=0.1, save_name=SAVE_NAME.text, state_changer=state_changer, text="Start", seed=_seed,difficulty=CHOICES.value)
        self.add_element(SEED)
        self.add_element(SAVE_NAME)
        self.add_element(CHOICES)
        self.add_element(TITLE)
        self.add_element(NEW_GAME)
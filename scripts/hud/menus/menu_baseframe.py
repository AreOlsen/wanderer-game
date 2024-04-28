from scripts.hud.gamestate import State
from scripts.hud.menus.menu_buttons import RedirectButton
from ursina import Entity, camera, Sprite
from ursina.ursinamath import Vec2, Vec3
import math

class MenuState(State):
    def __init__(self, background="textures/hud/main_menu_background.png", audio="sounds/music/titlescreen.mp3", button_distance=0.15):
        self.buttons=[]
        super().__init__(entities=[],audio=audio)
        z_sum = abs(500 - camera.position.z)
        s_x = 2 * abs(math.tan(math.radians(camera.fov_getter() / 2))) * z_sum
        self.background = Entity(
            texture=background,
            model="quad",
            world_position=Vec3(camera.position.x, camera.position.y, 500),
            scale_x=s_x,
            scale_y=s_x / camera.aspect_ratio_getter(),
            parent=camera,
            enabled=True
        )
        self.button_distance = button_distance
        self.space_out_buttons()

    def space_out_buttons(self):
        for i in range(len(self.buttons)):
            button = self.buttons[i]
            button.parent = camera.ui
            button.position = Vec3(camera.position.x,math.floor((i+1)/2)*self.button_distance*(-1)**(math.ceil(i+1)), camera.position.z+1)

    def add_element(self, element):
        self.buttons.append(element)
        self.space_out_buttons()

    def on_disable(self):
        for ent in self.buttons:
            ent.enabled=False
        if hasattr(self,"BACK"):
            self.BACK.enabled=False
        if hasattr(self,"background_music"):
            self.background_music.enabled=False
        if hasattr(self,"background"):
            self.background.enabled=False
        self.enabled=False

    def on_enable(self):
        self.enabled=True
        for ent in self.buttons:
            ent.enabled=True
        if hasattr(self,"BACK"):
            self.BACK.enabled=True
        if hasattr(self,"background_music"):
            self.background_music.enabled=True
        if hasattr(self,"background"):
            self.background.enabled=True

    
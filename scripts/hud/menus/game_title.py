from ursina import Entity


###
# GAME TITLE ELEMENT.
###
class Gametitle(Entity):
    def __init__(self, scale, parent):
        super().__init__(model="quad", texture="textures/hud/game_title.png", scale_x=0.5*scale,scale_y=0.1*scale, parent=parent)
        
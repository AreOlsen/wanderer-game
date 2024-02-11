from ursina import camera, Entity, rgb, window
from ursina.ursinamath import Vec2


class Minimap(Entity):
    def __init__(self):
        super().__init__()
        self.model = "quad"
        self.texture = "textures/hud/mini_map.png"
        self.parent = camera.ui
        self.scale = 0.25
        self.offset_x = 0.15
        self.offset_y = 0.15
        self.map_chunks_radius = 3
        self.position = Vec2(window.left.x + self.offset_x, window.top.y - self.offset_y)
    
    """
        IMPLEMENT MINIMAP.
    """

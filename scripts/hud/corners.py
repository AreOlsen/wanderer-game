from ursina import camera, Entity, window
import math

class Corners:
    def __init__(self,
                texture ="textures/hud/corner.png",
                size_scale = 0.05,
                offset_x = 0.1,
                offset_y = 0.1):
        self.texture = texture
        self.size_scale = size_scale
        self.offset_x = offset_x
        self.offset_y = offset_y
        #Load in all corners, they are placed - well - in the corners.
        #We use math to quickly place the corners, and we rotate them as well at the same time.
        self.corners = [
            Entity(
                parent=camera.ui,
                scale=size_scale,
                model="quad",
                texture=texture,
                x = window.left.x + offset_x if i == 0 or i == 1 else window.right.x - offset_x,
                y = window.bottom.y + offset_y if i == 0 or i == 3 else window.top.y -  offset_y,
                rotation_z = i*90
            )
            for i in range(4)
        ]

from ursina import Sprite, Entity, camera
from ursina.ursinamath import Vec3
import math
import glob
import os
from PIL import Image
import re


class Background(Sprite):
    def __init__(self, z_position):
        # Get all background images' path and put into a list.
        self.images = [path for path in glob.glob("textures/background/*.png")]
        # Denne funksjonen sorterer basert på talnummeret i namnet på bilete-filen.
        sorterings_funksjon = (
            lambda path: int(re.search(r"\d+", path).group())
            if re.search(r"\d+", path)
            else 0
        )
        # Sorterer filbaner basert på talnummer.
        self.images = sorted(self.images, key=sorterings_funksjon, reverse=True)

        # Get the desired 3d z distance from the background object and the camera.
        z_sum = abs(z_position - camera.position.z)
        # The background image object size in x direction.
        s_x = 2 * abs(math.tan(math.radians(camera.fov_getter() / 2))) * z_sum
        # Make the backgrounds into objects using the previous calculated properties.
        self.image_sprites = [
            Entity(
                texture=path,
                model="quad",
                scale_x=s_x,
                parent=camera,
                # the size in y direction is the size in x, multiplied by the inverse aspect ratio of the image.
                scale_y=s_x * (Image.open(path).height / Image.open(path).width),
                ppu=16,
                world_position=Vec3(0, 0, z_position),
            )
            for path in self.images
        ]

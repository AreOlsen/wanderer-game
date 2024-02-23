from ursina import Sprite, Entity, camera, color
from ursina.ursinamath import Vec3
from natsort import natsorted
import math
import glob
from PIL import Image


class Background(Entity):
    def __init__(self, z_position, y_position, movement_factor):
        super().__init__()
        self.movement_factor = movement_factor
        # Get all background images' path and put into a list.
        self.images = glob.glob("textures/background/*.png")
        # Sort the list such that we images are displayed in correct order.
        self.images = natsorted(self.images)
        self.y_position = y_position
        # Get the desired 3d z distance from the background object and the camera.
        z_sum = abs(z_position - camera.position.z)

        # The background image object size in x direction.
        self.s_x = 2 * abs(math.tan(math.radians(camera.fov_getter() / 2))) * z_sum

        # We want a constant background colour which is shown when the normal parallax images aren't in view, for empties skies and such.
        self.constant_background = Sprite(
            color=color.rgb(118, 184, 226),
            world_position=Vec3(camera.position.x, camera.position.y, z_position),
            scale_x=self.s_x,
            scale_y=self.s_x / camera.aspect_ratio_getter(),
            parent=camera,
        )

        # Make the backgrounds into objects using the previous calculated properties.
        # We spawn in two because if the camera is inbetween the need two to show the world continously.
        # the size in y direction is the size in x, multiplied by the inverse aspect ratio of the image.
        self.image_sprites = [
            (
                Entity(
                    texture=path,
                    model="quad",
                    scale_x=self.s_x,
                    scale_y=self.s_x
                    * (Image.open(path).height / Image.open(path).width),
                    ppu=16,
                    parent=camera,
                    world_position=Vec3(
                        camera.position.x, y_position, z_position - i / 1000
                    ),
                ),
                Entity(
                    texture=path,
                    model="quad",
                    scale_x=self.s_x,
                    scale_y=self.s_x
                    * (Image.open(path).height / Image.open(path).width),
                    ppu=16,
                    parent=camera,
                    world_position=Vec3(
                        camera.position.x, y_position, z_position - i / 1000
                    ),
                ),
            )
            for i, path in enumerate(self.images, start=1)
        ]

    def movement_speed(self, j):
        return 1 / (self.movement_factor ** (2) * j)

    def update(self):
        # We move the images according to a movement factor and then using basic sawtooth math we repeat the images.
        for j, image_set in enumerate(reversed(self.image_sprites), start=1):
            offset_x = -(self.movement_speed(j) * camera.position.x / (self.s_x)) % 1
            offset_y = -(camera.y - self.y_position) * self.movement_speed(j) * 1.5
            for i, image in enumerate(image_set, start=0):
                image.position = Vec3(
                    offset_x * self.s_x - self.s_x * (i),
                    offset_y,
                    image.position.z,
                )

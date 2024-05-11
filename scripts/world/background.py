from ursina import Sprite, Entity, camera, color, scene, Texture
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
        z_sum = abs(z_position - camera.world_position.z)

        # The background image object size in x direction.
        self.s_x = 2 * abs(math.tan(math.radians(camera.fov_getter() / 2))) * z_sum

        self.z_position = z_position


        # Make the backgrounds into objects using the previous calculated properties.
        # We spawn in two because if the camera is inbetween the need two chunks to show the world continously.
        # The size in y direction is the size in x, multiplied by the inverse aspect ratio of the image.
        self.image_sprites = [
            (
                Entity(
                    texture=path,
                    model="quad",
                    scale_x=self.s_x,
                    scale_y=self.s_x * (Image.open(path).height / Image.open(path).width),
                    ppu=16,
                    parent=camera,
                    world_position=Vec3(
                        camera.world_position.x, y_position, z_position - i / 20
                    ),
                ),
                Entity(
                    texture=path,
                    model="quad",
                    scale_x=self.s_x,
                    scale_y=self.s_x * (Image.open(path).height / Image.open(path).width),
                    ppu=16,
                    parent=camera,
                    world_position=Vec3(
                        camera.world_position.x, y_position, z_position - i/20
                    ),
                ),
            )
            for i, path in enumerate(self.images, start=1)
        ]
        
        # We want a constant background colour which is shown when the normal parallax images aren't in view, for empties skies and such
        self.constant_sky_background = Entity(
            parent=camera,
            texture=Texture(Image.new(mode="RGBA",size=(256,256), color=(118,184,226,256))),
            color=color.white,
            model="quad",
            world_position=Vec3(camera.world_position.x, camera.world_position.y, z_position),
            scale_x=self.s_x,
            scale_y=self.s_x / camera.aspect_ratio_getter(),
            scale_z=0,
        )


        #Constant underground background for when we go under the ground.
        #self.constant_underground_background = Sprite(
        #    color=color.rgb(7,14,9),
        #    world_position=Vec3(camera.world_position.x,min(self.image_sprites[-1][0].world_position.y-self.image_sprites[-1][0].scale_y,camera.world_position.y,self.z_position)),
        #    scale_x=self.s_x,
        #    scale_y=self.s_x/camera.aspect_ratio_getter(),
        #    parent=camera,
        #)
        #print(self.constant_underground_background.world_position)

    def movement_speed(self, j):
        return 1 / (self.movement_factor ** (2) * j)

    def update(self):
        #Update underground.
        #self.constant_underground_background.world_position=Vec3(camera.world_position.x,min(self.image_sprites[-1][0].world_position.y-self.image_sprites[-1][0].scale_y,camera.world_position.y,self.z_position))
        #print(self.constant_underground_background.world_position)
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

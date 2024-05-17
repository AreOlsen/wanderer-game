from ursina import Sprite, Entity, camera, color, scene, Texture
from ursina.ursinamath import Vec3
from natsort import natsorted
import math
import glob
from PIL import Image

###
# BACKGROUND OBJECT.
###
class Background(Entity):
    #INIT INFORMATION ABOUT THE BACKGROUND SPRITES.
    def __init__(self, z_position, y_position, movement_factor):
        super().__init__()

        #MOVEMENT FACTOR DECIDES HOW FAST THE BACKGROUNDS ARE MOVING WHEN PLAYER MOVES.
        self.movement_factor = movement_factor

        #GET ALL BACKGROUND IMAGES.
        self.images = glob.glob("textures/background/*.png")

        #SORT THE LIST SO THAT THE ORDER OF RENDER IS CORRECT.
        self.images = natsorted(self.images)
        self.y_position = y_position

        #GET THE DESIRED Z POSITION IN THE WORLD TO SPAWN THE SPRITES AT.
        z_sum = abs(z_position - camera.world_position.z)

        #BACKGROUND SPRITE SIZE IN X DIRECTION.
        self.s_x = 2 * abs(math.tan(math.radians(camera.fov_getter() / 2))) * z_sum

        #POSITION FOR BACKGROUND SPRITES IN Z DIRECTION.
        self.z_position = z_position


        #SPAWN THE BACKGROUND SPRITES.
        #SPAWN IN TWO SPRITES, AS WHEN CROSSING THE BORDER THERE NEEDS TO BE A NEW IDENTICAL SPRITE TO CONTINUE THE PATTERN.
        #SCALE IN Y DIRECTION FOR THE SPRITE IS CALCULATED USING THE SCALE IN X DIRECTION.
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
        

        #CONSTANT BACKGROUND BEHIND THE CLOUDS AND SUCH, THIS IS JUST A PLAIN SKY.
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


    #GET THE MOVEMENT SPEED USING THE MOVEMENT FACTOR. 
    #THE SPEED CHANGES BASED ON DISTANCE FROM THE PLAYER, THIS CREATES A PARALLAX EFFECT.
    def movement_speed(self, j):
        return 1 / (self.movement_factor ** (2) * j)


    #UPDATE THE POSITIONS FOR THE BACKGROUND USING PARALLAX.
    def update(self):
        #MOVE THE SPRITES IN SAWTOOTH PATTERN TO CREATE CONTINUATION IN SPRITES FOR CROSSING CHUNKS.
        for j, image_set in enumerate(reversed(self.image_sprites), start=1):
            offset_x = -(self.movement_speed(j) * camera.position.x / (self.s_x)) % 1
            offset_y = -(camera.y - self.y_position) * self.movement_speed(j) * 1.5
            for i, image in enumerate(image_set, start=0):
                image.position = Vec3(
                    offset_x * self.s_x - self.s_x * (i),
                    offset_y,
                    image.position.z,
                )

from ursina import Sprite, Entity, Texture
from ursina.ursinamath import Vec2, Vec3
from opensimplex import noise2
import json
from numpy import array
from PIL import Image
from scripts.world.dead_dropping_entity import DeadDroppingEntity
import math
import random
from scripts.moving_object import MovingObject
import os
import copy
"""
Each chunk consists of two parts.
One part is the actual chunk, this is what gets rendered.
The other part is the block data, this is what the chunk consists of.
The individual blocks do not get drawn individually, but help build one big chunk which then gets drawn.
"""

def chance_for_ore_based_on_y(y:float, max_chance=0.25, max_y_level = -5, min_y_level = -40):
    """This calculates the chance for an ore to be at at specific y level - using math."""
    if y >= max_y_level:
        return 0
    elif y <= min_y_level:
        return max_chance
    else:
        c=4.6 # -math.log(100/99 - 1), bruker modifisert versjon av 1/(1+e^(-bx+c)) for å rekne ut sannsyn.
        b=2*c
        y_under_max_y_level_dist = abs(max_y_level-abs(y))
        range_max_min = abs(max_y_level-min_y_level)
        return max_chance/(1+math.e**(-b*((y_under_max_y_level_dist)/range_max_min)+c))


class Chunk(Entity):
    _biomes = json.load(open("scripts/world/biomes.json", "r"))

    def __init__(self, top_left_world_position: Vec2, chunk_size=12, **kwargs):
        super().__init__()
        self.entities = []
        self.CHUNK_SIZE = chunk_size
        self.world_position = top_left_world_position
        self.ground_entity = Entity(world_position=self.world_position,visible=False)
        self.ground_entity.ground_blocks_entities = []
        self.ground_block_positions = []
        self.background_blocks = []

        self.CHUNK_TYPE = list(self._biomes.keys())[
            int(
                round(
                    noise2(self.position.x * 0.01, self.position.y * 0.0001)
                    * len(self._biomes.keys())
                )
            )
        ]
        self.generate_blocks()
        chunk_texture = self.generate_chunk_block_textures()
        self.scale=self.CHUNK_SIZE
        self.world_position+=Vec2(self.CHUNK_SIZE/2-0.5,-self.CHUNK_SIZE/2+0.5)
        self.model="quad"
        self.texture = chunk_texture
        self.generate_foliage()
        self.ground_entity.combine()
        self.ground_entity.collider = "mesh"
        for key, value in kwargs.items():
            setattr(self, key, value)

    def generate_chunk_block_textures(self):
        block_px = 16
        chunk_texture_image = Image.new(mode="RGBA",size=(block_px*self.CHUNK_SIZE,block_px*self.CHUNK_SIZE), color=0)
        for x_blocks in self.ground_entity.ground_blocks_entities:
            for block in x_blocks:
                pos_x_px = block.position.x*block_px
                pos_y_px = block.position.y*block_px
                chunk_texture_image.paste(Image.open("textures/blocks/"+block.texture.name),(int(pos_x_px),int(-pos_y_px)))
        tex = Texture(chunk_texture_image)
        return tex

    def generate_blocks(self):
        for x in range(int(self.CHUNK_SIZE)):
            # Surface height.
            surface_y = 3 * noise2(x=(x + self.world_position.x) * 0.1, y=0)
            blocks_x = []
            blocks_x_cords = []
            for y in range(int(self.CHUNK_SIZE)):
                block_cords = Vec2(x, -y)
                if block_cords.y+self.world_position.y < surface_y:
                    #Choose groundblock type - we assume we are in the ground and are not an ore.
                    block_type = "under_surface_block"

                    # If top block, such as grass block, we set that.
                    if 0 <= surface_y - (block_cords.y+self.world_position.y) <= 1:
                        block_type = "surface_block"
                    item_obj_data=Chunk._biomes[self.CHUNK_TYPE]["block_types"][block_type]["dropped_resource"]
                    texture = Chunk._biomes[self.CHUNK_TYPE]["block_types"][block_type]["texture"]
                    #Check if we are an ore.
                    if random.uniform(0,1)<=chance_for_ore_based_on_y(y=(block_cords.y+self.world_position.y)):
                        block_type = random.choice(list(Chunk._biomes[self.CHUNK_TYPE]["block_types"]["ores"].keys()))
                        item_obj_data=Chunk._biomes[self.CHUNK_TYPE]["block_types"]["ores"][block_type]["dropped_resource"]
                        texture = Chunk._biomes[self.CHUNK_TYPE]["block_types"]["ores"][block_type]["texture"]
                    # Spawn in the block, and store it into ground blocks.
                    block = DeadDroppingEntity(
                        position=block_cords,
                        texture=texture,
                        item_obj_data=item_obj_data,
                        _parent=self.ground_entity,
                        collider_enabled=True,
                        collider_scale=Vec3(1,1,0),
                        model="quad",
                        origin=(0,0)
                    )
                    blocks_x.append(block)
                    blocks_x_cords.append(copy.copy(block.position))
            self.ground_entity.ground_blocks_entities.append(blocks_x)
            self.ground_block_positions.append(blocks_x_cords)

    def generate_foliage(self):
        #Info about foliage.
        foliage_chances = [Chunk._biomes[self.CHUNK_TYPE]["foliage"][foliage_name]["spawn_rate"] for foliage_name in Chunk._biomes[self.CHUNK_TYPE]["foliage"]]
        foliage_names = list(Chunk._biomes[self.CHUNK_TYPE]["foliage"].keys())
        for x in range(self.CHUNK_SIZE): 
            #What foliage to spawn
            chosen_foliage_name = random.choices(foliage_names + [""], foliage_chances + [1 - sum(foliage_chances)], k=1)[0]
            if self.CHUNK_SIZE>len(self.ground_entity.ground_blocks_entities[x])>=1:
                #If no foliage is chosen we ignore the column.
                if chosen_foliage_name=="":
                    continue
                #Get info about the chosen foliage.
                plant_obj = Chunk._biomes[self.CHUNK_TYPE]["foliage"][chosen_foliage_name]
                spawn_y = self.ground_entity.ground_blocks_entities[x][0].world_position.y+0.5*plant_obj["size_y"]+1.5*self.ground_entity.ground_blocks_entities[x][0].scale_y
                spawn_x = self.ground_entity.ground_blocks_entities[x][0].world_position.x
                #Spawn the foliage.
                plant = DeadDroppingEntity(
                    model="quad",
                    texture=plant_obj["texture"],
                    world_position=Vec3(spawn_x,spawn_y,random.uniform(0.11,0.00000001)),
                    _parent=self,
                    item_obj_data=plant_obj["dropped_resource"],
                    scale_x=plant_obj["size_x"],
                    scale_y=plant_obj["size_y"],
                    double_sided=True,
                    origin=(0,-plant_obj["size_y"]/2)
                )
                self.entities.append(plant)
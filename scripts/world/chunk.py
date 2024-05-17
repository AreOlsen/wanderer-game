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


#CHANCE FOR AN ORE TO SPAWN AT Y LEVEL.
def chance_for_ore_based_on_y(y:float, max_chance=0.25, max_y_level = -5, min_y_level = -40):
    #IF ABOVE MAX SPAWNING RANGE - NO ORE SPAWN.
    if y >= max_y_level:
        return 0
    #IF BELOW THE RANGE - THEN FULL CHANCE.
    elif y <= min_y_level:
        return max_chance
    else:
        #MATH CALCULATION FOR CHANCE.
        c=4.6
        b=9.2
        y_under_max_y_level_dist = abs(max_y_level-abs(y))
        range_max_min = abs(max_y_level-min_y_level)
        return max_chance/(1+math.exp(-b*((y_under_max_y_level_dist)/range_max_min)+c))



###
# CHUNK OBJECT.
###
class Chunk(Entity):
    #GET ALL THE INFORMATION ABOUT THE BIOMES - A CHUNK HAS A BIOME.
    _biomes = json.load(open("scripts/world/biomes.json", "r"))

    #INIT THE CHUNK.
    def __init__(self, chunk_pos, top_left_world_position: Vec2, chunk_size=12, world=None, **kwargs):
        #INIT THE ENTITY.
        super().__init__()
        #STORE ALL THE ENTITIES IN THE CHUNK.
        self.entities = []
        self.CHUNK_SIZE = chunk_size
        self.world_position = top_left_world_position
        #THIS REPRESENTENTS THE DATA ABOUT THE BLOCKS IN THE GROUND.
        #THE CHUNK ENTITY ONLY HAS THE TEXTURE - NOT THE ACTUAL BLOCKS IN THE GROUND - OPTIMIZATION.
        self.ground_entity = Entity(world_position=self.world_position,visible=False)
        self.ground_entity.ground_blocks_entities = []
        self.ground_block_positions = []
        #GET THE CHUNK INDEX.
        self.chunk_pos = chunk_pos
        #GET THE WORLD REFERENCE.
        self.world=world

        #GET THE CHUNK TYPE USING PERLIN NOISE AND THE WORLD SEED.
        #THIS ADDS VARIATION TO THE GAME.
        self.CHUNK_TYPE = list(self._biomes.keys())[
            int(
                round(
                    noise2(self.position.x * 0.01, self.position.y * 0.0001)
                    * len(self._biomes.keys())
                )
            )
        ]
        #GENERATE ALL THE GROUND BLOCKS IN THE CHUNK
        self.generate_blocks()
        #GET THE TEXTURE FOR THE CHUNK - THIS ENTITY CLASS.
        chunk_texture = self.generate_chunk_block_textures()
        #SET INFORMATION THE CHUNK OBJECT.
        self.scale=self.CHUNK_SIZE
        self.world_position+=Vec2(self.CHUNK_SIZE/2-0.5,-self.CHUNK_SIZE/2+0.5)
        self.model="quad"
        self.texture = chunk_texture
        #GENERATE FOLIAGE FOR THE CHUNK - TREES PRIMARILY.
        self.generate_foliage()
        #COMBINE ALL THE GROUND BLOCKS INTO ONE ENTITY - PREVENTS EXCESSIVE DATA - OPTIMIZATION.
        self.ground_entity.combine()
        self.ground_entity.collider = "mesh"
        
        #SET ALL OTHER POSSIBLE PROPERTIES FOR THE CHUNK.
        for key, value in kwargs.items():
            setattr(self, key, value)


    #MOVING OBJECTS CAN MOVE BETWEEN CHUNKS. 
    #UPDATE THE MOVING OBJECT'S CHUNK IF MOVES OVER BORDERS.
    def move_items_cross_chunk(self):
        for i in self.entities:
            if i.__class__.__name__=="MovingObject":
                if self.world!=None:
                    chunk_indicies = self.world.pos_to_chunk_indicies(i.world_position)
                    if chunk_indicies!=self.chunk_pos:
                        self.world.all_chunks[chunk_indicies].entities.append(i)
                        self.entities.remove(i)


    #CHECK IF ANY MOVING OBJECTS HAVE MOVED OVER THE BORDER.
    def update(self):
        self.move_items_cross_chunk()


    #GENERATE THE TEXTURE FOR THE CHUNK.
    def generate_chunk_block_textures(self):
        #USING PIL - WE GENERATE THE CHUNK TEXTURE.
        block_px = 16
        chunk_texture_image = Image.new(mode="RGBA",size=(block_px*self.CHUNK_SIZE,block_px*self.CHUNK_SIZE), color=0)
        for x_blocks in self.ground_entity.ground_blocks_entities:
            for block in x_blocks:
                pos_x_px = block.position.x*block_px
                pos_y_px = block.position.y*block_px
                chunk_texture_image.paste(Image.open("textures/blocks/"+block.texture.name),(int(pos_x_px),int(-pos_y_px)))
        tex = Texture(chunk_texture_image)
        return tex


    #GENERATE THE GROUND BLOCKS IN THE CHUNK.
    def generate_blocks(self):
        #GO THROUGH ALL THE COLUMNS OF BLOCKS.
        for x in range(int(self.CHUNK_SIZE)):
            # MAX SURFACE HEIGHT IS 3 METERS ABOVE THE LOWEST POINT.
            surface_y = 3 * noise2(x=(x + self.world_position.x) * 0.1, y=0)
            blocks_x = []
            blocks_x_cords = []

            #GO THROUGH ALL THE BLOCKS IN THE COLUMN.
            for y in range(int(self.CHUNK_SIZE)):
                #GET THE BLOCK COORDINATE.
                block_cords = Vec2(x, -y)
                #IF THE BLOCK IS UNDER THE MAX HEIGHT OF THE WORLD IT CAN BE A GROUND BLOCK - ELSE IT'S JUST AIR.
                if block_cords.y+self.world_position.y < surface_y:
                    #MOST BLOCKS ARE UNDER SURFACE BLOCKS, NOT ORE NOR SURFACE. WE ASSUME THIS IS THE CASE.
                    block_type = "under_surface_block"

                    #IF IT IS SURFACE BLOCK - CHANGE BLOCK TYPE TO SURFACE BLOCK.
                    if 0 <= surface_y - (block_cords.y+self.world_position.y) <= 1:
                        block_type = "surface_block"
                    
                    #IF SURFACE OR UNDER SURFACE - SET THE CORRESPONDING INFORMATION ABOUT THE BLOCK.
                    item_obj_data=Chunk._biomes[self.CHUNK_TYPE]["block_types"][block_type]["dropped_resource"]
                    texture = Chunk._biomes[self.CHUNK_TYPE]["block_types"][block_type]["texture"]
                    
                    #IF IT IS AN ORE, SET THE CORRESPONDING ORE INFORMATION ABOUT THE BLOCK.
                    if random.uniform(0,1)<=chance_for_ore_based_on_y(y=(block_cords.y+self.world_position.y)):
                        block_type = random.choice(list(Chunk._biomes[self.CHUNK_TYPE]["block_types"]["ores"].keys()))
                        item_obj_data=Chunk._biomes[self.CHUNK_TYPE]["block_types"]["ores"][block_type]["dropped_resource"]
                        texture = Chunk._biomes[self.CHUNK_TYPE]["block_types"]["ores"][block_type]["texture"]

                    # SPAWN IN THE BLOCK - IT CAN DROP ITEMS IF DESTROYED - HENCE DEADDROPPINGENTITY.
                    block = DeadDroppingEntity(
                        position=block_cords,
                        texture=texture,
                        item_obj_data=item_obj_data,
                        chunk_ents=self.entities,
                        _parent=self.ground_entity,
                        collider_enabled=True,
                        collider_scale=Vec3(1,1,0),
                        model="quad",
                        origin=(0,0),
                        visible=False
                    )
                    #APPEND THE BLOCK AND IT'S COORDINATE.
                    blocks_x.append(block)
                    blocks_x_cords.append(copy.copy(block.position))
            #STORE THE GROUND BLOCK.
            self.ground_entity.ground_blocks_entities.append(blocks_x)
            self.ground_block_positions.append(blocks_x_cords)


    #GENERATE ANY FOLIAGE THAT CAN BE ON THE SURFACE.
    def generate_foliage(self):
        #GET INFO ABOUT THE FOLIAGES.
        foliage_chances = [Chunk._biomes[self.CHUNK_TYPE]["foliage"][foliage_name]["spawn_rate"] for foliage_name in Chunk._biomes[self.CHUNK_TYPE]["foliage"]]
        foliage_names = list(Chunk._biomes[self.CHUNK_TYPE]["foliage"].keys())

        #GO THROUGH EACH SURFACE BLOCK X POSITION.
        for x in range(self.CHUNK_SIZE): 
            #GET WHICH FOLIAGE TO SPAWN.
            chosen_foliage_name = random.choices(foliage_names + [""], foliage_chances + [1 - sum(foliage_chances)], k=1)[0]

            #IF THE TOP BLOCK IS THE SURFACE BLOCK OF SURFACE CHUNK.
            if self.CHUNK_SIZE>len(self.ground_entity.ground_blocks_entities[x])>=1:
                
                #IF NO FOLIAGE CHOSEN - SKIP TO NEXT X POSITION.
                if chosen_foliage_name=="":
                    continue

                #GET INFO ABOUT THE CHOSEN FOLIAGE.
                plant_obj = Chunk._biomes[self.CHUNK_TYPE]["foliage"][chosen_foliage_name]
                spawn_y = self.ground_entity.ground_blocks_entities[x][0].world_position.y+0.5*plant_obj["size_y"]+1.5*self.ground_entity.ground_blocks_entities[x][0].scale_y
                spawn_x = self.ground_entity.ground_blocks_entities[x][0].world_position.x
                
                #SPAWN THE FOLIAGE. - IT DROPS ITEMS HENCE DEADDROPPINGENTITY.
                plant = DeadDroppingEntity(
                    model="quad",
                    texture=plant_obj["texture"],
                    world_position=Vec3(spawn_x,spawn_y,random.uniform(0.11,0.00000001)),
                    _parent=self,
                    chunk_ents=self.entities,
                    item_obj_data=plant_obj["dropped_resource"],
                    scale_x=plant_obj["size_x"],
                    scale_y=plant_obj["size_y"],
                    health=plant_obj["health"],
                    double_sided=True,
                    origin=(0,-plant_obj["size_y"]/2),
                    collider_enabled=True,
                    collider_scale=Vec3(plant_obj["size_x"]*2,plant_obj["size_y"]*1.5,0),
                    intersects_with_player=False
                )
                
                #APPEND THE ENTITY TO THE WORLD.
                self.entities.append(plant)

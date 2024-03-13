from ursina import Sprite, Entity, Texture
from ursina.ursinamath import Vec2, Vec3
from opensimplex import noise2
import json
from numpy import array
from PIL import Image

"""
Each chunk consists of two parts.
One part is the actual chunk, this is what gets rendered.
The other part is the block data, this is what the chunk consists of.
The individual blocks do not get drawn individually, but help build one big chunk which then gets drawn.
"""

class Chunk(Entity):
    _biomes = json.load(open("scripts/world/biomes.json", "r"))

    def __init__(self, top_left_position: Vec2, chunk_size=12, **kwargs):
        self.entities = []
        self.CHUNK_SIZE = chunk_size
        self.ground_blocks_entities = []
        self.background_blocks = []
        super().__init__(eternal=True)
        self.position = top_left_position
        self.CHUNK_TYPE = list(self._biomes.keys())[
            int(
                round(
                    noise2(self.position.x * 0.01, self.position.y * 0.0001)
                    * len(self._biomes.keys())
                )
            )
        ]
        self.generate_blocks()
        self.combine(ignore=self.entities+self.background_blocks)
        self.collider = "mesh"
        self.texture = self.generate_ground_chunk_texture()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def generate_ground_chunk_texture(self):
        """
        When combining all the different blocks into one entity, we lose the data for the respective textures.
        So in this function we just generate it and apply it ourselves! Quick and easy!
        """
        texture = Texture("")
        for block in self.ground_blocks_entities:
            
        return texture
        

    def generate_blocks(self):
        for x in range(int(self.CHUNK_SIZE)):
            # Surface height.
            surface_y = 3 * noise2(x=(x + self.position.x) * 0.1, y=0)
            for y in range(int(self.CHUNK_SIZE)):
                block_cords = Vec2(x, -y)
                if block_cords.y + self.position.y < surface_y:
                    # If we are in the ground, we set the ground texture.
                    texture = self._biomes[self.CHUNK_TYPE]["block_textures"][
                        "under_surface_block"
                    ]
                    # If top block, such as grass block, we set that.
                    if 0 <= surface_y - (block_cords.y + self.position.y) <= 1:
                        texture = self._biomes[self.CHUNK_TYPE]["block_textures"][
                            "surface_block"
                        ]
                    # Spawn in the block, and store it into ground blocks.
                    block = Entity(
                        position=block_cords,
                        parent=self,
                        model="quad",
                        texture=texture,
                    )
                    self.ground_blocks_entities.append(block)

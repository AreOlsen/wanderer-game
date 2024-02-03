from ursina import Sprite, Entity
from ursina.ursinamath import Vec2
from opensimplex import noise2


class Chunk(Entity):
    def __init__(self, top_left_position: Vec2, chunk_size=8, **kwargs):
        self.entities = []
        self.CHUNK_SIZE = chunk_size
        self.ground_blocks_entities = []
        super().__init__()
        self.position = top_left_position
        self.generate_blocks()

        for key, value in kwargs.items():
            setattr(self, key, value)

    def generate_blocks(self):
        for x in range(int(self.CHUNK_SIZE)):
            surface_y = 3 * noise2(x=(x + self.position.x) * 0.1, y=0)
            for y in range(int(self.CHUNK_SIZE)):
                block_cords = Vec2(x, -y)
                if block_cords.y + self.position.y < surface_y:
                    texture = "textures/blocks/414.png"
                    if 0 <= surface_y - (block_cords.y + self.position.y) <= 1:
                        texture = "textures/blocks/400.png"
                    block = Entity(
                        position=block_cords,
                        parent=self,
                        model="quad",
                        texture=texture,
                        collider="box",
                    )
                    self.ground_blocks_entities.append(block)

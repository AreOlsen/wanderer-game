import pickle
from ursina.ursinamath import Vec2
from ursina import Entity, camera
from scripts.world.chunk import Chunk
import opensimplex
import math


class World(Entity):
    def __init__(self, chunk_size=8):
        self.all_chunks = {}
        self.CHUNK_SIZE = chunk_size
        self.loaded_chunks_indices = []
        opensimplex.random_seed()
        super().__init__()

    def save_world(self, name):
        with open(f"{name}.pickle", "wb") as handle:
            pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_world(self, name):
        with open(f"{name}.pickle", "rb") as handle:
            self = pickle.load(handle)

    def pos_to_chunk_indices(self, pos: Vec2) -> Vec2:
        return Vec2(
            math.floor(pos.x / self.CHUNK_SIZE), math.floor(pos.y / self.CHUNK_SIZE)
        )

    def load_chunks(self):
        # Enable all chunks which are in render view.
        # We calculate the number of chunks to load in x and y.
        count_x = (
            int(
                math.ceil(
                    2
                    * abs(camera.position.z)
                    * abs(math.tan(math.radians(camera.fov_getter() / 2)))
                    - self.CHUNK_SIZE
                )
                / (2 * self.CHUNK_SIZE)
            )
            * 2
            + 2
        )
        count_y = math.ceil(camera.aspect_ratio_getter() / count_x) + 3
        # We get the individual chunks from the counts and the cam position.
        cam_pos_indices = self.pos_to_chunk_indices(camera.position)
        new_loaded_chunk_indices = []
        for x in range(-count_x // 2, count_x // 2 + 1):
            for y in range(-count_y // 2, count_y // 2 + 1):
                chunk_indices = Vec2(cam_pos_indices.x + x, cam_pos_indices.y + y)
                new_loaded_chunk_indices.append(chunk_indices)
                if chunk_indices in self.all_chunks.keys():
                    self.all_chunks[chunk_indices].enabled = True
                else:
                    self.all_chunks[chunk_indices] = Chunk(
                        self.CHUNK_SIZE * chunk_indices, self.CHUNK_SIZE
                    )

        # Reset which chunks are loaded in rn.
        # Get difference in cur loaded chunks and the new ones, we disable the unloaded ones.
        for index in list(
            set(self.loaded_chunks_indices) - set(new_loaded_chunk_indices)
        ):
            self.all_chunks[index].enabled = False

        # Set the current loaded chunk indices for next iteration.
        self.loaded_chunks_indices = new_loaded_chunk_indices

        # This greatly increases the frame rate.

    def update(self):
        self.load_chunks()

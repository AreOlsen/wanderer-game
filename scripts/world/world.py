import pickle
from ursina.ursinamath import Vec2
from ursina import Entity, camera, destroy, time
from scripts.world.chunk import Chunk
import opensimplex
import math
import asyncio
import os
import copy


class World(Entity):
    def __init__(self, save_name, chunk_size=12, save_frequency=3*60, seed=0, difficulty = "Easy"):
        self.all_chunks = {}
        self.CHUNK_SIZE = chunk_size
        self.all_chunks_indices = []
        super().__init__()
        self.save_name = save_name
        self.save_frequency = save_frequency
        self.time_to_next_save = min(10,save_frequency)
        self.seed=seed
        opensimplex.seed(self.seed)
        self.difficulty = difficulty


    def save_world(self):
        with open(f"data/world_saves/{self.save_name}.pickle", "wb") as handle:
            pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_world(self):
        with open(f"data/world_saves/{self.save_name}.pickle", "rb") as handle:
            self = pickle.load(handle)

    def pos_to_chunk_indicies(self, pos: Vec2) -> Vec2:
        return Vec2(
            math.floor(pos.x / self.CHUNK_SIZE), math.floor(pos.y / self.CHUNK_SIZE)
        )

    def load_chunks(self):
        # Enable all chunks which are in render view.
        # We calculate the number of chunks to load in x and y.
        count_x = int(
            math.ceil(
                2
                * abs(camera.position.z)
                * abs(math.tan(math.radians(camera.fov / 2)))
                / self.CHUNK_SIZE
            )
        )
        count_y = int(math.ceil(camera.aspect_ratio_getter() / count_x) + 1)
        # We get the individual chunks from the counts and the cam position.
        cam_pos_indices = self.pos_to_chunk_indicies(camera.position)
        new_loaded_chunk_indicies = []
        # Go through all the currently loaded chunks.
        for x in range(-int(math.floor(count_x / 2)), int(math.ceil(count_x / 2)) + 1):
            for y in range(
                -int(math.floor(count_y / 2)), int(math.ceil(count_y / 2)) + 1
            ):
                # Get the current chunk indices.
                chunk_indicies = Vec2(cam_pos_indices.x + x, cam_pos_indices.y + y)
                # Currently loaded chunks.
                new_loaded_chunk_indicies.append(chunk_indicies)
                # If the chunk exists but we ensure it is enabled.
                if chunk_indicies in self.all_chunks.keys():
                    self.all_chunks[chunk_indicies].enabled = True
                # If the chunk hasn't been made.
                else:
                    self.all_chunks[chunk_indicies] = Chunk(
                        self.CHUNK_SIZE * chunk_indicies, self.CHUNK_SIZE
                    )

        # Some of the old chunks may get unloaded, so we disable those.
        # This is the difference between the previous frame's loaded chunks, and the current new loaded chunks.
        for chunk_indicies in list(
            set(self.all_chunks_indices).symmetric_difference(
                set(new_loaded_chunk_indicies)
            )
        ):
            self.all_chunks[chunk_indicies].enabled = False

        # Set the current loaded chunk indices for next iteration.
        self.all_chunks_indices = new_loaded_chunk_indicies

    def update(self):
        self.time_to_next_save-=time.dt
        self.load_chunks()
        #AUTOMATIC SAVE OF WORLD - EACH SAVE_FREQUENCY SECONDS.
        if self.time_to_next_save<0:
            self.time_to_next_save=self.save_frequency
            self.save_world()

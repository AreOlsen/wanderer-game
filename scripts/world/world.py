import pickle
from ursina.ursinamath import Vec2
from ursina import Entity, camera, destroy, time
from scripts.world.chunk import Chunk
import opensimplex
import math

### 
# WORLD OBJECT.
###
class World(Entity):
    #INIT THE WORLD OBJECT AND ANYTHING RELATED TO IT.
    def __init__(self, save_name, background, chunk_size=12, save_frequency=3*60, seed=0, difficulty = "Easy"):
        self.all_chunks = {}
        self.CHUNK_SIZE = chunk_size
        self.all_chunks_indices = []
        super().__init__()
        self.save_name = save_name
        self.save_frequency = save_frequency
        self.time_to_next_save = min(10,save_frequency)
        self.seed=seed
        self.background=background
        opensimplex.seed(self.seed)
        self.difficulty = difficulty
        self.preload_chunks(6)

    
    #SAVE THE WORLD TO FILE.
    def save_world(self):
        with open(f"data/world_saves/{self.save_name}.pickle", "wb") as handle:
            pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)


    #LOAD THE WORLD IN FROM FILE.
    def load_world(self):
        with open(f"data/world_saves/{self.save_name}.pickle", "rb") as handle:
            self = pickle.load(handle)


    #FUNCTION FOR CONVERTING A WORLD POSITION INTO THE CORRECT CHUNK INDEX.
    def pos_to_chunk_indicies(self, pos: Vec2) -> Vec2:
        return Vec2(
            math.floor(pos.x / self.CHUNK_SIZE), math.floor(pos.y / self.CHUNK_SIZE)
        )


    #LOAD IN ALL THE CHUNKS WHICH ARE IN RENDER VIEW.
    def load_chunks(self):
        #CALCULATE THE NUMBER OF CHUNKS IN X DIRECTION IN RENDER VIEW.
        count_x = int(
            math.ceil(
                2
                * abs(camera.position.z)
                * abs(math.tan(math.radians(camera.fov / 2)))
                / self.CHUNK_SIZE
            )
        )

        #GET THE NUMBER OF CHUNKS IN Y DIRECTION RENDERED FROM X CHUNK DIRECTION COUNT.
        count_y = int(math.ceil(camera.aspect_ratio_getter() / count_x) + 1)


        #GET THE CAMERA'S CHUNK INDEX. 
        #THIS IS THE CENTER CHUNK IN RENDER VIEW - COUNT_X AND COUNT_Y IS USED AS OFFSETS FROM THIS CHUNK INDEX.
        cam_pos_indices = self.pos_to_chunk_indicies(camera.position)
        
        #OPTIMIZATION: BY CHECKING FOR THE NEWLY LOADED CHUNKS IN THIS FRAME, WE DONT HAVE TO LOAD THE PREVIOUS FRAME CHUNKS IN.
        new_loaded_chunk_indicies = []

        #GO THROUGH ALL THE LOADED CHUNKS.
        for x in range(-int(math.floor(count_x / 2)), int(math.ceil(count_x / 2)) + 1):
            for y in range(
                -int(math.floor(count_y / 2)), int(math.ceil(count_y / 2)) + 1
            ):
                #GET THE CURRENT CHUNK INDEX BEING LOADED. 
                chunk_indicies = Vec2(cam_pos_indices.x + x, cam_pos_indices.y + y)
                
                #SET INTO THE NEWLY LOADED CHUNKS.
                new_loaded_chunk_indicies.append(chunk_indicies)
                
                #IF THE CHUNK'S DATA ALREADY EXISTS - WE ENABLE THE CHUNK.
                if chunk_indicies in self.all_chunks.keys():
                    self.all_chunks[chunk_indicies].enable()
                #ELSE CREATE THE CHUNK DATA FOR THE FIRST TIME.
                else:
                    self.all_chunks[chunk_indicies] = Chunk(
                        chunk_pos=chunk_indicies,
                        top_left_world_position=self.CHUNK_SIZE * chunk_indicies, chunk_size=self.CHUNK_SIZE, world=self
                    )

        #UNLOAD ALL THE CHUNKS WHICH AREN'T IN THE CURRENT FRAME.
        for chunk_indicies in list(
            set(self.all_chunks_indices).symmetric_difference(
                set(new_loaded_chunk_indicies)
            )
        ):
            self.all_chunks[chunk_indicies].disable()

        #SET THIS FRAME'S CHUNKS AS THE PREVIOUS CHUNKS FOR THE NEXT FRAME.
        self.all_chunks_indices = new_loaded_chunk_indicies


    #PRELOAD ALL THE CHUNKS AROUND POINT (0,0) - WORLD CENTRE.
    def preload_chunks(self, radius_chunks):
        for x in range(-int(math.floor(radius_chunks / 2)), int(math.ceil(radius_chunks / 2)) + 1):
            for y in range(-int(math.floor(radius_chunks / 2)), int(math.ceil(radius_chunks / 2)) + 1):
                #GET CHUNK INDEX.
                chunk_indicies = Vec2(x, y)
                
                #GENERATE THE CHUNK DATA.
                self.all_chunks[chunk_indicies] = Chunk(
                        chunk_pos=chunk_indicies,
                        top_left_world_position=self.CHUNK_SIZE * chunk_indicies, chunk_size=self.CHUNK_SIZE, world=self
                    )
                #DISABLE them AS ALL OF THEM WON'T BE IN RENDER VIEW INSTANTLY.
                self.all_chunks[chunk_indicies].disable()


    #UPDATE THE WORLD.
    def update(self):
        self.time_to_next_save-=time.dt
        self.load_chunks()
        #AUTOMATIC SAVE OF WORLD - EACH SAVE_FREQUENCY SECONDS.
        if self.time_to_next_save<0:
            self.time_to_next_save=self.save_frequency
            self.save_world()

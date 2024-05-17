from ursina import camera, Entity, rgb, window, Texture
from ursina.ursinamath import Vec3,Vec2
import numpy as np
from PIL import Image



###
# MINIMAP ENTITY.
# SHOWS THE SURROUNDING CHUNKS BLOCK POSITIONS.
###
class Minimap(Entity):
    #THE MINIMAP BLOCK COLOUR.
    _MINIMAP_COLOUR = (30,41,55,255)
    
    #INIT THE MINIMAP.
    def __init__(self, player):
        super().__init__()
        self.model = "quad"
        self.texture = "textures/hud/mini_map.png"
        self.parent = camera.ui
        self.scale = 0.25
        self.offset_x = 0.15
        self.offset_y = 0.15
        self.map_chunks_diameter = 5
        self.player = player
        self.position = Vec2(window.left.x + self.offset_x, window.top.y - self.offset_y)
        self.origin=(0,0)
        
        #SPAWN IN THE ENTITY HOLDING THE CHUNKS' BLOCKS' DATA.
        self.map = Entity(scale=self.scale*2.3, parent=self, model="quad", position=(0,0,0-1),texture="", enabled=True)

        #ONLY NEED TO UPDATE MINIMAP ON NEW CHUNK LOADING.
        self.prev_mid_chunk_indicies = Vec2(1000,1000)


    #UPDATE THE MINIMAP.
    def update(self):
        #GET THE MID CHUNK OF THE MINIMAP.
        mid_chunk_indicies = self.player.world.pos_to_chunk_indicies(self.player.world_position)

        #ONLY NEED TO UPDATE THE MINIMAPS' BLOCKS AT NEW CHUNKS LOADED.
        if mid_chunk_indicies!=self.prev_mid_chunk_indicies and mid_chunk_indicies in list(self.player.world.all_chunks.keys()):
            #GENERATE THE MINIMAP TEXTURE.
            map_texture = Image.new(mode="RGBA", size=(self.map_chunks_diameter*self.player.world.CHUNK_SIZE,self.map_chunks_diameter*self.player.world.CHUNK_SIZE),color=(0,0,0,0))

            #GO THROUGH EACH CHUNK.
            for top_left_chunk_x in range(self.map_chunks_diameter):
                for top_left_chunk_y in range(self.map_chunks_diameter):
                    #GET INFO ABOUT CURRENT CHUNK AND SURROUNDING CHUNKS.
                    top_left_chunk_pos = Vec2(top_left_chunk_x*self.player.world.CHUNK_SIZE,top_left_chunk_y*self.player.world.CHUNK_SIZE)
                    chunk_indicies = mid_chunk_indicies+Vec2(top_left_chunk_x-(self.map_chunks_diameter-1)/2,top_left_chunk_y-(self.map_chunks_diameter-1)/2)
                    #IF ANY INFORMATION LOAD IT IN.
                    if chunk_indicies in list(self.player.world.all_chunks.keys()):
                        #GET ALL BLOCK POSITIONS FROM THE CHUNK.
                        for block_x_column in self.player.world.all_chunks[chunk_indicies].ground_block_positions:
                            for block_coords in block_x_column:
                                #PLACE THE BLOCK ON THE MINIMAP.
                                try:
                                    pixel_coords=(int(max(0, min(top_left_chunk_pos.x+block_coords.x, map_texture.width))),int(max(0,min(map_texture.height,map_texture.height-(top_left_chunk_pos.y+block_coords.y)))))
                                    map_texture.putpixel(xy=pixel_coords, value=Minimap._MINIMAP_COLOUR)
                                except Exception:
                                    continue

            #CREATE THE MINIMAP FROM THE PLOTTED BLOCK PIXELS.
            map_texture = Texture(map_texture)
            self.map.texture=map_texture
            self.prev_mid_chunk_indicies=mid_chunk_indicies

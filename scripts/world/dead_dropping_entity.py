from ursina import Entity, BoxCollider, destroy
from ursina.ursinamath import Vec2, Vec3
from scripts.moving_object import MovingObject
import copy


###
# DEAD DROPPING ENTITY - TREES, ORES, ETC. - NOT "LIVING" ENEMIES, BUT STILL DROPS ITEMS AT "HEALTH" BELOW 0.
###
class DeadDroppingEntity(Entity):
    #INIT THE DEAD DROPPING ENTITY.
    #SOME HAVE COLLIDERS, SOME INTERSECTS WITH PLAYER - DIFFERENT FORMS OF DEAD DROPPING ENTITY EXISTS.
    def __init__(self,
    _parent,
    texture,
    item_obj_data,
    chunk_ents,
    collider_enabled=False,
    collider_scale=Vec3(0,0,0),
    collider_center_offset=Vec3(0,0,0),
    intersects_with_player=True,
    scale_x=1,
    scale_y=1,
    health=250,
    **kwargs):
        #INIT BASE ENTITY CLASS.
        super().__init__(
                        parent=_parent,
                        model="quad",
                        texture=texture,
                        scale_x=scale_x,
                        scale_y=scale_y
                    )
        #STORE DATA FOR THE DROPPED ITEM.
        self.item_obj_data = item_obj_data
        #HEALTH.
        self.health = health
        #GET REFERENCE TO THE ENTITIES IN THE CHUNK.
        self.chunk_ents = chunk_ents
        #SOME COLLIDE WITH THE PLAYER, SOME DON'T.
        self.intersects_with_player=intersects_with_player
        #INIT ALL OTHER PROPERTIES NOT IN THE PARAMETER.
        for key, val in kwargs.items():
            setattr(self,key,val)
        #IF THERE IS A COLLIDER - ENABLE IT.
        if collider_enabled:
            self.collider = BoxCollider(self,center=collider_center_offset,size=collider_scale)


    #UPDATE - CHECK IF THE ENTITY HAS DIED -> DROP ENTITY THEN.
    def update(self):
        if self.health<=0:
            self._destroy()
        

    #DESTROY THE ENTITY. THIS DROPS THE ITEM, AND REMOVES THIS ENTITY FROM THE WORLD.
    def _destroy(self):
        #ADD DROPPED ENTITY TO THE WORLD.
        dropped_item = MovingObject(
                texture=copy.copy(self.item_obj_data["texture"]),
                scale_y=copy.copy(self.item_obj_data["scale"][1]),
                scale_x=copy.copy(self.item_obj_data["scale"][0]),
                item_type=copy.copy(self.item_obj_data["name"]),
                num_items=1,
                item_data=copy.copy(self.item_obj_data),
                description=copy.copy(self.item_obj_data["description"]),
                enabled=True,
                collides=True,
                model="quad",
                collider="box",
                world_position=Vec3(copy.copy(self.world_position.x),3,0),
                gravity=-2,
                parent_on_hit=False
            )
        #ADD DROPPED ENTITY TO THE CURRENT CHUNK ENTITIES.
        self._parent.entities.append(
            dropped_item
        )
        #REMOVE THE DEAD DROPPING ENTITY FROM THE WORLD.
        self.chunk_ents.remove(self)
        destroy(self)
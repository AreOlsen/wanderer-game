from ursina import Entity, BoxCollider
from ursina.ursinamath import Vec2, Vec3
from scripts.moving_object import MovingObject

class DeadDroppingEntity(Entity):
    def __init__(self,
    _parent,
    texture,
    item_obj_data,
    collider_enabled=False,
    collider_scale=Vec3(0,0,0),
    collider_center_offset=Vec3(0,0,0),
    scale_x=1,
    scale_y=1,
    **kwargs):
        super().__init__(
                        parent=_parent,
                        model="quad",
                        texture=texture,
                        scale_x=scale_x,
                        scale_y=scale_y
                    )
        self.item_obj_data = item_obj_data
        if collider_enabled:
            self.collider = BoxCollider(self,center=collider_center_offset,size=collider_scale)
    
        for key, val in kwargs.items():
            setattr(self,key,val)

        
    def _destroy(self):
        dropped_item = MovingObject(
                texture=self.item_obj_data["texture"],
                scale_y=self.item_obj_data["size_y"],
                scale_x=self.item_obj_data["size_x"],
                enabled=True,
                position=Vec3(0,0,-0.001),
                collides=True,
                parent=self._parent
            )
        dropped_item.collider = BoxCollider(dropped_item,center=Vec3(0,0,0),size=Vec3(self.item_obj_data["size_x"],self.item_obj_data["size_y"],0))
        self.parent.entities.append(
            dropped_item
        )
        
        self.destroy()
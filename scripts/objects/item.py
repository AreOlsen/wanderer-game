from ursina import Entity, mouse, time, held_keys, destroy, BoxCollider, curve, color, Sequence, Wait, Func, camera,scene
from ursina.ursinamath import Vec3,Vec2, distance
import math
from scripts.moving_object import MovingObject
import numpy as np
import copy



###
# HOLDING ITEM CLASS - THIS IS BASE OBJECT THE PLAYER "HOLDS" WHEN HAVING SELECTED AN ITEM.
###
class HoldingItem(Entity):
    #INIT THE HOLDING ITEM CLASS.
    def __init__(self, texture:str, offset:Vec3, inventory_slot, player, min_angle=0, max_angle=360, size=[0.1,0.1,0], **kwargs):
        super().__init__(
            model="quad",
            texture=texture,
            parent=player,
            double_sided=True,
        )
        #INFO ABOUT THE HOLDING ITEM CLASS. 
        #SOME CAN HAVE ANGLES - SOME NOT.
        self.min_angle=min_angle
        self.max_angle=max_angle
        self.inventory_slot=inventory_slot
        self.time_since_used = 0
        self.parent=player
        self.position=Vec3(0+offset[0],0+offset[1],-0.1+offset[2])
        self.scale=Vec3(size[0],size[1],size[2])
        #ANY EXTRA PROPERTIES NOT PRESENTED IN THE PARAMETERS.
        for key, val in kwargs.items():
            setattr(self, key, val)


    #UPDATE THE OBJECT.
    def update(self):
        self.time_since_used+=time.dt
        self.reset_slot_check()

    
    #CALCULATE THE ANGLE OF THE ITEM.
    def calculate_angle_item(self):
        delta = mouse.position - self.screen_position
        angle=0
        self.scale=Vec3(np.sign(self.parent.scale.x)*abs(self.scale.x),np.sign(self.parent.scale.x)*abs(self.scale.y),self.scale.z)
        if delta.x!=0:
            angle = (math.atan2(delta.y, delta.x) * 180 / math.pi + 360) % 360 
        if 90<=angle<=270 and np.sign(self.parent.scale.x)==1:
            angle-=90
            self.scale=Vec3(np.sign(self.parent.scale.x)*abs(self.scale.x),-np.sign(self.parent.scale.x)*abs(self.scale.y),self.scale.z)
        elif np.sign(self.parent.scale.x)==-1 and (270<=angle<=360 or 0<=angle<=90):
            angle+=90
            self.scale=Vec3(-abs(self.scale.x),abs(self.scale.y),self.scale.z)     
        if self.parent.scale.x<0:
            angle=-angle
        return angle
    
    #DELETE THE HOLDING ITEM IF THE INVENTORY DOESN'T SELECT THE ITEM ANYMORE.
    def reset_slot_check(self):
        if self.inventory_slot.num_items_slot<=0:
            self.inventory_slot.item_type=""
            self.inventory_slot.category=""
            self.inventory_slot.description=""
            self.inventory_slot.item_data={}
            self.inventory_slot.num_items_slot=0
            self.inventory_slot.num_items_slot_text.text="0"
            destroy(self.inventory_slot.visualizer_entity)
            destroy(self)


    #USE THE ITEM IN THE INVENTORY. 
    #FOR EXAMPLE: STEAK CAN BE USED IN THE INVENTORY AND EATEN FOR HEALTH.
    def use_inv_inventory(self):
        self.inventory_slot.num_items_slot-=1
        self.inventory_slot.num_items_slot_text.text=f"{self.inventory_slot.num_items_slot}"
        self.reset_slot_check()


###
# FOOD CLASS.
###
class Food(HoldingItem):
    #INIT THE FOOD HOLDING ITEM.
    def __init__(self, texture, offset, inventory_slot, min_angle, max_angle, size, hp_increase, player):
        super().__init__(texture=texture,offset=offset,inventory_slot=inventory_slot,min_angle=min_angle,max_angle=max_angle,size=size, player=player)
        self.player = player
        self.hp_increase = hp_increase

    #IF THE FOOD IS EATEN UPDATE THE PLAYER'S HEALTH.
    def input(self,key):
        if key=="e" and self.time_since_used>=1:
            self.time_since_used=0
            self.player.health+=self.hp_increase
            self.use_inv_inventory()


### 
# HANDHELD WEAPON CLASS. 
# THIS IS AXES, SWORDS, ETC.
###
class HandheldWeapon(HoldingItem):
    #INIT THE HANDHELD WEAPON.
    def __init__(self, texture, offset, inventory_slot, min_angle, max_angle, size, attack_range, swing_time, swing_reload_time, attack_damage,player, rotation_max=60):
        super().__init__(texture=texture,offset=offset,inventory_slot=inventory_slot,min_angle=min_angle,max_angle=max_angle, size=size, player=player)
        self.range = attack_range
        self.swing_time = swing_time
        self.time_since_last_swing = swing_reload_time
        self.swing_reload_time=swing_reload_time
        self.attack_damage=attack_damage
        self.rotation_max = rotation_max
        self.rotation_animation_val = 0
        self.player = player


    #CALCULATE THE ROTATION OF THE ITEM MATHEMATICALLY FOR SWINGING THE ITEM WHEN ATTACKING.
    def rotation_animation_val_update(self,x):
        self.rotation_animation_val+=time.dt*((2*self.rotation_max)/(self.swing_time**2))*x


    #UPDATE THE ITEM ON NEW FRAME.
    def update(self):
        #UPDATE TIME SINCE LAST SWING USING TIME FROM LAST FRAME.
        self.time_since_last_swing+=time.dt
        
        #PLAY MATHEMATICAL SWING ANIMATION.
        if self.time_since_last_swing<=self.swing_time:
            self.rotation_animation_val_update(self.time_since_last_swing)
        #RESET IF THE ANIMATION HAS ENDED.
        else:
            self.rotation_animation_val=0

        #PUT THE ANIMATION INTO ROTATION.
        self.rotation_z = -self.calculate_angle_item()+self.rotation_animation_val-45


    #CHECK IF THE ITEM IS ATTACKING.
    def input(self,key):
        #SWING.
        if key == "left mouse down" and self.time_since_last_swing>=self.swing_reload_time:
            self.time_since_last_swing=0
            #REMOVE HEALTH OF ANY OBJECT THAT HAS HEALTH.
            try:
                if hasattr(mouse.hovered_entity, "health") and mouse.hovered_entity!=self.player and distance(mouse.hovered_entity.world_position, self.world_position)<=self.range:
                    mouse.hovered_entity.health-=self.attack_damage
            except Exception:
                print("Error with swinging weapon.")



###
# GUN HOLDING CLASS.
# NOT IMPLEMENTED YET - USED IN NEXT UPDATE.
###
class Gun(HoldingItem):
    #INIT THE GUN HOLDING ITEM.
    def __init__(self, scale, texture, offset, inventory_slot, min_angle, max_angle, size, player, mag_size, reload_time, fire_rate_rps, bullet_scale, bullet_texture, bullet_offset, bullet_damage):
        super().__init__(texture,offset,inventory_slot,min_angle,max_angle,size)
        #GUN INFO.
        self.left_in_mag = mag_size
        self.mag_size = mag_size
        self.reload_time = reload_time
        self.fire_rate_rps = fire_rate_rps
        self.time_since_last_bullet = fire_rate_rps
        self.time_since_last_reload = reload_time
        #GENERAL INFO.
        self.player = player
        self.scale=scale
        self.texture=texture
        self.offset=offset
        self.position=offset
        #BULLET INFO.
        self.bullet_damage = bullet_damage
        self.bullet_texture = bullet_texture
        self.bullet_scale = bullet_scale


    #FIRE A BULLET FROM THE GUN.
    def fire_bullet(self):
        chunk_pos = self.player.world.pos_to_chunk_indicies(self.player.world_position)
        chunk_ents = self.player.world.all_chunks[chunk_pos].entities
        velocity_vector = (mouse.position-self.position)/(distance(mouse.position,self.position))*100
        #SPAWN THE BULLET.
        bullet = MovingObject(
            gravity=0,
            velocity=velocity_vector,
            collides=True,
            destroy_on_hit=True,
            damage_on_collision=self.bullet_damage,
            texture=self.bullet_texture,
            scale=self.bullet_scale,
            chunk_ents=chunk_ents)
        chunk_ents.append(bullet)


    #RELOAD THE GUN.
    def reload(self):
        self.time_since_last_reload=0
        self.left_in_mag = self.mag_size


    #UPDATE FRAME - CHECK IF FIRING GUN.
    def update(self):
        #UPDATE GENERAL INFO.
        self.time_since_last_bullet+=time.dt
        self.time_since_last_reload+=time.dt
        #IF FIRING GUN.
        if held_keys["left mouse down"] and self.time_since_last_reload>self.reload_time:
            if self.time_since_last_bullet>=self.fire_rate_rps:
                self.time_since_last_bullet=0
                self.fire_bullet()


    #WHEN PRESSING R RELOADING WILL BE ACTIVATED.
    def input(self,key):
        if key == "r":
            self.reload()



###
# BUILDING STRUCTURE HOLDING CLASS.
# USED FOR BUILDING THINGS.
###
class BuildingStructure(HoldingItem):
    #INIT THE BUILDING STUCTURE.
    def __init__(self, texture, offset, inventory_slot, min_angle, max_angle, size, player, health, building_range, building_data):
        super().__init__(texture=texture,offset=offset, inventory_slot=inventory_slot,min_angle=min_angle,max_angle=max_angle, size=size,player=player)
        self.player = player
        self.health = health
        self.building_range = building_range
        self.building_data = building_data
        #A VISUALIZER ENTITY WILL BE USED TO SHOW THE EVENTUAL PLACEMENT OF THE STRUCTURE.
        self.visualizer_building_entity = Entity(model="quad",
                                                texture=building_data["texture"],
                                                scale=Vec3(building_data["scale_x"],building_data["scale_y"],0),
                                                add_to_scene_entities=False,
                                                parent=scene)
        self.visualizer_building_entity.collider = BoxCollider(self.visualizer_building_entity,center=(0,0,0), size=self.scale)


    #UPDATE.
    def update(self):
        #NOT SHOWING IF INVENTORY IS OPEN.
        self.visualizer_building_entity.enabled = not self.player.inventory.big_menu.enabled
        #KEEP THE VISUALIZER ENTITY FAR AWAY FROM THE PLAYER.
        self.visualizer_building_entity.world_position = self.player.world_position+Vec3(np.sign(self.player.scale.x)*3,0,-1)


    #CHECK IF THE EVENTUAL PLACEMENT OF THE STRUCTURE IS LEGAL.
    def check_legal_placement(self):
        hit_info = self.visualizer_building_entity.intersects(ignore=(self,self.player))
        if hit_info.hit:
            return False
        return True
        

    #RESET THE SLOT - NEED TO REMOVE THE VISUALIZER.
    def reset_slot_check(self):
        super().reset_slot_check()
        if self.inventory_slot.num_items_slot<=0:
            destroy(self.visualizer_building_entity)

    
    #CHECK IF PLACING STRUCTURE.
    def input(self,key):
        if key=="e":
            #IF LEGAL PLACEMENT.
            placeable = self.check_legal_placement()
            if placeable:
                #GET CURRENT CHUNK.
                chunk_indicies = self.player.world.pos_to_chunk_indicies(self.player.world_position)
                chunk_ents = self.player.world.all_chunks[chunk_indicies].entities
                #BUILDING ENTITY.
                building = MovingObject(
                    model="quad",
                    scale_x=copy.copy(self.building_data["scale_x"]),
                    scale_y=copy.copy(self.building_data["scale_y"]),
                    texture=copy.copy(self.building_data["texture"]),
                    rotate=False,
                    collides=True,
                    player=self.player,
                    chunk_ents=chunk_ents,
                    gravity=-2,
                    velocity=Vec2(0,0),
                    health=copy.copy(self.building_data["health"]),
                    intersects_with_player=False)
                #SET POSITION OF BUILDING ENTITY.
                building.world_position=Vec3(self.visualizer_building_entity.world_position.x,6,0.001)
                #ADD TO CHUNK ENTITIES.
                chunk_ents.append(building)
                #USE THE INVENTORY ITEM UP.
                self.use_inv_inventory()


###
# GENERAL INVENTORYITEM.
# NOT CURRENTLY USED - MIGHT BE USED IN NEXT UPDATE.
###
class InventoryItem(HoldingItem):
    #INIT THE INVENTORYITEM.
    def __init__(self, **kwargs):
        super().__init__()
        #ANY PROPERTIES NOT IN THE PARAMETERES.
        for key, val in kwargs.items():
            setattr(self, key, val)

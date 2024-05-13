from ursina import Entity, mouse, time, held_keys, destroy, BoxCollider, curve, color
from ursina.ursinamath import Vec3, distance
import math
from scripts.moving_object import MovingObject

class HoldingItem(Entity):
    def __init__(self, texture:str, offset:Vec3, inventory_slot, min_angle=0, max_angle=360, size=0.1, **kwargs):
        super().__init__(
            texture=texture,
            size=size,
            position=Vec3(0,1,-0.001)+offset,
            double_sided=True,
        )
        self.min_angle=min_angle
        self.max_angle=max_angle
        self.inventory_slot=inventory_slot
        for key, val in kwargs.items():
            setattr(self, key, val)

    def calculate_angle_item(self):
        mos_pos = mouse.position
        delta = mos_pos - self.position
        angle = math.acos((delta.x)/((delta.x**2+delta.y**2+delta.z**2)**0.5))
        if angle<self.min_angle:
            angle=self.min_angle
        elif angle>self.max_angle:
            angle=self.max_angle
        return angle
    
    def use_inv_inventory(self):
        self.inventory_slot.num_items_slot-=1
        self.inventory_slot.num_items_slot_text.text=f"{self.inventory_slot.num_items_slot}"
        self.inventory_slot.visualizer_entity.num_items-=1
        self.inventory_slot.visualizer_entity.num_items_slot_text.text=f"{self.inventory_slot.visualizer_entity.num_items}"
        if self.inventory_slot.num_items_slot==0:
            destroy(self.inventory_slot.visualizer_entity)

class Food(HoldingItem):
    def __init__(self, texture, offset,min_angle, max_angle, size, hp_increase, player):
        super().__init__(texture,offset,min_angle,max_angle,size)
        self.player = player
        self.hp_increase = hp_increase

    def input(self,key):
        if key=="e":
            self.player.health+=self.hp_increase
            self.use_inv_inventory()


class HandheldWeapon(HoldingItem):
    """This is a handheld item."""
    def __init__(self, attack_range, swing_time, swing_reload_time, attack_damage, rotation_max=60):
        super().__init__()
        self.range = attack_range
        self.swing_time = swing_time
        self.time_since_last_swing = swing_reload_time
        self.swing_reload_time=swing_reload_time
        self.attack_damage=attack_damage
        self.rotation_max = rotation_max
        self.rotation_animation_val = 0

    def rotation(self,x):
        if 0<=x<=self.swing_time/3:
            self.rotation_animation_val-=time.dt*((-18/self.rotation_max/((self.swing_time)**2)) * x + 6*(self.rotation_max/self.swing_time))
        elif self.swing_reload_time/3<=x<=self.swing_reload_time*2/3:
            return
        elif self.swing_reload_time*2/3<=x<=self.swing_reload_time:
            self.rotation_animation_val+=time.dt*(3*self.rotation_max/self.swing_time)


    def update(self):
        self.time_since_last_swing+=time.dt
        
        #Play mathematical swing animation.
        if self.time_since_last_swing<=self.swing_time:
            self.rotation(self.time_since_last_swing)

        #Play animation.
        self.rotation.z = self.calculate_angle_item()+self.rotation_animation_val

    def input(self,key):
        if key == "left mouse down" and self.time_since_last_swing>=self.swing_reload_time:
            self.time_since_last_swing=0
            if hasattr(mouse.hovered_entity, "health"):
                mouse.hovered_entity.health-=self.attack_damage

                


class Gun(HoldingItem):
    """Gun, this can shoot."""
    def __init__(self, scale, texture, offset, mag_size, reload_time, fire_rate_rps, player, bullet_scale, bullet_texture, bullet_offset, bullet_damage):
        super().__init__()
        self.left_in_mag = mag_size
        self.mag_size = mag_size
        self.reload_time = reload_time
        self.fire_rate_rps = fire_rate_rps
        self.time_since_last_bullet = fire_rate_rps
        self.time_since_last_reload = reload_time
        self.player = player
        self.scale=scale
        self.texture=texture
        self.offset=offset
        self.parent=player
        self.position=offset
        self.bullet_damage = bullet_damage
        self.bullet_texture = bullet_texture
        self.bullet_scale = bullet_scale

    def fire_bullet(self):
        chunk_pos = self.player.world.pos_to_chunk_indicies(self.player.world_position)
        chunk_ents = self.player.world.all_chunks[chunk_pos].entities
        velocity_vector = (mouse.position-self.position)/(distance(mouse.position,self.position))*100
        bullet = MovingObject(gravity=0,velocity=velocity_vector,collides=True,destroy_on_hit=True,damage_on_collision=self.bullet_damage, texture=self.bullet_texture, scale=self.bullet_scale, chunk_ents=chunk_ents)
        chunk_ents.append(bullet)

    def reload(self):
        self.time_since_last_reload=0
        self.left_in_mag = self.mag_size


    def update(self):
        self.time_since_last_bullet+=time.dt
        self.time_since_last_reload+=time.dt
        if held_keys["left mouse down"] and self.time_since_last_reload>self.reload_time:
            if self.time_since_last_bullet>=self.fire_rate_rps:
                self.time_since_last_bullet=0
                self.fire_bullet()

    def input(self,key):
        if key == "r":
            self.reload()



class BuildingStructure(HoldingItem):
    def __init__(self, texture, health, scale, player, building_range, building_data):
        super().__init__()
        self.player = player
        self.health = health
        self.texture = texture
        self.scale = scale
        self.building_range = building_range
        self.building_data = building_data
        self.visualizer_building_entity = None
        self.visualizer_building_entity.collider = BoxCollider(self.visualizer_building_entity,center=(), size=self.scale)

    def check_legal_placement(self):
        hit_info = self.visualizer_building_entity.intersects(ignore=(self,self.player))
        if hit_info.hit:
            return False
        return True

    def update(self):
        self.visualizer_building_entity.position = mouse.position
            
    def input(self,key):
        if key=="left mouse down":
            placeable = self.check_legal_placement(self.visualizer_building_entity.position)
            if placeable and distance(self.player.world_position, self.visualizer_building_entity.world_position)<=self.building_range:
                chunk_indicies = self.player.world.pos_to_chunk_indicies(self.player.world_position)
                chunk_ents = self.player.world.all_chunks[chunk_indicies].entities
                building = MovingObject(texture=self.building_data["texture"], scale=self.building_data["scale"], rotate=False, collides=True,intersects_with_player=False,player=self.player,chunk_ents=chunk_ents, health=self.building_data["health"])
                building.collider = BoxCollider(building,center=(0,0), size=self.building_data["scale"])
                chunk_ents.append(building)


class InventoryItem(HoldingItem):
    def __init__(self, **kwargs):
        super().__init__()
        for key, val in kwargs.items():
            setattr(self, key, val)

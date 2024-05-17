from ursina import (
    held_keys,
    camera,
    Entity,
    duplicate,
    time,
    window,
    Sequence,
    Draggable,
    Func,
    Wait,
    BoxCollider,
    Text,
    color,
    mouse,
    destroy
)

from scripts.world.world import World
from scripts.moving_object import MovingObject
from ursina.ursinamath import Vec2, Vec3, distance
import json
import math
import numpy as np
import copy
import pickle
from scripts.world.chunk import Chunk

###
# INVENTORY SLOT ENTITY. THIS HOLDS ITEMS.
###
class InventorySlot(Entity):
    #INIT SLOT.
    def __init__(self,MAX_STACK_SIZE=16,**kwargs):
        #SLOT DATA.
        self.visualizer_entity = ""
        super().__init__()
        self.MAX_STACK_SIZE = MAX_STACK_SIZE
        self.num_items_slot = 0 
        self.item_type = ""
        self.item_data = {}

        #SLOT TEXT.
        self.num_items_slot_text = Text(f"{self.num_items_slot}", position=Vec3(-0.3,-0.3,-2.1), scale=10, origin=(0,0), parent=self)

        #ANY OTHER PROPERTIES WISHED FOR.
        for key, val in kwargs.items():
            setattr(self,key,val)


    #ON DISABLE - DISABLE THE VISUALIZER ENTITY AS WELL.
    def on_disable(self):
        if self.visualizer_entity!="":
            try:
                self.visualizer_entity.disable()
            except Exception:
                print("Couldn't disable visaulizer.")
        self.enabled=False


    #ON ENABLE - ENABLE THE VISUALIZER ENTITY AS WELL.
    def on_enable(self):
        if self.visualizer_entity != "":
            try:
                self.visualizer_entity.enable()
            except Exception:
                print("Couldn't enable visaulizer.")
        self.enabled=True


###
# INVENTORY ITEM.
# CLASS FOR THE VISUALIZER ENTITY.
# THIS SHOWS THE ITEM IN THE INVENTORY.
###
class InventoryItem(Draggable):
    #INIT THE INVENTORY ITEM.
    def __init__(self, slot_parent, inventory, texture, item_type, description, category, item_data, scale):
        super().__init__()
        #BASIC INIT.
        self.texture = texture
        self.item_type = item_type
        self.description = description
        self.slot_parent = slot_parent
        self.enabled=self.slot_parent.enabled
        self.parent=camera.ui
        self.world_position=self.slot_parent.world_position
        self.model="quad"
        self.inventory = inventory
        self.category=category,
        self.item_data=item_data
        self.time_since_split=0
        
        #NO HIGHLIGHT COLOUR.
        self.color = color.white
        self.highlight_color = color.white
        self.pressed_color = color.white
        
        #COLLIDER.
        self.scale = (scale,scale,0)

        #INFO ABOUT THE ITEM.
        self.info = Text(f"{self.item_type}\n{self.description}", position=Vec3(1,1,-2.1), scale=20, origin=(0,0), parent=self)
        self.info.enabled = False


    #ON DRAG - ORG_POS IS USED FOR REVERTING BACK TO INVENTORY SLOT WHEN THE ITEM IS NOT PLACED IN ANY SLOT.
    def drag(self):
        self.org_pos = (self.x,self.y,self.z)



    #TRADITIONAL COLLISION CHECK FOR INVENTORY SLOT.
    #CANNOT USED .intersects(), AS THIS WOULD MEAN ARROWS AND OTHER MOVINGOBJECTS COULD COLLIDE WITH THE INVENTORY.
    def check_traditional_collision(self,ent_2):
        #CALCULATE MINIMUM AND MAXIMUM FOR THE COLLISION.
        self_min_x = self.world_position.x - self.scale_x*5
        self_max_x = self.world_position.x + self.scale_x*5
        self_min_y = self.world_position.y - self.scale_y*5
        self_max_y = self.world_position.y + self.scale_y*5

        ent_2_min_x = ent_2.world_position.x - ent_2.scale_x*5
        ent_2_max_x = ent_2.world_position.x + ent_2.scale_x*5
        ent_2_min_y = ent_2.world_position.y - ent_2.scale_y*5
        ent_2_max_y = ent_2.world_position.y + ent_2.scale_y*5

        #CHECK FOR THE COLLISION.
        if (self_min_x <= ent_2_max_x and self_max_x >= ent_2_min_x) and \
            (self_min_y <= ent_2_max_y and self_max_y >= ent_2_min_y):
            return True
        else:
            return False


    #MOVE THE WHOLE INVENTORY ITEM TO ANOTHER SLOT.
    def move_to_slot(self,inventory_slot_chosen):
        #IF THE SLOT IS NOT EMPTY OR IT IS NOT THE CORRECT ITEM TYPE.
        if inventory_slot_chosen.item_type != "" and inventory_slot_chosen.item_type!=self.item_type:
            self.move_back()
        #IF THERE IS SPACE AVAILABLE IN THE SLOT.
        if inventory_slot_chosen.num_items_slot<inventory_slot_chosen.MAX_STACK_SIZE:
            #IF THE UPDATED SIZE IS UNDER THE MAXIMUM.
            if inventory_slot_chosen.num_items_slot+self.slot_parent.num_items_slot<=inventory_slot_chosen.MAX_STACK_SIZE:
                delete_self = False
                #UPDATE THE NEW INVENTORY SLOTS ITEM COUNT.
                #IF THERE IS NO VISUALIZER ENTITY THERE.
                if inventory_slot_chosen.num_items_slot==0:
                    inventory_slot_chosen.num_items_slot=copy.copy(self.slot_parent.num_items_slot)
                    inventory_slot_chosen.item_type=copy.copy(self.slot_parent.item_type)
                    inventory_slot_chosen.num_items_slot_text.text=f"{inventory_slot_chosen.num_items_slot}"
                    inventory_slot_chosen.item_data=copy.copy(self.slot_parent.item_data)
                    inventory_slot_chosen.visualizer_entity = self
                    self.slot_parent.num_items_slot = 0
                    self.slot_parent.num_items_slot_text.text="0"
                    self.slot_parent.visualizer_entity = ""
                    self.slot_parent.item_type=""
                    self.slot_parent.item_data={}
                    self.world_position=inventory_slot_chosen.world_position
                    self.slot_parent=inventory_slot_chosen
                #ELSE JUST ADD THE COUNT.
                else:
                    inventory_slot_chosen.num_items_slot+=self.slot_parent.num_items_slot
                    inventory_slot_chosen.num_items_slot_text.text=f"{inventory_slot_chosen.num_items_slot}"
                    self.slot_parent.num_items_slot = 0
                    self.slot_parent.num_items_slot_text.text="0"
                    delete_self = True
                #IF WE REQUIRE DELETING THIS INVENTORY ITEM.
                if delete_self:
                    destroy(self)
                return True
            else:
                self.move_back()
                return False
        else:
            self.move_back()
            return False


    #MOVE BACK TO THE ORIGINAL POSITION BEFORE DRAGGING.
    def move_back(self):
        self.position=self.org_pos
        

    #IF DROPPING THE ITEM FROM THE INVENTORY.
    def drop_item(self):
        #ADD THE DROPPED ITEM TO THE CHUNK ENTITIES.
        chunk_pos = self.inventory.player.world.pos_to_chunk_indicies(self.inventory.player.world_position)
        #SPAWN THE ITEM.
        item = MovingObject(model="quad",texture=copy.copy(self.texture),scale=0.5,velocity=Vec2(0,1),gravity=-4.905,collides=True,item_type=copy.copy(self.item_type), num_items=copy.copy(self.slot_parent.num_items_slot), description=copy.copy(self.description), item_data=copy.copy(self.item_data))
        item.world_position=Vec3(copy.copy(self.inventory.player.world_position.x), copy.copy(self.inventory.player.world_position.y)+1,copy.copy(self.inventory.player.world_position.z))
        self.inventory.player.world.all_chunks[chunk_pos].entities.append(item)
        #UPDATE SLOT DATA.
        self.slot_parent.num_items_slot=0
        self.slot_parent.item_type=""
        self.slot_parent.item_data={}
        self.slot_parent.num_items_slot_text.text = "0"
        destroy(self)


    #SPLIT THE ITEM - REMOVE ONE FROM THE INVENTORY SLOT COUNT AND MAKE IT INTO ONE OWN INVENTORY ITEM.
    def split_item(self):
        #LOOK FOR FREE SLOT.
        slot = self.inventory.find_free_slot()
        #NO SLOTS -> NO SPLITTING.
        if slot==None:
            return
        #SPLIT.
        if self.slot_parent.num_items_slot>1:
            self.slot_parent.num_items_slot-=1  
            self.slot_parent.num_items_slot_text.text=f"{self.slot_parent.num_items_slot}"
            slot.num_items_slot=1
            slot.num_items_slot_text.text="1"
            slot.item_type=self.slot_parent.item_type
            slot.item_data=self.slot_parent.item_data
            slot.visualizer_entity = InventoryItem(slot_parent=slot, inventory=self.inventory, texture=copy.copy(self.texture), item_type=copy.copy(self.item_type), description=copy.copy(self.description), category=copy.copy(self.category), item_data=copy.copy(self.item_data), scale=copy.copy(self.scale.x))
                

    #UPDATE THE INVENTORYITEM.
    def update(self):
        self.time_since_split+=time.dt
        #SOMETIMES URSINA GETS QUIRKY WITH DRAGGING, THIS ENSURES CORRECT POSITIONING.
        if not self.dragging:
            self.world_position = self.slot_parent.world_position

        super().update()

        #DROP ITEM.
        if self.hovered and mouse.right:
            self.drop_item()
        #SPLIT ITEM.
        if self.hovered and held_keys['e'] and self.time_since_split>=1:
            self.time_since_split=0
            self.split_item()


    #WHEN STOPPING DRAGGING.
    def drop(self):
        #CHECK IF THE INVENTORY ITEM IS TO BE DROPPED INTO A NEW INVENTORY SLOT.
        MOVED_TO_SLOT = False
        #SMELL MENU CHECK.
        for small_inv_slot in self.inventory.small_menu.inventory_items:
            if small_inv_slot == self.slot_parent:
                continue
            if self.check_traditional_collision(small_inv_slot):
                MOVED_TO_SLOT=self.move_to_slot(small_inv_slot)
                break
        #BIG MENU CHECK:
        if MOVED_TO_SLOT == False:
            for big_inv_slot in self.inventory.big_menu.inventory_items:
                if big_inv_slot==self.slot_parent:
                    continue
                if self.check_traditional_collision(big_inv_slot):
                    MOVED_TO_SLOT=self.move_to_slot(big_inv_slot)
                    break
        #SMELL MENU CHECK.
        if MOVED_TO_SLOT == False:
            for crafting_inv_slot in self.inventory.big_menu.crafting_slots:
                if crafting_inv_slot == self.slot_parent:
                    continue
                if self.check_traditional_collision(crafting_inv_slot):
                    MOVED_TO_SLOT=self.move_to_slot(crafting_inv_slot)
                    break

        #IF NOT GOING INTO A NEW SLOT, JUST MOVE BACK.
        if MOVED_TO_SLOT == False:
            self.move_back()


###
# CRAFTING ITEM SLOT.
# THIS IS WHERE ITEMS GETS CREATED AND CAN BE WITHDRAWN FROM THE CRAFTING TABLE.
###
class CraftingItemSlot(Entity):
    #CRAFTABLE ITEMS DATA.
    _craftable_items_data = json.load(open("scripts/objects/items.json"))
    #INIT CRAFTING ITEM SLOT.
    def __init__(self, inventory,**kwargs):
        super().__init__()
        self.inventory = inventory
        self.parent=camera.ui
        self.model="quad"
        for key,val in kwargs.items():
            setattr(self,key,val)
        #VISUALIZER ENTITY FOR THE TO BE CRAFTED ITEM.
        self.visualiser_entity = Entity(model="quad",parent=self,texture="",scale=(self.scale_x*5,self.scale_y*5,0), position=Vec3(0,0,-2))
        self.item_type=""
        self.collider="box"


    #UPDATE: CHECK FOR ANY ITEMS TO BE CRAFTED.
    def update(self):
        if self.inventory.big_menu.enabled == True:
            #CHECK FOR ANY ITEMS THAT CAN BE CREAFTED.
            crafting_item_craft, item_type_craft = self.check_for_craftable_item()
            #SHOW CRAFTABLE ITEM.
            if crafting_item_craft!=None and item_type_craft!=None:
                self.visualiser_entity.enabled=True
                self.visualiser_entity.texture=copy.copy(crafting_item_craft["texture"])
                self.item_type=copy.copy(item_type_craft)
                self.item_data=copy.copy(crafting_item_craft)
            #NO ITEMS TO BE CRAFTED RESET THE SLOT.
            else:
                self.visualiser_entity.enabled=False
                self.item_type=""
                self.item_data={}


    #GET THE CRAFTABLE ITEM WITH THE CURRENT CRAFTING BENCH CONFIG.
    def check_for_craftable_item(self):
        for craftable_item_category in CraftingItemSlot._craftable_items_data:
            for item in CraftingItemSlot._craftable_items_data[craftable_item_category]:
                #IF WE CANT CRAFT THE ITEM - JUST IGNORE IT.
                if len(CraftingItemSlot._craftable_items_data[craftable_item_category][item]["crafting_slots"])==0:
                    continue
                #CHECK IF THE CURRENT CRAFTING_SLOTS' CONFIG IS THE ITEM'S CONFIFG.
                cur_config = True
                for slot_i in range(len(self.inventory.big_menu.crafting_slots)):
                    if self.inventory.big_menu.crafting_slots[slot_i].item_type == CraftingItemSlot._craftable_items_data[craftable_item_category][item]["crafting_slots"][slot_i]["item_type"]:
                        if self.inventory.big_menu.crafting_slots[slot_i].num_items_slot < CraftingItemSlot._craftable_items_data[craftable_item_category][item]["crafting_slots"][slot_i]["num_items_slot"]:
                            cur_config=False
                    else: 
                        cur_config=False
                #IF THIS IS THE CORRECT CONFIG - RETURN THE ITEM DATA.
                if cur_config==True:
                    return (CraftingItemSlot._craftable_items_data[craftable_item_category][item], item)
        return (None,None)


    #CREATE THE ITEM ENTITY - USED FOR WHEN DROPPING ITEM OUT OF INVENTORY.
    def create_item_entity(self,item_data):
        chunk_indicies = self.inventory.player.world.pos_to_chunk_indicies(self.inventory.player.world_position)
        item = MovingObject(velocity=Vec2(0,1),gravity=-4.905,collides=True, scale=0.5, texture=self.texture, model="quad", item_type=item_data["item_type"], num_items=item_data["num_items"], description=item_data["description"], item_category=item_data["category"], item_data=item_data)
        item.world_position=Vec3(self.inventory.player.world_position.x, self.inventory.player.world_position.y+1,self.inventory.player.world_position.z)
        self.inventory.player.world.all_chunks[chunk_indicies].entities.append(item)

    #WHEN CRAFTING THE ITEM.
    def craft_item(self,item_to_craft, item_type):
        try:
            #REMOVE USED MATERIALS.
            if len(item_to_craft["crafting_slots"])==0:
                return
            for i in range(len(self.inventory.big_menu.crafting_slots)):
                crafting_slot = self.inventory.big_menu.crafting_slots[i]
                if crafting_slot.item_type == item_to_craft["crafting_slots"][i]["item_type"]:
                    if crafting_slot.num_items_slot > item_to_craft["crafting_slots"][i]["num_items_slot"]:
                        #IF COUNT IS HIGHER THAN 1 -> REDUCE THE COUNT FOR REMOVAL.
                        crafting_slot.num_items_slot-=item_to_craft["crafting_slots"][i]["num_items_slot"]
                        crafting_slot.num_items_slot_text.text=f"{crafting_slot.num_items_slot}"
                    elif crafting_slot.num_items_slot == item_to_craft["crafting_slots"][i]["num_items_slot"]:
                        #IF EXACTLY THE RIGHT NUMBER OF ITEM COUNT -> DELETE CRAFTINGBENCH SLOT ITEM VISUALIZER ENTITY.
                        crafting_slot.num_items_slot=0
                        crafting_slot.num_items_slot_text.text="0"
                        crafting_slot.item_type=""
                        crafting_slot.item_data={}
                        destroy(crafting_slot.visualizer_entity)

            #TRY TO FIND A POSSIBLE SLOT- SLOT WITH ALREADY THE ITEM.
            slot = self.inventory.find_possible_slot(item_type,1)
            #IF NO SLOT IS FOUND -> CHECK FOR ANY SLOTS WITHOUT ANY ITEMS.
            if slot==None:
                slot = self.inventory.find_free_slot()
            #NO SLOTS AVAILABLE -> DROP THE CRAFTED ITEM OUT OF THE INVENTORY.
            if slot==None:
                self.create_item_entity(item_to_craft)
                return
            
            #PUT THE CRAFTED ITEM INTO THE INVENTORY IF POSSIBLE.
            if slot.num_items_slot==0:
                self.num_items_slot=0
                slot.num_items_slot=1
                slot.item_type=item_type
                slot.item_data=item_to_craft
                slot.num_items_slot_text.text = slot.num_items_slot
                inv_item = InventoryItem(slot_parent=slot, inventory=self.inventory, texture=item_to_craft["texture"],category=item_to_craft["category"],item_type=item_type,description=item_to_craft["description"],scale=0.05, item_data=item_to_craft)
                slot.visualizer_entity=inv_item
            #IF THE INVENTORY ITEM VISUALIZER ENTITY ALREADY EXISTS -> INCREASE COUNT.
            else:
                slot.num_items_slot+=1
        except Exception:
            print(f"Couldn't craft item. {Exception}")
        
    
    #TRY CRAFTING THE ITEM.
    def on_click(self):
        self.craft_item(self.item_data,self.item_type)





##
# BIG INVENTORY MENU.
# THIS HOLDS THE CRAFTING MENU AND THE BIG INVENTORY SLOTS FOR STORAGE.
###
class BigInventory(Entity):
    #INIT BIG INVENTORY.
    def __init__(self, inventory):
        super().__init__()
        # Small inventory can only hold one item per slot, big one 16.
        self.GRID_Y = 5
        self.GRID_X = 2
        self.CRAFTING_GRID_X=3
        self.CRAFTING_GRID_Y=3
        self.parent = camera.ui
        self.position=Vec3(0,0,0)
        self.scale = 0.65
        self.model = "quad"
        self.texture = "textures/hud/inventory/static.png"
        self.inventory_items = []
        self.crafting_slots = []

        
        #SPAWN IN THE SLOTS FOR HOLDING ITEMS.
        item_holder_distance = 0.5*0.65*self.scale_x/30
        item_holder_scale = (0.5*0.65*self.scale_x-(self.GRID_X-2)*item_holder_distance)/self.GRID_X
        for x in range(self.GRID_X):
            for y in range(self.GRID_Y):
                self.inventory_items.append(
                    InventorySlot(
                        model="quad",
                        texture="textures/hud/inventory/item_holder.png",
                        parent=camera.ui,
                        scale=(item_holder_scale,item_holder_scale,0),
                        position=Vec3(
                            -0.65*self.scale_x/2+item_holder_distance+item_holder_scale*(x+0.5)+(0.25),
                            -0.65*self.scale_y/2+item_holder_distance+item_holder_scale*(y+0.5)-0.03,
                            z=-0.1
                        ),
                        enabled=False
                    )
                )



        #SPAWN IN THE SLOTS FOR CRAFTING.
        crafting_item_holder_distance = 0.5*0.65*self.scale_x/30
        crafting_item_holder_scale = (0.5*0.65*self.scale_x-(self.CRAFTING_GRID_X-2)*item_holder_distance)/self.CRAFTING_GRID_X
        for x in range(self.CRAFTING_GRID_X):
            for y in range(self.CRAFTING_GRID_Y):
                self.crafting_slots.append(
                    InventorySlot(
                        model="quad",
                        texture="textures/hud/inventory/item_holder.png",
                        parent=camera.ui,
                        scale=(crafting_item_holder_scale,crafting_item_holder_scale,0),
                        position=Vec3(
                            -0.65*self.scale_x/2+crafting_item_holder_distance+crafting_item_holder_scale*(x+0.5)-(0.05),
                            -0.65*self.scale_y/2+crafting_item_holder_distance+crafting_item_holder_scale*(y+0.5)+0.25,
                            z=-0.1
                        ),
                        enabled=False
                    )
                )

        #SPAWN IN THE CRAFTING SLOT - THE SLOT YOU GET ITEMS FROM.
        self.crafting_item_slot = CraftingItemSlot(
                        texture="textures/hud/inventory/item_holder.png",
                        scale=(item_holder_scale,item_holder_scale,0),
                        position=Vec3(
                            self.crafting_slots[int(math.floor(len(self.crafting_slots)/2))].x,
                            -0.65*self.scale_y/2+item_holder_distance+item_holder_scale*(y+0.5)-0.1,
                            z=-0.1
                        ),
                        enabled=False,
                        inventory=inventory
                    )


    #ON ENABLE -> ENABLE ALL INVENTORY AND CRAFTING SLOTS.
    def enable(self):
        for i in self.inventory_items:
            i.enabled = True
        for ii in self.crafting_slots:
            ii.enabled=True
        self.crafting_item_slot.enabled=True
        self.enabled = True


    #ON DISABLE -> DISABLE ALL INVENTORY AND CRAFTING SLOTS.
    def disable(self):
        for i in self.inventory_items:
            i.enabled = False
        for i in self.crafting_slots:
            i.enabled=False
        self.crafting_item_slot.enabled=False
        self.enabled = False



###
# SMALL INVENTORY MENU.
# HOLDS THE QUICK SELECT ITEMS -> SELECTED ITEM CAN BE A SWORD, OR SOMETHING ALIKE, WHICH THE PLAYER HOLDS.
###
class SmallInventory(Entity):
    #INIT THE SMALL INVENTORY.
    def __init__(self):
        super().__init__()
        # INIT MINI QUICK INVENTORY.
        self.mini_offset_x = 0
        self.mini_offset_y = 0.08
        self.MINI_GRID_X = 10
        self.selected_item_index = 0
        self.parent = camera.ui
        self.position = Vec2(
            window.bottom.x + self.mini_offset_x,
            window.bottom.y + self.mini_offset_y,
        )
        self.model = "quad"
        self.texture = "textures/hud/inventory/mini_inv.png"
        self.scale_x = 0.8
        self.scale_y = 0.15

        # INIT ALL MINI SLOTS.
        item_holder_distance = self.scale_x / 12
        item_holder_scale = (self.scale_x - item_holder_distance * 2) / self.MINI_GRID_X

        #INIT ALL MINI INVENTORY SLOTS.
        self.inventory_items = [
            InventorySlot(
                model="quad",
                texture=(
                    "textures/hud/inventory/item_holder.png"
                    if i != self.selected_item_index
                    else "textures/hud/inventory/item_holder_selected.png"
                ),
                parent=camera.ui,
                scale_x=item_holder_scale,
                scale_y=min(4 / 9 * self.scale_y, item_holder_scale),
                scale_z=0,
                position=Vec3(
                    self.position.x
                    - self.scale_x / 2
                    + item_holder_distance
                    + item_holder_scale * (i + 0.5),
                    self.position.y,
                    z=-0.1,
                ),
                collider="box",
                MAX_STACK_SIZE=1
            )
            for i in range(self.MINI_GRID_X)
        ]


    #CHECK FOR THE SLOT FOCUSED IN THE QUICK MENU.
    def check_slot_focused(self):
        """Checks and updates which slot is focused."""
        # GET ALL NUMBER KEYS PRESSED.
        selected_quick = [
            key for key in held_keys.keys() if key.isdigit() and held_keys[key]
        ]
        # CHECK IF ANY NUMBER KEY IS PRESSED.
        if len(selected_quick) != 0:
            # MANY SLOTS CAN BE PRESSED AT ONCE, CHOOSE FIRST ONE.
            selected_quick = int(selected_quick[0])
            # KEYBOARD GOES FROM 1..9,0 WE WANT INDICES WE NEED TO TRANSFORM 0 KEY TO '10 KEY'.
            if selected_quick == 0:
                selected_quick = 10

            # IT IS NOT GARAUNTEED THAT NUMBER IS INSIDE THE SLOT ARRAY.
            if selected_quick <= self.MINI_GRID_X:
                # CHANGE CURRENT SLOT FOCUSED TO STANDARD.
                self.inventory_items[self.selected_item_index].texture = (
                    "textures/hud/inventory/item_holder.png"
                )
                # UPDATE FOCUSED SLOT.
                self.selected_item_index = selected_quick - 1
                self.inventory_items[self.selected_item_index].texture = (
                    "textures/hud/inventory/item_holder_selected.png"
                )


    #ON ENABLE -> ENABLE ALL INVENTORY SLOTS.
    def enable(self):
        for i in self.inventory_items:
            i.enabled = True
        self.enabled = True


    #ON DISABLE -> DISABLE ALL INVENTORY SLOTS.
    def disable(self):
        for i in self.inventory_items:
            i.enabled = False
        self.enabled = False

###   
# WHOLE INVENTORY SYSTEM OBJECT.
###
class Inventory(Entity):
    """
    The inventory works quite like in minecraft,
    You've got one grid of squares, in each square you can have one item
    Stacking upwards towards 16 before a new slot is filled.
    You've also got a smaller inv for quick-switching items, this one holds one item per slot.
    When 'I' is pressed the big inventory is shown, else the smaller one is shown.
    """
    #INIT THE INVENTORY.
    def __init__(self, player, pick_up_radius=1.5):
        super().__init__()
        self.big_menu = BigInventory(inventory=self)
        self.big_menu.enabled=False
        self.small_menu = SmallInventory()
        self.spawn_in_start_items()
        self.player = player
        self.pick_up_radius=pick_up_radius

    #SPAWN IN ONE INVENTORY START ITEM.
    def spawn_one_start_item(self, item_type, category, index, amount, resource_or_item, biome=""):
        #IF THE INVENTORY ITEM WANTED IS A CRAFTABLE ITEM.
        if resource_or_item=="item":
            self.small_menu.inventory_items[index].visualizer_entity=(
                InventoryItem(self.small_menu.inventory_items[index],
                            inventory=self,
                            texture=CraftingItemSlot._craftable_items_data[category][item_type]["texture"],
                            category=category,
                            item_type=item_type,
                            description=CraftingItemSlot._craftable_items_data[category][item_type]["description"],
                            item_data=CraftingItemSlot._craftable_items_data[category][item_type],
                            scale=0.05)
                )

            self.small_menu.inventory_items[index].item_data=CraftingItemSlot._craftable_items_data[category][item_type]
            self.small_menu.inventory_items[index].description=CraftingItemSlot._craftable_items_data[category][item_type]["description"]
        #IF THE START INVENTORY ITEM WANTED IS A RESOURCE FROM A BIOME AND NOT AN ITEM.
        else:
            self.small_menu.inventory_items[index].visualizer_entity=(
                InventoryItem(self.small_menu.inventory_items[index],
                            inventory=self,
                            texture=Chunk._biomes[biome]["block_types"]["ores"][item_type]["dropped_resource"]["texture"],
                            category=category,
                            item_type=item_type,
                            description=Chunk._biomes[biome]["block_types"]["ores"][item_type]["dropped_resource"]["description"],
                            item_data=Chunk._biomes[biome]["block_types"]["ores"][item_type]["dropped_resource"],
                            scale=0.05)
                )
            self.small_menu.inventory_items[index].item_data=Chunk._biomes[biome]["block_types"]["ores"][item_type]["dropped_resource"]
            self.small_menu.inventory_items[index].description=Chunk._biomes[biome]["block_types"]["ores"][item_type]["dropped_resource"]["description"]
        #UPDATE COMMON INVENTORY SLOT INFORMATION.
        self.small_menu.inventory_items[index].num_items_slot=amount
        self.small_menu.inventory_items[index].num_items_slot_text.text=amount
        self.small_menu.inventory_items[index].item_type=item_type


    #SPAWN IN ALL THE START ITEMS.
    def spawn_in_start_items(self):
        self.spawn_one_start_item("steak","food",0,5,"item")
        self.spawn_one_start_item("axe","handheld_weapons",1,1,"item")
        self.spawn_one_start_item("dagger","handheld_weapons",2,1,"item")
        self.spawn_one_start_item("iron","resource",3,10,"resource","winter_plains")

        
    #CHECK FOR ANY ITEMS PICKED UP - OR IF THE BIG MENU IS ENABLED OR NOT - OR QUICK SELECT ITEM IS BEING DROPPED.
    def input(self, key):
        #PICK UP ITEM.
        if key=="e":
            #We get all the possible entities that are close to the player
            #We may also need to check the other chunks as the player may be on the edge.
            all_entities_to_check = {}

            #CHECK ALL CLOSE CHUNKS.
            for x in range(3):
                for y in range(3):

                    #GET ALL ENTITIES IN PICK UP RANGE.
                    cur_chunk_index = self.player.world.pos_to_chunk_indicies(self.player.world_position+Vec3(x-1,y-1,0))
                    if cur_chunk_index not in all_entities_to_check and cur_chunk_index in self.player.world.all_chunks.keys():
                            all_entities_to_check[cur_chunk_index]=self.player.world.all_chunks[cur_chunk_index].entities

            #FOR EACH ENTITY IN ALL CHUNKS IN PICKUP RANGE.
            for chunk_index in all_entities_to_check:
                chunk_ents = all_entities_to_check[chunk_index]
                for ent in chunk_ents:
                    #Check if it is an item.
                    if hasattr(ent,"num_items"):
                        delta = ent.world_position-self.player.world_position
                        if (delta.x**2+delta.y**2)**0.5<=self.pick_up_radius:
                            self.pick_up_item(ent, chunk_ents)
                            break


        ##ENABLE / DISABLE MENUS.
        if key=="i":
            if self.big_menu.enabled:
                self.big_menu.disable()
            else:
                self.big_menu.enable()

        ##DROP QUICKSLOT ITEM.
        if key=="g":
            if self.small_menu.inventory_items[self.small_menu.selected_item_index].num_items_slot>0:
                self.small_menu.inventory_items[self.small_menu.selected_item_index].visualizer_entity.drop_item()
                self.small_menu.inventory_items[self.small_menu.selected_item_index].num_items_slot=0
                self.small_menu.inventory_items[self.small_menu.selected_item_index].num_items_slot_text.text=0



    #UPDATE THE SELECTED QUICK ITEM FOCUSED.
    def update(self):
        self.small_menu.check_slot_focused()



    #LOOK FOR A FREE SLOT IN THE INVENTORY - AKA A SLOT WITHOUT ANY ITEMS.
    def find_free_slot(self):
        """
        THIS FUNCTION ATTEMPTS TO FIND A FREE SLOT WITHOUT ANY ITEM DATA.
        """
        for slot in self.small_menu.inventory_items:
            if slot.item_type=="":
                return slot

        for slot in self.big_menu.inventory_items:
            if slot.item_type=="":
                return slot
        
        return None


    #LOOK FOR A POSSIBLE SLOT IN THE INVENTORY - AKA A SLOT WITH THE REQUEST ITEM BUT ADDING WOUDLN'T GO ABOVE THE STACK SIZE.
    def find_possible_slot(self, item_type, item_num):
        """
        THIS FUNCTION ATTEMPTS TO FIND A SLOT WITH THE SAME ITEM DATA - THEN WE JUST INCREMENT THE NUM ITEM COUNT. 
        """
        for slot in self.small_menu.inventory_items:
            if slot.item_type==item_type and item_num+slot.num_items_slot<slot.MAX_STACK_SIZE:
                return slot

        for slot in self.big_menu.inventory_items:
            if slot.item_type==item_type and item_num+slot.num_items_slot<slot.MAX_STACK_SIZE:
                return slot
        
        return None
    


    #TRY TO PICK UP THE ITEM ON THE GROUND.
    def pick_up_item(self, item_on_ground, chunk_ents):
        #TRY FIND INVENTORY SLOT WITH POSSIBLE COUNT ADDITION.
        slot = self.find_possible_slot(copy.copy(item_on_ground.item_type),copy.copy(item_on_ground.num_items))
        #IF NO SLOT FOUND -> TRY FIND EMPTY SLOT.
        if slot==None:
            slot = self.find_free_slot()
        #NO SLOTS -> IGNORE THE ITEM.
        if slot==None:
            return

        #PICK UP THE ITEM.
        #IF VISUALIZER ENTITY IS REQUIRED.
        if slot.num_items_slot==0:
            slot.num_items_slot=copy.copy(item_on_ground.num_items)
            slot.item_type=copy.copy(item_on_ground.item_type)
            slot.item_data=copy.copy(item_on_ground.item_data)
            slot.num_items_slot_text.text=slot.num_items_slot
            inv_item = InventoryItem(slot_parent=slot, inventory=self,texture=copy.copy(item_on_ground.texture),item_type=copy.copy(item_on_ground.item_type),item_data=copy.copy(item_on_ground.item_data), category =copy.copy(item_on_ground.item_data["category"]), description=copy.copy(item_on_ground.description),scale=0.05)
            slot.visualizer_entity=inv_item
            chunk_ents.remove(item_on_ground)
            destroy(item_on_ground)
        #IF NOT REQUIRED.
        else:
            slot.num_items_slot+=copy.copy(item_on_ground.num_items)
            slot.num_items_slot_text.text=slot.num_items_slot
            chunk_ents.remove(item_on_ground)
            destroy(item_on_ground)
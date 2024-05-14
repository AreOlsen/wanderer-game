from ursina import (
    held_keys,
    camera,
    Entity,
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


class InventorySlot(Entity):
    def __init__(self,MAX_STACK_SIZE=16,**kwargs):
        self.visualizer_entity = ""
        super().__init__()
        self.MAX_STACK_SIZE = MAX_STACK_SIZE
        self.num_items_slot = 0 
        self.item_type = ""
        self.item_data = {}

        self.num_items_slot_text = Text(f"{self.num_items_slot}", position=Vec3(-0.3,-0.3,-2.1), scale=10, origin=(0,0), parent=self)

        for key, val in kwargs.items():
            setattr(self,key,val)

    def on_disable(self):
        if self.visualizer_entity != "":
            self.visualizer_entity.disable()
        self.enabled=False

    def on_enable(self):
        if self.visualizer_entity != "":
            self.visualizer_entity.enable()
        self.enabled=True



class InventoryItem(Draggable):
    """
        This is a class representing the visual item on the inventory.
        It houses all the information regarding movement of items, removal, etc.
    """
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
        
        #NO HIGHLIGHT COLOUR.
        self.color = color.white
        self.highlight_color = color.white
        self.pressed_color = color.white
        
        #COLLIDER.
        self.scale = (scale,scale,0)

        #INFO ABOUT THE ITEM.
        self.info = Text(f"{self.item_type}\n{self.description}", position=Vec3(1,1,-2.1), scale=20, origin=(0,0), parent=self)
        self.info.enabled = False



    def drag(self):
        self.org_pos = (self.x,self.y,self.z)



    def check_traditional_collision(self,ent_2):
        # Calculate the minimum and maximum x and y values for both objects
        self_min_x = self.world_position.x - self.scale_x
        self_max_x = self.world_position.x + self.scale_x
        self_min_y = self.world_position.y - self.scale_y
        self_max_y = self.world_position.y + self.scale_y

        ent_2_min_x = ent_2.world_position.x - ent_2.scale_x
        ent_2_max_x = ent_2.world_position.x + ent_2.scale_x
        ent_2_min_y = ent_2.world_position.y - ent_2.scale_y
        ent_2_max_y = ent_2.world_position.y + ent_2.scale_y

        # Check for collision
        if (self_min_x <= ent_2_max_x and self_max_x >= ent_2_min_x) and \
            (self_min_y <= ent_2_max_y and self_max_y >= ent_2_min_y):
            return True
        else:
            return False



    def move_to_slot(self,inventory_slot_chosen):
        #If not empty or not correct item in slot.
        if inventory_slot_chosen.item_type != "" and inventory_slot_chosen.item_type!=self.item_type:
            self.move_back()
        #If there is space available in the slot.
        if inventory_slot_chosen.num_items_slot<inventory_slot_chosen.MAX_STACK_SIZE:
            #If the new value of the next is less than max size.
            if inventory_slot_chosen.num_items_slot+self.slot_parent.num_items_slot<=inventory_slot_chosen.MAX_STACK_SIZE:
                delete_self = False
                #Update the new slots item count.
                #If there is no displaying item object already there.
                if inventory_slot_chosen.num_items_slot==0:
                    inventory_slot_chosen.num_items_slot+=self.slot_parent.num_items_slot
                    inventory_slot_chosen.num_items_slot_text.text=f"{inventory_slot_chosen.num_items_slot}"
                    self.slot_parent.num_items_slot = 0
                    self.slot_parent.num_items_slot_text.text="0"
                    self.slot_parent.visualizer_entity = ""
                    self.slot_parent = inventory_slot_chosen
                    self.slot_parent.visualizer_entity = self
                    self.world_position=inventory_slot_chosen.world_position
                #Else we just do the math addition and delete ourselves.
                else:
                    inventory_slot_chosen.num_items_slot+=self.slot_parent.num_items_slot
                    inventory_slot_chosen.num_items_slot_text.text=f"{inventory_slot_chosen.num_items_slot}"
                    self.slot_parent.num_items_slot = 0
                    self.slot_parent.num_items_slot_text.text="0"
                    delete_self = True
                #If we require deleting ourselves.
                if delete_self:
                    destroy(self)
                return True
            else:
                self.move_back()
                return False
        else:
            self.move_back()
            return False



    def move_back(self):
        self.position=self.org_pos
        


    def drop_item(self):
        #We need to add the dropped items to the chunk entities.
        chunk_pos = self.inventory.player.world.pos_to_chunk_indicies(self.inventory.player.world_position)
        item = MovingObject(model="quad",texture=copy.copy(self.texture),scale=0.5,velocity=Vec2(0,1),gravity=-4.905,collides=True,item_type=copy.copy(self.item_type), num_items=copy.copy(self.slot_parent.num_items_slot), description=copy.copy(self.description), item_data=copy.copy(self.item_data))
        item.world_position=Vec3(copy.copy(self.inventory.player.world_position.x), copy.copy(self.inventory.player.world_position.y)+1,copy.copy(self.inventory.player.world_position.z))
        self.inventory.player.world.all_chunks[chunk_pos].entities.append(item)
        self.slot_parent.num_items_slot=0
        self.slot_parent.item_type=""
        self.slot_parent.item_data={}
        self.slot_parent.num_items_slot_text.text = "0"
        destroy(self)

    def check_move_one_to_slot(self):
        """
        Instead of moving everything, just move one.
        """
        big_inv_moved = False
        for big_inv_slot in self.inventory.big_menu.inventory_items:
            if big_inv_slot==self.slot_parent:
                continue
            if self.check_traditional_collision(big_inv_slot):
                big_inv_moved = self.move_one_to_slot(big_inv_slot)
                break
        #SMELL MENU CHECK.
        if big_inv_moved==False:
            for small_inv_slot in self.inventory.small_menu.inventory_items:
                if small_inv_slot == self.slot_parent:
                    continue
                if self.check_traditional_collision(small_inv_slot):
                    self.move_one_to_slot(small_inv_slot)
                    break


    def move_one_to_slot(self, inventory_slot_chosen):
        """
        Instead of moving everything, just move one.
        """
        if inventory_slot_chosen.num_items_slot >= 0 and inventory_slot_chosen.num_items_slot+1<=inventory_slot_chosen.MAX_STACK_SIZE:
            inventory_slot_chosen.num_items_slot+=1
            self.slot_parent.num_items_slot-=1
            inventory_slot_chosen.num_items_slot_text.text=f"{inventory_slot_chosen.num_items_slot}"
            self.slot_parent.num_items_slot_text.text=f"{self.slot_parent.num_items_slot}"
            if self.slot_parent.num_items_slot == 0:
                inventory_slot_chosen.visualizer_entity = self
                self.slot_parent=inventory_slot_chosen
                self.world_position = inventory_slot_chosen.world_position
            return True
        return False


    def update(self):
        super().update()
        
        #Move just one item.
        if self.dragging and mouse.right:
            self.check_move_one_to_slot()

        #Drop item.
        elif self.hovered and mouse.right:
            self.drop_item()

        #Sometimes Ursina gets a little quirky, and doesn't update the position - this ensures position is correct.
        if not self.dragging:
            self.world_position = self.slot_parent.world_position



    def drop(self):
        #HERE A MORE TRADITIONAL COLLISION CHECK IS IMPLEMENTED.
        #THIS IS BECAUSE WE DON'T WANT THE INVENTORY SLOTS TO HAVE COLLISION BOXES.
        #AS THIS WOULD MEAN THAT IN GAME ITEMS, LIKE AN ARROW, COULD COLLIDE WITH THE INVENTORY SLOTS.
        #AND THIS WOULD NOT BE ADVANTAGEOUS.
        MOVED_TO_SLOT = False
        #BIG MENU CHECK:
        for big_inv_slot in self.inventory.big_menu.inventory_items:
            if big_inv_slot==self.slot_parent:
                continue
            if self.check_traditional_collision(big_inv_slot):
                MOVED_TO_SLOT=self.move_to_slot(big_inv_slot)
                break
        #SMELL MENU CHECK.
        if MOVED_TO_SLOT == False:
            for small_inv_slot in self.inventory.small_menu.inventory_items:
                if small_inv_slot == self.slot_parent:
                    continue
                if self.check_traditional_collision(small_inv_slot):
                    MOVED_TO_SLOT=self.move_to_slot(small_inv_slot)
                    break
        #IF NOT GOING INTO A NEW SLOT, JUST MOVE BACK.
        if MOVED_TO_SLOT == False:
            self.move_back()



class CraftingItemSlot(Entity):
    _craftable_items_data = json.load(open("scripts/objects/items.json"))
    def __init__(self, inventory,**kwargs):
        super().__init__()
        self.inventory = inventory
        self.parent=camera.ui
        self.model="quad"
        for key,val in kwargs.items():
            setattr(self,key,val)
        self.visualiser_entity = Entity(parent=self,texture="",scale=(self.scale_x*0.8,self.scale_y*0.8,0), position=Vec3(0,0,-2))
        self.item_type=""

    def update(self):
        if self.inventory.big_menu.enabled == True:
            crafting_item = self.check_for_craftable_item()
            if crafting_item!=None:
                self.visualiser_entity.texture=crafting_item["texture"]
                self.item_type=crafting_item["item_type"]
                self.item_data=crafting_item

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
                    return item
        return None


    def create_item_entity(self,item_data):
        chunk_indicies = self.inventory.player.world.pos_to_chunk_indicies(self.inventory.player.world_position)
        item = MovingObject(velocity=Vec2(0,1),gravity=-4.905,collides=True, scale=0.5, texture=self.texture, model="quad", item_type=item_data["item_type"], num_items=item_data["num_items"], description=item_data["description"], item_category=item_data["category"], item_data=item_data)
        item.world_position=Vec3(self.inventory.player.world_position.x, self.inventory.player.world_position.y+1,self.inventory.player.world_position.z)
        self.inventory.player.world.all_chunks[chunk_indicies].entities.append(item)


    def craft_item(self,item_to_craft):
        #Remove the used materials.
        if len(item_to_craft["crafting_slots"])==0:
            return
        for i in range(self.inventory.big_menu.crafting_slots):
            crafting_slot = self.inventory.big_menu.craftings_slots[i]
            if crafting_slot.item_type == item_to_craft["crafting_slots"][i]["item_type"]:
                if crafting_slot.num_items_slot > item_to_craft["crafting_slots"][i]["num_items"]:
                    #If left other items - > reduce the num items count.
                    crafting_slot.num_items_slot-=item_to_craft["crafting_slots"][i]["num_items"]
                elif crafting_slot.num_items_slot == item_to_craft["crafting_slots"][i]["num_items"]:
                    #If we have exactly the right num of the item we need to delete the visualizer entity.
                    crafting_slot.num_items_slot=0
                    crafting_slot.item_type=""
                    crafting_slot.item_data={}
                    destroy(crafting_slot.visualizer_entity)

        #Try to find a possible slot.
        slot = self.inventory.find_possible_slot(item_to_craft["item_type"],item_to_craft["num_items"])
        #If none found -> look for free slot.
        if slot==None:
            slot = self.inventory.find_free_slot()
        #No slots -> drop the new item.
        if slot==None:
            self.create_item_entity(item_to_craft)
            return
        
        #Put the crafted item into the inventory
        if slot.num_items_slot==0:
            slot.num_items_slot=item_to_craft["num_items"]
            slot.item_type=item_to_craft["item_type"]
            slot.item_data=item_to_craft
            slot.num_items_slot_text.text = slot.num_items_slot
            inv_item = InventoryItem(slot_parent=slot, inventory=self,texture=item_to_craft["texture"],item_type=item_to_craft["item_type"],description=item_to_craft["description"],scale=0.05, item_data=item_to_craft)
            slot.visualizer_entity=inv_item
        #If it already exists there.
        else:
            slot.num_items_slot+=item_to_craft["num_items"]
        


class BigInventory(Entity):
    def __init__(self, inventory):
        super().__init__()
        # INIT BIG INVENTORY.
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

    def enable(self):
        for i in self.inventory_items:
            i.enabled = True
        for ii in self.crafting_slots:
            ii.enabled=True
        self.crafting_item_slot.enabled=True
        self.enabled = True



    def disable(self):
        for i in self.inventory_items:
            i.enabled = False
        for i in self.crafting_slots:
            i.enabled=False
        self.crafting_item_slot.enabled=False
        self.enabled = False



class SmallInventory(Entity):
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



    def enable(self):
        for i in self.inventory_items:
            i.enabled = True
        self.enabled = True



    def disable(self):
        for i in self.inventory_items:
            i.enabled = False
        self.enabled = False

    


class Inventory(Entity):
    """
    The inventory works quite like in minecraft,
    You've got one grid of squares, in each square you can have one item
    Stacking upwards towards 16 before a new slot is filled.
    You've also got a smaller inv for quick-switching items, this one holds one item per slot.
    When 'I' is pressed the big inventory is shown, else the smaller one is shown.
    """



    def __init__(self, player, pick_up_radius=1.5):
        super().__init__()
        self.big_menu = BigInventory(inventory=self)
        self.big_menu.enabled=False
        self.small_menu = SmallInventory()
        self.spawn_in_start_items()
        self.player = player
        self.pick_up_radius=pick_up_radius

    def spawn_one_start_item(self, item_type, category, index):
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
        self.small_menu.inventory_items[index].num_items_slot=1
        self.small_menu.inventory_items[index].num_items_slot_text.text=1
        self.small_menu.inventory_items[index].item_type=item_type
        self.small_menu.inventory_items[index].item_data=CraftingItemSlot._craftable_items_data[category][item_type]
        self.small_menu.inventory_items[index].description=CraftingItemSlot._craftable_items_data[category][item_type]["description"]

    def spawn_in_start_items(self):
        self.spawn_one_start_item("steak","food",0)
        self.spawn_one_start_item("axe","handheld_weapons",1)
        self.spawn_one_start_item("dagger","handheld_weapons",2)




    def input(self, key):
        #PICK UP ITEM.
        if key=="e":
            #We get all the possible entities that are close to the player
            #We may also need to check the other chunks as the player may be on the edge.
            all_entities_to_check = {}

            #CHECK ALL CLOSE CHUNKS.
            for x in np.arange(-self.pick_up_radius/2,self.pick_up_radius/2,0.1):
                for y in np.arange(-self.pick_up_radius/2,self.pick_up_radius/2,0.1):

                    #GET ALL ENTITIES IN PICK UP RANGE.
                    cur_chunk_index = self.player.world.pos_to_chunk_indicies(self.player.world_position+Vec3(x,y,0))
                    if cur_chunk_index not in all_entities_to_check and cur_chunk_index in self.player.world.all_chunks:
                            all_entities_to_check[cur_chunk_index]=self.player.world.all_chunks[cur_chunk_index].entities

            #FOR EACH ENTITY IN ALL CHUNKS IN PICKUP RANGE.
            for chunk_ents in list(all_entities_to_check.values()):
                for ent in chunk_ents:
                    #Check if it is an item.
                    if hasattr(ent,"num_items"):
                        if distance(ent.world_position,self.player.world_position)<=self.pick_up_radius:
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




    def update(self):
        self.small_menu.check_slot_focused()



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
    


    def pick_up_item(self, item_on_ground, chunk_ents):
        #Try to find a possible slot which already has the item type.
        slot = self.find_possible_slot(copy.copy(item_on_ground.item_type),copy.copy(item_on_ground.num_items))
        #If none found -> look for free slot.
        if slot==None:
            slot = self.find_free_slot()
        #No slots -> dont pick up item.
        if slot==None:
            return

        #Pick up the item:
        if slot.num_items_slot==0:
            slot.num_items_slot=copy.copy(item_on_ground.num_items)
            slot.item_type=copy.copy(item_on_ground.item_type)
            slot.item_data=copy.copy(item_on_ground.item_data)
            slot.num_items_slot_text.text=slot.num_items_slot
            inv_item = InventoryItem(slot_parent=slot, inventory=self,texture=copy.copy(item_on_ground.texture),item_type=copy.copy(item_on_ground.item_type),item_data=copy.copy(item_on_ground.item_data), category =copy.copy(item_on_ground.item_data["category"]), description=copy.copy(item_on_ground.description),scale=0.05)
            slot.visualizer_entity=inv_item
            chunk_ents.remove(item_on_ground)
            destroy(item_on_ground)
        else:
            slot.num_items_slot+=copy.copy(item_on_ground.num_items)
            chunk_ents.remove(item_on_ground)
            destroy(item_on_ground)
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
    mouse
)
from ursina.ursinamath import Vec2, Vec3
import math

class InventorySlot(Entity):
    def __init__(self,MAX_STACK_SIZE=16,**kwargs):
        super().__init__()
        self.MAX_STACK_SIZE = MAX_STACK_SIZE
        self.num_items_slot = 0 
        self.item_type = ""

        self.num_items_slot_text = Text(f"{self.num_items_slot}", position=Vec3(-1,-1,-1), scale=10, origin=(0,0), parent=self)

        for key, val in kwargs.items():
            setattr(self,key,val)


class InventoryItem(Draggable):
    def __init__(self, slot_parent, inventory, texture, item_type, description, scale):
        super().__init__()
        #BASIC INIT.
        self.texture = texture
        self.item_type = item_type
        self.description = description
        self.parent = slot_parent
        self.model="quad"
        self.inventory = inventory
        
        #NO HIGHLIGHT COLOUR.
        self.color = color.white
        self.highlight_color = color.white
        self.pressed_color = color.white
        
        #COLLIDER.
        self.scale = (scale,scale,0)

        #INFO ABOUT THE ITEM.
        self.info = Text(f"{self.item_type}\n{self.description}", position=Vec3(1,1,-1), scale=20, origin=(0,0), parent=self)
        self.info.enabled = False

    def drag(self):
        self.org_pos = (self.x,self.y,self.z)

    def check_traditional_collision(self,ent_2):
        # Calculate the minimum and maximum x and y values for both objects
        self_min_x = self.world_position.x - self.scale_x / 2
        self_max_x = self.world_position.x + self.scale_x / 2
        self_min_y = self.world_position.y - self.scale_y / 2
        self_max_y = self.world_position.y + self.scale_y / 2

        ent_2_min_x = ent_2.world_position.x - ent_2.scale_x / 2
        ent_2_max_x = ent_2.world_position.x + ent_2.scale_x / 2
        ent_2_min_y = ent_2.world_position.y - ent_2.scale_y / 2
        ent_2_max_y = ent_2.world_position.y + ent_2.scale_y / 2

        # Check for collision
        if (self_min_x <= ent_2_max_x and self_max_x >= ent_2_min_x) and \
        (self_min_y <= ent_2_max_y and self_max_y >= ent_2_min_y):
            return True
        else:
            return False

    def move_to_slot(self,inventory_slot_chosen):
        #If not empty or not correct item in slot.
        if inventory_slot_chosen.item_type != "" or inventory_slot_chosen.item_type!=self.item_type:
            self.move_back()
        #If there is space available in the slot.
        if inventory_slot_chosen.num_items_slot<inventory_slot_chosen.MAX_STACK_SIZE:
            #If the new value of the next is less than max size.
            if inventory_slot_chosen.num_items_slot+self.parent.num_items_slot<=inventory_slot_chosen.MAX_STACK_SIZE:
                delete_self = False
                #If there is no displaying item object already there.
                if inventory_slot_chonsen.num_items_slot==0:
                    self.parent = inventory_slot_chosen
                    self.position=Vec3(0,0,-0.1)
                #Else we just do the math addition and delete ourselves.
                else:
                    delete_self = True
                #Update the new slots item count.
                inventory_slot_chosen.num_items_slot+=self.parent.num_items_slot
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

    def drop(self):
        #HERE A MORE TRADITIONAL COLLISION CHECK IS IMPLEMENTED.
        #THIS IS BECAUSE WE DON'T WANT THE INVENTORY SLOTS TO HAVE COLLISION BOXES.
        #AS THIS WOULD MEAN THAT IN GAME ITEMS, LIKE AN ARROW, COULD COLLIDE WITH THE INVENTORY SLOTS.
        #AND THIS WOULD NOT BE ADVANTAGEOUS.
        MOVED_TO_SLOT = False
        #BIG MENU CHECK:
        for big_inv_slot in self.inventory.big_menu.inventory_items:
            if big_inv_slot==self.parent:
                continue
            print(self.check_traditiona_collision(big_inv_slot))
            if self.check_traditiona_collision(big_inv_slot):
                MOVED_TO_SLOT=self.move_to_slot(big_inv_slot)
                break
        #SMELL MENU CHECK.
        if MOVED_TO_SLOT == False:
            for small_inv_slot in self.inventory.small_menu.inventory_items:
                if small_inv_slot == self.parent:
                    continue
                if self.check_traditiona_collision(big_inv_slot):
                    MOVED_TO_SLOT=self.move_to_slot(small_inv_slot)
                    break
        #IF NOT GOING INTO A NEW SLOT, JUST MOVE BACK.
        if MOVED_TO_SLOT == False:
            self.move_back()

class BigInventory(Entity):
    def __init__(self):
        super().__init__()
        # INIT BIG INVENTORY.
        # Small inventory can only hold one item per slot, big one 16.
        self.GRID_Y = 5
        self.GRID_X = 4
        self.parent = camera.ui
        self.position=Vec3(0,0,0)
        self.scale = 0.65
        self.model = "quad"
        self.texture = "textures/hud/inventory/static.png"
        self.inventory_items = []

        item_holder_distance = 0.65*self.scale_x/30
        item_holder_scale = (0.65*self.scale_x-(self.GRID_X-2)*item_holder_distance)/self.GRID_X
        for x in range(self.GRID_X):
            for y in range(self.GRID_Y):
                self.inventory_items.append(
                    InventorySlot(
                        model="quad",
                        texture="textures/hud/inventory/item_holder.png",
                        parent=camera.ui,
                        scale=(item_holder_scale,item_holder_scale,0),
                        position=Vec3(
                            -0.65*self.scale_x/2+item_holder_distance+item_holder_scale*(x+0.5)-(0.05)*((-1)**(math.floor(x/(self.GRID_X/2)))),
                            -0.65*self.scale_y/2+item_holder_distance+item_holder_scale*(y+0.5)-0.02,
                            z=-0.1
                        ),
                        enabled=False
                    )
                )

    def enable(self):
        for i in self.inventory_items:
            i.enabled = True
        self.enabled = True

    def disable(self):
        for i in self.inventory_items:
            i.enabled = False
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
                collider="box"
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

    def __init__(self):
        super().__init__()
        self.big_menu = BigInventory()
        self.big_menu.enabled=False
        self.small_menu = SmallInventory()

    def input(self, key):
        if key=="i":
            if self.big_menu.enabled:
                self.big_menu.disable()
            else:
                self.big_menu.enable()

    def update(self):
        self.small_menu.check_slot_focused()
        

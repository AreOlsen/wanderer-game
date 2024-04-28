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

class InventoryItem(Draggable):
    _MAX_STACK_SIZE = 16
    def __init__(self, inventory_parent, texture, name, description, scale):
        super().__init__()
        self.texture = texture
        self.name = name
        self.description = description
        self.parent = inventory_parent
        self.model="quad"
        self.color = color.white
        self.highlight_color = color.white
        self.pressed_color = color.white
        self.scale = (scale,scale,1)
        self.collider = BoxCollider(self,center=(0,0,0),size=(scale,scale,1))
        self.info = Text(f"{self.name}\n{self.description}", position=Vec3(1,1,-1), scale=20, origin=(0,0), parent=self)
        self.info.enabled = False

    def drag(self):
        self.org_pos = (self.x,self.y,self.z)

    def drop(self):
        if self.intersects().hit:
            print("Intersected something.")
        else:
            self.position=self.org_pos



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
                    Entity(
                        model="quad",
                        texture="textures/hud/inventory/item_holder.png",
                        parent=camera.ui,
                        scale=item_holder_scale,
                        position=Vec3(
                            -0.65*self.scale_x/2+item_holder_distance+item_holder_scale*(x+0.5)-(0.05)*((-1)**(math.floor(x/(self.GRID_X/2)))),
                            -0.65*self.scale_y/2+item_holder_distance+item_holder_scale*(y+0.5)-0.02,
                            z=-0.1
                        ),
                        collider="box",
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
            Entity(
                model="quad",
                texture=(
                    "textures/hud/inventory/item_holder.png"
                    if i != self.selected_item_index
                    else "textures/hud/inventory/item_holder_selected.png"
                ),
                parent=camera.ui,
                scale_x=item_holder_scale,
                scale_y=min(4 / 9 * self.scale_y, item_holder_scale),
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
    When I is pressed the big inventory is shown, else the smaller one is shown.
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
        

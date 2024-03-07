from ursina import (
    held_keys,
    camera,
    Entity,
    Animation,
    window,
    Sequence,
    Draggable,
    Tooltip,
)
from ursina.ursinamath import Vec2, Vec3


class InventoryItem(Draggable):
    def __init__(self, texture, name, description, scale):
        super().__init__()
        self.texture = texture
        self.name = name
        self.description = description
        self.info = Tooltip(f"{self.name}\n{self.description}")
        self.info.enabled = False

    def update(self):
        if self.dragging == False and self.hovered:
            self.info.enabled = True


class BigInventory(Entity):
    def __init__(self):
        super().__init__()
        # INIT BIG INVENTORY.
        # Small inventory can only hold one item per slot, big one 16.
        self.MAX_STACK_SIZE = 16
        self.OPENING_ANIMATION_SECONDS = 0.2
        self.CLOSING_ANIMATION_SECONDS = 0.2
        self.GRID_Y = 10
        self.GRID_X = 15
        self.parent = camera.ui
        self.model = "quad"
        self.texture = "textures/hud/inventory/static.png"
        self.inventory_items = []

    def enable(self):
        #Show opening animation
        self.enabled = True

    def disable(self):
        #Show closing animation.
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
        self.position =Vec2(
                window.bottom.x + self.mini_offset_x,
                window.bottom.y + self.mini_offset_y,
            )
        self.model="quad"
        self.texture = "textures/hud/inventory/mini_inv.png"
        self.scale_x = 0.8
        self.scale_y = 0.15

        #INIT ALL MINI SLOTS.
        item_holder_distance = self.scale_x / 12
        item_holder_scale = (
            self.scale_x - item_holder_distance * 2
        ) / self.MINI_GRID_X

        self.quick_inv_items = [
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
                selected_quick = 1

            # IT IS NOT GARAUNTEED THAT NUMBER IS INSIDE THE SLOT ARRAY.
            if selected_quick <= self.MINI_GRID_X:
                #CHANGE CURRENT SLOT FOCUSED TO STANDARD.
                self.quick_inv_items[self.selected_item_index].texture = (
                    "textures/hud/inventory/item_holder.png"
                )
                #UPDATE FOCUSED SLOT.
                self.selected_item_index = selected_quick - 1
                self.quick_inv_items[self.selected_item_index].texture = (
                    "textures/hud/inventory/item_holder_selected.png"
                )

    
    def enable(self):
        for i in self.quick_inv_items:
            i.enabled = True
        self.enabled = True

    def disable(self):
        for i in self.quick_inv_items:
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
        #For toggling:
        #Each frame is updated and gives a return, we have to check if it is the first frame when clicked.
        self._opening_last_frame = False
        self.big_inventory_visible = False
        self.big_menu = BigInventory()
        self.small_menu = SmallInventory()

    def check_if_toggle(self):
        """Check and eventually toggle the currently toggled menu."""
        if held_keys["i"]:
            #Check for if first key-press.
            #Each frame registers individual press of button while holding, so we create a toggle here by utilising the last frame's pressing state.
            if self._opening_last_frame == False:
                self.big_inventory_visible = not self.big_inventory_visible

        #Set next frame's last frame state. Aka current state.
        self._opening_last_frame=False
        if held_keys["i"]:
            self._opening_last_frame = True

    def toggle_inventories(self):
        # Only show one inventory.
        #SHOW ONLY BIG INVENTORY.
        if self.big_inventory_visible:
            self.small_menu.disable()
            self.big_menu.enable()
        #SHOW ONLY SMALL INVENTORY.
        else:
            self.small_menu.enable()
            self.big_menu.disable()

    def update(self):
        self.check_if_toggle()
        self.toggle_inventories()
        if not self.big_inventory_visible:
            self.small_menu.check_slot_focused()
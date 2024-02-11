from ursina import held_keys, camera, Entity, Animation, window, Sequence
from ursina.ursinamath import Vec2, Vec3


class Inventory(Entity):
    def __init__(self):
        super().__init__()
        """
        The inventory works quite like in minecraft,
        you've got one grid of squares, in each square you can have one item
        stacking upwards towards 16 before a new square is filled.
        You've also got a smaller inv for quick-switching items.
        When I is pressed the big inventory is shown, else the smaller one is shown.
        """

        # INIT BIG INVENTORY.
        self.MAX_STACK_SIZE = 16
        self.GRID_Y = 10
        self.GRID_X = 15

        self.main_inventory = Entity(
            parent = camera.ui,
            model="quad",
            texture = "textures/hud/inventory/static.png"
        )

        self.big_inventory_visible = False

        # INIT MINI QUICK INVENTORY.
        self.mini_offset_x = 0
        self.mini_offset_y = 0.08
        self.MINI_GRID_X = 10
        self.selected_item_index = 0
        self.quick_inv = Entity(
            parent=camera.ui,
            position=Vec2(window.bottom.x+self.mini_offset_x, window.bottom.y+self.mini_offset_y),
            texture="textures/hud/inventory/mini_inv.png",
            model="quad",
            scale_x = 0.8,
            scale_y = 0.15
            )
        
        item_holder_distance = self.quick_inv.scale_x/12
        item_holder_scale = (self.quick_inv.scale_x - item_holder_distance*2)/self.MINI_GRID_X
        self.quick_inv_items = [
            Entity(
                model="quad",
                texture="textures/hud/inventory/item_holder.png" if i != self.selected_item_index else "textures/hud/inventory/item_holder_selected.png",
                parent=camera.ui,
                scale_x = item_holder_scale,
                scale_y = min(4/9 * self.quick_inv.scale_y,item_holder_scale),
                position=Vec3(self.quick_inv.position.x-self.quick_inv.scale_x/2+item_holder_distance + item_holder_scale*(i+0.5),self.quick_inv.position.y, z=-0.1)
            ) for i in range(self.MINI_GRID_X)
        ]


    def update(self):
        self.big_inventory_visible=False
        if held_keys["i"]:
            self.big_inventory_visible=True

        #Only show one inventory.
        #Assume the big inv is not to be shown, show lil one.
        self.quick_inv.enabled = True
        self.main_inventory.enabled = False
        for item in self.quick_inv_items: item.enabled = True
        # If it is to be, then show big inv and not lil one.
        if self.big_inventory_visible:
            self.quick_inv.enabled = False
            self.main_inventory.enabled = True
            for item in self.quick_inv_items: item.enabled = False

        else:
            #Select quick item for mini inventory.
            #Get all numbers keys pressed.
            selected_quick = [key for key in held_keys.keys() if key.isdigit() and held_keys[key]]
            #If any is pressed.
            if len(selected_quick)!= 0:
                #Choose just one of them.
                selected_quick=selected_quick[0]
                #The quick items are represented as in the keyboard -> 0 'should' be 10.
                if selected_quick=="0":
                    selected_quick="10"
                selected_quick=int(selected_quick)
                #We only want to be able to select quick item index that is inside the number of quick items.
                if selected_quick<=self.MINI_GRID_X:
                    self.quick_inv_items[self.selected_item_index].texture="textures/hud/inventory/item_holder.png"
                    self.selected_item_index=selected_quick-1
                    self.quick_inv_items[self.selected_item_index].texture="textures/hud/inventory/item_holder_selected.png"
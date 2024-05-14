from ursina import (
    Entity,
    camera,
    time,
    held_keys,
    BoxCollider,
    Animation,
    mouse,
    Animator,
)
from ursina.ursinamath import Vec2, Vec3, distance_2d
from scripts.moving_object import MovingObject
from scripts.hud.inventory import Inventory, InventoryItem
from scripts.objects.item import *

class Player(MovingObject):
    def __init__(self, world, **kwargs):
        super().__init__(**kwargs)
        self.scale = 1
        self.collider = BoxCollider(self, center=(0, 0, 0), size=(0.5, 0.7, 0))
        self.double_sided = True
        self.inventory = Inventory(player=self)
        self.world = world
        self.PUNCHING_RANGE = 4
        self.holding_item = Entity(enabled=False)

        self.animator = Animator(
            animations={
                "idle": Animation(
                    "textures/player/idle/sprite",
                    fps=6,
                    autoplay=True,
                    loop=True,
                    parent=self,
                    scale=self.scale,
                ),
                "up_jump": Animation(
                    "textures/player/jump/up/sprite",
                    fps=6,
                    autoplay=True,
                    loop=True,
                    parent=self,
                    scale=self.scale,
                ),
                "down_jump": Animation(
                    "textures/player/jump/down/sprite",
                    fps=6,
                    autoplay=True,
                    loop=True,
                    parent=self,
                    scale=self.scale,
                ),
                "running": Animation(
                    "textures/player/running/sprite",
                    fps=6,
                    autoplay=True,
                    loop=True,
                    parent=self,
                    scale=self.scale,
                ),
            }
        )
        self.animator.state = "idle"

    def update(self):
        camera.position = (
            self.world_position.x,
            self.world_position.y + 1.5 * self.scale.y,
            camera.position.z,
        )
        self.handle_movement()
        self.update_vel()
        self.collisions()
        self.update_pos()
        self.hold_item()

    def handle_movement(self):
        # We don't want to show animations mid air for x movement.
        if self.velocity.y == 0:
            if held_keys["space"]:
                self.velocity = Vec2(self.velocity.x, 4)
            elif held_keys["d"]:
                self.animator.state = "running"
                self.velocity = Vec2(1, self.velocity.y)
                self.scale = Vec3(abs(self.scale.x), self.scale.y, self.scale.z)
            elif held_keys["a"]:
                self.velocity = Vec2(-1, self.velocity.y)
                self.scale = Vec3(-1 * abs(self.scale.x), self.scale.y, self.scale.z)
                self.animator.state = "running"
            else:
                self.animator.state = "idle"
                self.velocity = Vec3(0, self.velocity.y, 0)
            
        # Change animation for jumping and such.
        if self.velocity.y > 0:
            self.animator.state = "up_jump"
        elif self.velocity.y < 0:
            self.animator.state = "down_jump"

    def hold_item(self):
        """This makes the player hold the item that is selected in the quick menu,"""
        selected_item_slot = self.inventory.small_menu.inventory_items[self.inventory.small_menu.selected_item_index]
        if hasattr(selected_item_slot, "item_data"):
            if "category" in selected_item_slot.item_data.keys():
                match selected_item_slot["category"]:
                    case "food":
                        self.holding_item = Food(selected_item_slot["texture"], selected_item_slot["offset"], selected_item_slot, 0, 0, selected_item_slot["scale"], selected_item_slot["health_increase"], self)
                    case "handheld_weapons":
                        self.holding_item = HandheldWeapon(selected_item_slot["texture"], selected_item_slot["offset"], selected_item_slot, 0, 360, selected_item_slot["scale"], selected_item_slot["attack_range"], selected_item_slot["swing_time"], selected_item_slot["swing_reload_time"], selected_item_slot["attack_damage"],selected_item_slot["swing_rotation_max"],self)
                    case "guns":
                        self.holding_item = Gun(selected_item_slot["texture"], selected_item_slot["offset"], selected_item_slot, 0, 360, selected_item_slot["scale"], self, selected_item_slot["mag_size"], selected_item_slot["reload_time"],selected_item_slot["fire_rate"],selected_item_slot["bullet_scale"],selected_item_slot["bullet_texture"],selected_item_slot["bullet_offset"], selected_item_slot["bullet_damage"])
                    case "building_structures":
                        self.holding_item = BuildingStructure(selected_item_slot["texture"], selected_item_slot["offset"], selected_item_slot, 0, 0, selected_item_slot["scale"], self, selected_item_slot["health"], selected_item_slot["buildling_range"], selected_item_slot["building_data"])
                    case _:
                        self.holding_item = HoldingItem(selected_item_slot["texture"], selected_item_slot["offset"], selected_item_slot, 0, 0, selected_item_slot["scale"])
            else:
                self.holding_item=Entity(enabled=False)
        else:
            self.holding_item=Entity(enabled=False)
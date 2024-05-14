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
    def __init__(self, world, max_health=100, **kwargs):
        super().__init__(**kwargs)
        self.scale = 1
        self.collider = BoxCollider(self, center=(0, 0, 0), size=(0.5, 0.7, 0))
        self.double_sided = True
        self.health = max_health
        self.MAX_HEALTH = max_health
        self.inventory = Inventory(player=self)
        self.world = world
        self.PUNCHING_RANGE = 4
        self.holding_item = Entity(enabled=False)
        self.prev_holding_item_type = ""

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
        self.health = min(self.health,self.MAX_HEALTH)
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
        if selected_item_slot.item_type == self.prev_holding_item_type:
            return
        destroy(self.holding_item)
        if hasattr(selected_item_slot, "item_data") and selected_item_slot.num_items_slot>0:
            if "category" in selected_item_slot.item_data.keys():
                match selected_item_slot.item_data["category"]:
                    case "food":
                        self.holding_item = Food(
                            texture=selected_item_slot.item_data["texture"],
                              offset=selected_item_slot.item_data["offset"],
                                inventory_slot=selected_item_slot,
                                  min_angle=0,
                                    max_angle=0,
                                      size=selected_item_slot.item_data["scale"],
                                        hp_increase=selected_item_slot.item_data["health_increase"],
                                          player=self)
                    case "handheld_weapons":
                        self.holding_item = HandheldWeapon(
                            texture=selected_item_slot.item_data["texture"],
                              offset=selected_item_slot.item_data["offset"],
                                inventory_slot=selected_item_slot,
                                  min_angle=0,
                                    max_angle=360,
                                      size=selected_item_slot.item_data["scale"],
                                        attack_range=selected_item_slot.item_data["attack_range"],
                                          swing_time=selected_item_slot.item_data["swing_time"],
                                            swing_reload_time=selected_item_slot.item_data["swing_reload_time"],
                                              attack_damage=selected_item_slot.item_data["attack_damage"],
                                              rotation_max=selected_item_slot.item_data["swing_rotation_max"],
                                              player=self)
                    case "guns":
                        self.holding_item = Gun(selected_item_slot.item_data["texture"], selected_item_slot.item_data["offset"], selected_item_slot, 0, 360, selected_item_slot.item_data["scale"], self, selected_item_slot["mag_size"], selected_item_slot["reload_time"],selected_item_slot["fire_rate"],selected_item_slot.item_data["bullet_scale"],selected_item_slot.item_data["bullet_texture"],selected_item_slot.item_data["bullet_offset"], selected_item_slot.item_data["bullet_damage"])
                    case "building_structures":
                        self.holding_item = BuildingStructure(selected_item_slot.item_data["texture"], selected_item_slot.item_data["offset"], selected_item_slot, 0, 0, selected_item_slot["scale"], self, selected_item_slot.item_data["health"], selected_item_slot.item_data["buildling_range"], selected_item_slot.item_data["building_data"])
                    case "":
                        destroy(self.holding_item)
                    case _:
                        self.holding_item = HoldingItem(selected_item_slot.item_data["texture"], selected_item_slot.item_data["offset"], selected_item_slot, 0, 0, selected_item_slot.item_data["scale"])
            else:
                destroy(self.holding_item)
        else:
            destroy(self.holding_item)
        self.prev_holding_item_type=selected_item_slot.item_type
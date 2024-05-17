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
from scripts.hud.player_hp import PlayerHealthBar


###
# PLAYER OBJECTC.
###
class Player(MovingObject):
    def __init__(self, world, max_health=100, walking_speed=1.25, running_speed=2,  **kwargs):
        #INIT TEXTURE AND SUCH.
        super().__init__(**kwargs)
        self.scale = 1
        self.collider = BoxCollider(self, center=(0, 0, 0), size=(0.5, 0.7, 0))
        self.double_sided = True
        #HEALTH
        self.health = max_health*0.8
        self.MAX_HEALTH = max_health
        #INVENTORY
        self.inventory = Inventory(player=self)
        #WORLD
        self.world = world
        #ITEM HOLDING DATA.
        self.holding_item = Entity(enabled=False)
        self.prev_holding_item_type = ""
        #HEALTH BAR
        self.health_bar = PlayerHealthBar(player=self)
        #MOVEMENT SPEED.
        self.walking_speed = walking_speed
        self.running_speed = running_speed


        #CHANGE BETWEEN ANIMATIONS.
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


    #UPDATE THE PLAYER'S INFORMATION.
    def update(self):
        #MAKE CAMERA FOLLOW PLAYER.
        camera.position = (
            self.world_position.x,
            self.world_position.y + 1.5 * self.scale.y,
            camera.position.z,
        )
        #UPDATE HEALTH TO ENSURE UNDER MAX HEALTH.
        #UNDER 0 IS NOT REQUIRED AS PLAYER IS MOVINGOBJECT AND GETS DELETED IF UNDER 0 HEALTH.
        self.health = min(self.health,self.MAX_HEALTH)
        #HANDLE MOVEMENT AND COLLISIONS
        self.handle_movement()
        self.update_vel()
        self.collisions()
        self.update_pos()
        #HANDLE HOLDING ITEM.
        self.hold_item()


    #HANDLE MOVEMENT INPUT.
    def handle_movement(self):
        # NO MOVEMENT IN AIR. REALISTIC FACTOR.
        if self.velocity.y == 0:
            if held_keys["space"]:
                self.velocity = Vec2(self.velocity.x, 6)
            elif held_keys["d"]:
                self.animator.state = "running"
                self.velocity = Vec2(self.walking_speed, self.velocity.y)
                if held_keys["shift"]:
                  self.velocity = Vec2(self.running_speed, self.velocity.y)
                self.scale = Vec3(abs(self.scale.x), self.scale.y, self.scale.z)
            elif held_keys["a"]:
                self.velocity = Vec2(-self.walking_speed, self.velocity.y)
                if held_keys["shift"]:
                  self.velocity = Vec2(-self.running_speed, self.velocity.y)
                self.scale = Vec3(-1 * abs(self.scale.x), self.scale.y, self.scale.z)
                self.animator.state = "running"
            else:
                self.animator.state = "idle"
                self.velocity = Vec3(0, self.velocity.y, 0)
            
        # CHANGE ANIMATION FOR IN AIR.
        if self.velocity.y > 0:
            self.animator.state = "up_jump"
        elif self.velocity.y < 0:
            self.animator.state = "down_jump"


    # HOLD THE ITEM SELECTED IN THE QUICK (SMALL) MENU.
    def hold_item(self):
        selected_item_slot = self.inventory.small_menu.inventory_items[self.inventory.small_menu.selected_item_index]
        #IF THE SELECTED HOLDING ITEM HASN'T CHANGE - NO NEED FOR UPDATING HOLDING ITEM.
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
                        self.holding_item = Gun(
                            selected_item_slot.item_data["texture"],
                              selected_item_slot.item_data["offset"],
                                selected_item_slot,
                                  0,
                                    360,
                                      selected_item_slot.item_data["scale"],
                                        self, selected_item_slot["mag_size"],
                                          selected_item_slot["reload_time"],
                                          selected_item_slot["fire_rate"],
                                          selected_item_slot.item_data["bullet_scale"],
                                          selected_item_slot.item_data["bullet_texture"],
                                          selected_item_slot.item_data["bullet_offset"],
                                          selected_item_slot.item_data["bullet_damage"])
                    case "building_structures":
                        self.holding_item = BuildingStructure(
                            texture=selected_item_slot.item_data["texture"],
                                offset=selected_item_slot.item_data["offset"],
                                  inventory_slot=selected_item_slot,
                                    min_angle=0,
                                      max_angle=0,
                                        size=selected_item_slot.item_data["scale"],
                                          player=self,
                                            health=selected_item_slot.item_data["building_data"]["health"],
                                              building_range=selected_item_slot.item_data["building_range"],
                                                building_data=selected_item_slot.item_data["building_data"])
                    case "":
                        destroy(self.holding_item)                    
                    case "resource":
                      self.holding_item = HoldingItem(
                          texture=selected_item_slot.item_data["texture"],
                            offset=selected_item_slot.item_data["offset"],
                              inventory_slot=selected_item_slot,
                                min_angle=0,
                                  max_angle=0,
                                    size=selected_item_slot.item_data["scale"],
                                    player=self)
                    case _:
                        self.holding_item = HoldingItem(
                            texture=selected_item_slot.item_data["texture"],
                              offset=selected_item_slot.item_data["offset"],
                                inventory_slot=selected_item_slot,
                                  min_angle=0,
                                    max_angle=0,
                                     size=selected_item_slot.item_data["scale"],
                                     player=self)
            else:
                destroy(self.holding_item)
        else:
            destroy(self.holding_item)
        self.prev_holding_item_type=selected_item_slot.item_type
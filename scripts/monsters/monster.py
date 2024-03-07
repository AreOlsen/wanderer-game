import json
from ursina import Entity, camera, Animator, Animation, BoxCollider
from ursina.ursinamath import Vec2

from numpy import random


class Monster(Entity):
    _monsters = json.load(open(f"scripts/monsters/monsters.json", "r"))

    def __init__(self, position: Vec2):
        super().__init__(position=position)
        # Velg random monster type basert på spawnrates.
        self.monster_type = list(Monster._monsters)[
            random.choice(
                range(len(list(Monster._monsters))),
                p=[
                    monster_type["spawn_chance"]
                    for monster_type in list(Monster._monsters.values())
                ],
            )
        ]
        self.scale_x = Monster._monsters[self.monster_type]["scale"]["x"]
        self.scale_y = Monster._monsters[self.monster_type]["scale"]["y"]
        self.can_shoot = Monster._monsters[self.monster_type]["can_shoot"]
        self.can_melee = Monster._monsters[self.monster_type]["can_melee"]
        self.can_run = Monster._monsters[self.monster_type]["can_run"]
        self.health = Monster._monsters[self.monster_type]["health"]
        collider_center = (Monster._monsters[self.monster_type]["box_collider"]["center"]["x"],
                           Monster._monsters[self.monster_type]["box_collider"]["center"]["y"],
                           0)
        collider_size = (Monster._monsters[self.monster_type]["box_collider"]["size"]["x"],
                         Monster._monsters[self.monster_type]["box_collider"]["size"]["y"],
                         0)
        self.collider = BoxCollider(self,center=collider_center,size=collider_size)
        self.stationary_when_attacking = Monster._monsters[self.monster_type][
            "stationary_when_attacking"
        ]
        self.animator = Animator(
            animations={
                "idle": Animation(
                    Monster._monsters[self.monster_type]["animations"]["idle"],
                    fps=6,
                    autoplay=True,
                    loop=True,
                    parent=self,
                    scale_x=self.scale_x,
                    scale_y=self.scale_y,
                    enabled=False,
                ),
                "walking": Animation(
                    Monster._monsters[self.monster_type]["animations"]["walking"],
                    fps=6,
                    autoplay=True,
                    loop=True,
                    parent=self,
                    scale_x=self.scale_x,
                    scale_y=self.scale_y,
                    enabled=False,
                ),
            }
        )
        #CAN MELEE.
        if self.can_melee:
            self.animator.animations["melee"] = Animation(
                Monster._monsters[self.monster_type]["animations"]["melee"],
                fps=6,
                autoplay=True,
                loop=True,
                parent=self,
                scale_x=self.scale_x,
                scale_y=self.scale_y,
                enabled=False,
            )
        #CAN RUN.
        if self.can_run:
            self.animator.animations["running"] = Animation(
                Monster._monsters[self.monster_type]["animations"]["running"],
                fps=6,
                autoplay=True,
                loop=True,
                parent=self,
                scale_x=self.scale_x,
                scale_y=self.scale_y,
                enabled=False,
            )
        #CAN SHOOT.
        if self.can_shoot:
            self.animator.animations["shooting"] = Animation(
                Monster._monsters[self.monster_type]["animations"]["shooting"],
                fps=6,
                autoplay=True,
                loop=True,
                parent=self,
                scale_x=self.scale_x,
                scale_y=self.scale_y,
                enabled=False,
            )
            self.projectile_texture = Monster._monsters[self.monster_type][
                "projectile"
            ]["texture"]
            self.projectile_speed = Monster._monsters[self.monster_type]["projectile"][
                "speed"
            ]
            self.projectile_rotating = Monster._monsters[self.monster_type][
                "projectile"
            ]["rotating"]
            self.shooting_range = Monster._monsters[self.monster_type][
                "projectile"
            ]["shooting_range"]

        #SET DEFAULT ANIMATION STATE.
        self.animator.state = "idle"

    def update(self):
        print(self.intersects().hit)
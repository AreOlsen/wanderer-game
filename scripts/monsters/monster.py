import json
from ursina import Entity, camera, Animator, Animation, BoxCollider
from ursina.ursinamath import Vec2
from numpy import random

###
# MONSTER CLASS.
# NOT CURRENTLY USED - TO BE IMPLEMENTED IN NEXT UPDATE.
###
class Monster(Entity):
    #ALL MONSTERS' DATA.
    _monsters = json.load(open(f"scripts/monsters/monsters.json", "r"))

    #INIT THE CURRENT MONSTER.
    def __init__(self, position: Vec2):
        super().__init__(position=position)
        #CHOOSE RANDOM MONSTER BASED ON SPAWN RATES.
        self.monster_type = list(Monster._monsters)[
            random.choice(
                range(len(list(Monster._monsters))),
                p=[
                    monster_type["spawn_chance"]
                    for monster_type in list(Monster._monsters.values())
                ],
            )
        ]

        #GET INFORMATION ABOUT THE MONSTER.
        self.scale_x = Monster._monsters[self.monster_type]["scale"]["x"]
        self.scale_y = Monster._monsters[self.monster_type]["scale"]["y"]
        self.can_shoot = Monster._monsters[self.monster_type]["can_shoot"]
        self.can_melee = Monster._monsters[self.monster_type]["can_melee"]
        self.can_run = Monster._monsters[self.monster_type]["can_run"]
        self.health = Monster._monsters[self.monster_type]["health"]

        #SET COLLIDER INFORMATION.
        collider_center = (
            Monster._monsters[self.monster_type]["box_collider"]["center"]["x"],
            Monster._monsters[self.monster_type]["box_collider"]["center"]["y"],
            0,
        )
        collider_size = (
            Monster._monsters[self.monster_type]["box_collider"]["size"]["x"],
            Monster._monsters[self.monster_type]["box_collider"]["size"]["y"],
            0,
        )
        self.collider = BoxCollider(self, center=collider_center, size=collider_size)


        #SET ATTACKING INFORMATION.
        self.stationary_when_attacking = Monster._monsters[self.monster_type][
            "stationary_when_attacking"
        ]

        #SET ANIMATOR DATA.
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


        #IF THE MONSTER CAN MELEE - ADD THE ANIMATION.
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


        #IF MONSTER CAN RUN - ADD THE ANIMATION.
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

        
        #IF MONSTER CAN SHOOT - ADD THE ANIMATION.
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
            self.shooting_range = Monster._monsters[self.monster_type]["projectile"][
                "shooting_range"
            ]


        # SET DEFAULT ANIMATION STATE.
        self.animator.state = "idle"

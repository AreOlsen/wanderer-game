import json
from ursina import Entity, camera, Animator,Animation


class Monster(Entity):
    _monsters = json.load(open(f"scripts/monsters/monsters.json","r"))
    def __init__(self):
        super().__init__()
        self.monster_type = list(self._monsters)[] #FIX: ADD WEIGHTED RANDOMNESS.
        self.scale_x = self._monsters[self.monster_type]["scale"]["x"]
        self.scale_y = self._monsters[self.monster_type]["scale"]["y"]
        self.collider = "mesh"
        self.can_shoot = self._monsters[self.monster_type]["can_shoot"]
        self.can_melee = self._monsters[self.monster_type]["can_melee"]
        self.can_run = self._monsters[self.monster_type]["can_run"]
        self.health = self._monsters[self.monster_type]["health"]
        self.stationary_when_attacking = self._monsters[self.monster_type]["stationary_when_attacking"]

        self.animator = Animator(animations={
            "idle":Animation(
                self._monsters[self.monster_type]["animations"]["idle"],
                fps=6,
                autoplay=True,
                loop=True,
                parent=self,
                scale_x=self.scale_x,
                scale_y=self.scale_y
            ),
            "walking":Animation(
                self._monsters[self.monster_type]["animations"]["walking"],
                fps=6,
                autoplay=True,
                loop=True,
                parent=self,
                scale_x=self.scale_x,
                scale_y=self.scale_y
            )
        })
        self.animator.state = "idle"

        if self.can_melee:
            self.animator.animations["melee"]=Animation(
                self._monsters[self.monster_type]["animations"]["melee"],
                fps=6,
                autoplay=True,
                loop=True,
                parent=self,
                scale_x=self.scale_x,
                scale_y=self.scale_y
            )

        if self.can_run:
            self.animator.animations["running"]=Animation(
                self._monsters[self.monster_type]["animations"]["running"],
                fps=6,
                autoplay=True,
                loop=True,
                parent=self,
                scale_x=self.scale_x,
                scale_y=self.scale_y
            )
    
        if self.can_shoot:
            self.animator.animations["shooting"]=Animation(
                self._monsters[self.monster_type]["animations"]["shooting"],
                fps=6,
                autoplay=True,
                loop=True,
                parent=self,
                scale_x=self.scale_x,
                scale_y=self.scale_y
            )
            self.projectile_texture = self._monsters[self.monster_type]["projectile"]["texture"]
            self.projectile_speed = self._monsters[self.monster_type]["projectile"]["speed"]
            self.projectile_rotating = self._monsters[self.monster_type]["projectile"]["rotating"]

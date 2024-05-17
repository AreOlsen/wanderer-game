from ursina import camera, rgb, window, Texture, camera,Entity
from ursina.prefabs.health_bar import HealthBar
from ursina.ursinamath import Vec3,Vec2

###
# PLAYER HEALTH BAR ENTITY.
###
class PlayerHealthBar(Entity):
    #INIT THE PLAYERHEALTHBAR.
    def __init__(self, player):
        #THE BAR ITSELF.
        self.bar = HealthBar(origin=(0,0),max_value=player.MAX_HEALTH, value=player.health, show_text=True)
        super().__init__()
        #INFORMATION ABOUT THE BAR.
        self.player = player
        self.bar.parent = camera.ui
        self.bar.scale = Vec2(self.scale.x*0.6, self.scale.y*0.02)
        self.bar.position = player.inventory.small_menu.position + Vec2(0,0.065)
    

    #UPDATE THE BAR INFORMATION BASED ON PLAYER HEALTH.
    def update(self):
        #IF PLAYER DOESN'T EXIST - BAR DOESN'T EXIST.
        try:
            self.bar.enabled=self.player.enabled
        except Exception:
            print("Error in updating healthbar enabled/disabled.")

        #UPDATE THE HEALTHBAR VALUE.
        try:
            self.bar.value=max(0,self.player.health)
        except Exception:
            print("Error in updating healthbar value.")
            
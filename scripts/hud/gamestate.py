from ursina import Sprite, Entity, Texture, Button, Audio,camera
from ursina.ursinamath import Vec2, Vec3

###
# STATE CLASS- THIS HOLDS INFORMATION ABOUT THE CURRENT GAME STATE.
# SUCH AS MENU OR GAME STATE.
###
class State(Entity):
    #INIT THE STATE INFORMATION.
    def __init__(self, entities=[],  audio=""):
        super().__init__(entities=entities)
        self.entities=entities
        if len(audio)>0:
            self.background_music = Audio(sound_file_name=audio, loop=True, autoplay=False, parent=self)

    #DISABLE ALL NECESSARY THINGS ON THE STATE DISABLE.
    def on_disable(self):
        #DISABLE ANY ENTITIES IN THE STATE.
        for ent in self.entities:
            ent.enabled=False
        #IF ANY BACK BUTTON IS PRESENT.
        if hasattr(self,"BACK"):
            self.BACK.enabled=False
        #BACKGROUND MUSIC - NOT CURRENTLY IMPLEMENTED - WILL BE USED IN NEXT UPDATE.
        if hasattr(self,"background_music"):
            self.background_music.stop()
            self.background_music.enabled=False
        #DISABLE STATE BACKGROUND.
        if hasattr(self,"background"):
            self.background.enabled=False
        #DISABLE THE STATE ITSELF.
        self.enabled=False

    #ENABLE ALL NECESSARY THINGS ON STATE ENABLE.
    def on_enable(self):
        #ENABLE THE STATE.
        self.enabled=True
        #ENABLE ALL ENTITIES IN THE STATE.
        for ent in self.entities:
            ent.enabled=True
        #ENABLE THE BACK BUTTON IF THERE IS ANY.
        if hasattr(self,"BACK"):
            self.BACK.enabled=True
        #ENABLE BACKGROUND MUSIC - NOT CURRENTLY IMPLEMENTED - WILL BE USED IN NEXT UPDATE.
        if hasattr(self,"background_music"):
            self.background_music.enabled=True
            self.background_music.play(start=0)
        #ENABLE STATE BACKGROUND.
        if hasattr(self,"background"):
            self.background.enabled=True
        

### 
# STATE CHANGER CLASS.
# RESPONSIBLE FOR CHANGING STATES.
###
class Statechanger:
    #INIT THE STATE CHANGER.
    def __init__(self):
        super().__init__()
        self.states = {}


    #CHOOSE THE STATE LOADED IN CURRENTLY.
    def choose_state(self, state_name):
        for i in self.states:
            self.states[i].disable()
        self.states[state_name].enable()

    #ADD ANY STATES WANTED.
    def add_state(self,state,state_name):
        state.enabled=False
        self.states[state_name]=state
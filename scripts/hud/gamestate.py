from ursina import Sprite, Entity, Texture,Button,Audio,camera
from ursina.ursinamath import Vec2, Vec3


class State(Entity):
    """This is a game state."""
    def __init__(self, entities=[],  audio=""):
        super().__init__(entities=entities)
        self.entities=entities
        if len(audio)>0:
            self.background_music = Audio(sound_file_name=audio, loop=True, autoplay=True, parent=self)

    def on_disable(self):
        for ent in self.entities:
            ent.enabled=False
        if hasattr(self,"BACK"):
            self.BACK.enabled=False
        if hasattr(self,"background_music"):
            self.background_music.enabled=False
        if hasattr(self,"background"):
            self.background.enabled=False
        self.enabled=False

    def on_enable(self):
        self.enabled=True
        for ent in self.entities:
            ent.enabled=True
        if hasattr(self,"BACK"):
            self.BACK.enabled=True
        if hasattr(self,"background_music"):
            self.background_music.enabled=True
        if hasattr(self,"background"):
            self.background.enabled=True
        
class Statechanger:
    def __init__(self):
        super().__init__()
        self.states = {}

    def choose_state(self, state_name):
        for i in self.states:
            self.states[i].disable()
        self.states[state_name].enable()

    def add_state(self,state,state_name):
        state.enabled=False
        self.states[state_name]=state
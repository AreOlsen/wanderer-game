from ursina import Entity, Button,camera, Text, Texture, application, InputField, color, ButtonGroup
from ursina.ursinamath import Vec3
from scripts.hud.gamestate import State
from scripts.world.world import World
from scripts.world.background import Background
from scripts.characters.player import Player
from scripts.hud.mini_map import Minimap


###
# REDIRECT TO ANOTHER STATE BUTTON.
###
class RedirectButton(Entity):
    def __init__(self, texture, to_state, state_changer, scale_x=0.3, scale_y=0.1, text="aaaa", font="textures/fonts/monocraft.ttf"):
        super().__init__(model="quad",collider="box",texture=texture)
        self.text = Text(text=text, size=0.3, scale_x=0.6,scale_y=1.2, parent=self, position=Vec3(0,0,0), origin=(0,0), font=font)
        self.origin = (0,0)
        self.scale_x=scale_x
        self.scale_y=scale_y
        self.state_changer = state_changer
        self.to_state = to_state

    def on_click(self):
        self.state_changer.choose_state(self.to_state)


###
# QUIT GAME BUTTON.
###
class QuitButton(Entity):
    def __init__(self, texture, scale_x=0.3, scale_y=0.1, text="Quit", font="textures/fonts/monocraft.ttf"):
        super().__init__(model="quad",collider="box",texture=texture)
        self.text = Text(text=text, size=0.3, scale_x=0.6,scale_y=1.2, parent=self, position=Vec3(0,0,0), origin=(0,0), font=font)
        self.origin = (0,0)
        self.scale_x=scale_x
        self.scale_y=scale_y
    
    #QUIT.
    def on_click(self):
        application.quit()


###
# LOAD GAME FROM FILE BUTTON.
###
class LoadGameButton(Entity):
    def __init__(self, texture, save_name, state_changer, scale_x=0.3, scale_y=0.1, text="Save 1", font="textures/fonts/monocraft.ttf"):
        super().__init__(model="quad",collider="box",texture=texture)
        self.text = Text(text=text, size=0.3, scale_x=0.6,scale_y=1.2, parent=self, position=Vec3(0,0,0), origin=(0,0), font=font)
        self.origin = (0,0)
        self.scale_x=scale_x
        self.scale_y=scale_y
        self.state_changer = state_changer
        self.save_name=save_name

    def on_click(self):
        self.state_changer.states["game"]=State()
        w = World(save_name=self.save_name,background=Background(100,0.5,0.9999))
        p = Player(world_position=Vec3(0,35,0), world=w)
        m = Minimap(player=p)
        p.minimap = m
        w.player=p
        self.state_changer.states["game"].entities.append(w)
        self.state_changer.states["game"].entities[0].load_world()
        self.state_changer.choose_state("game")


###
# NEW GAME FROM GAME INFORMATION BUTTON.
###
class NewGameButton(Entity):
    def __init__(self, texture, save_name_ref, seed_ref, difficulty_ref, state_changer, scale_x=0.3, scale_y=0.1, text="Start", font="textures/fonts/monocraft.ttf"):
        super().__init__(model="quad",collider="box",texture=texture)
        self.text = Text(text=text, size=0.3, scale_x=0.6,scale_y=1.2, parent=self, position=Vec3(0,0,0), origin=(0,0), font=font)
        self.origin = (0,0)
        self.scale_x=scale_x
        self.scale_y=scale_y
        self.state_changer = state_changer
        self.save_name_ref=save_name_ref
        self.seed_ref = seed_ref
        self.difficulty_ref = difficulty_ref


    #GENERATE WORLD.
    def on_click(self):
        #Create game state.
        self.state_changer.states["game"]=State()

        #PURIFY SEED.
        _seed = "0"
        for char in self.seed_ref.text:
            if char.isdigit():
                _seed+=char
            else:
                _seed+="0"
        _seed=int(_seed)
        _save_name=self.save_name_ref.text
        _difficulty=self.difficulty_ref.value

        #Create the world.
        world=World(save_name=_save_name,background=Background(100,0.5,0.9999), seed=_seed,difficulty=_difficulty)
        player=Player(world_position=Vec3(0,35,0), world=world)
        world.player=player
        minimap = Minimap(player=player)
        player.minimap = minimap
        self.state_changer.states["game"].entities.append(world)
        self.state_changer.choose_state("game")


###
# TEXT INPUT "BUTTON" FIELD.
###
class InputButtonField(InputField):
    def __init__(self, texture, scale_x=0.3, scale_y=0.1, text="Input", font="textures/fonts/monocraft.ttf"):
        super().__init__(model="quad",collider="box",texture=texture, character_limit=24, text=text, default_value=text, font=font)
        self.color = color.white
        self.highlight_color = color.white
        self.pressed_color = color.white	
        self.origin = (0,0)
        self.scale_x=scale_x
        self.scale_y=scale_y


### 
# MULTIPLE CHOICE BUTTON GROUP.
###
class ButtonChoice(ButtonGroup):
    def __init__(self, choices, texture, min_choice, max_choice, font="textures/fonts/monocraft.ttf",scale_x=0.3, scale_y=0.1,):
        super().__init__(options=choices,spacing=(0,0,0),texture=texture, character_limit=24, font=font, scale_x=scale_x, scale_y=scale_y, origin=(0,0,0), position=Vec3(0,0,-1))
        for i in self.buttons:
            i.model="quad"
            i.texture = texture
            i.pressed_color = color.white
            i.highlight_color = color.white
            i.color = color.white
            i.scale_x=scale_x*4.3
            i.scale_y=scale_y*8
            i.text_color=color.white
            i.position = Vec3(i.position.x/1.5,i.position.y,i.position.z)
        self.color = color.white
        self.deselected_color = color.white
        self.selected_color = color.blue
        self.highlight_color = color.white
        self.pressed_color = color.white	
        self.origin = (0,0)
        self.scale_x=scale_x
        self.scale_y=scale_y

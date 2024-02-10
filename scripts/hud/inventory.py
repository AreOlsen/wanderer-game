from ursina import held_keys


class Inventory:

    def __init__(self):
        """
        The inventory works quite like in minecraft,
        you've got one grid of squares, in each square you can have one item
        stacking upwards towards 64 before a new square is filled.
        """
        self.MAX_STACK_SIZE = 64
        self.GRID_Y = 10
        self.GRID_X = 15
        self.IN_INVENTORY = False

    def update(self):
        if held_keys["i"]:
            self.IN_INVENTORY = True
        else:
            self.IN_INVENTORY = False

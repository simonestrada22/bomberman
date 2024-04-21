# items/powerup.py

import random
from items.item import Item

class Powerup(Item):
    def __init__(self, node):
        super().__init__(node)
        self.type = random.choice(['extra_bomb', 'extra_life'])

    def apply_powerup(self, entity):
        if self.type == 'extra_bomb':
            entity.max_bombs += 1
        elif self.type == 'extra_life':
            entity.lives += 1
        self.node.item = None

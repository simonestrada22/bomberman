# entities/player.py

from entities.entity import Entity


class Player(Entity):
    def __init__(self, node, lives=3, name='Player'):
        super().__init__(node, lives)
        self.name = name

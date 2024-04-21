# entities/enemy.py

from random import choice
from items.bomb import Bomb
from entities.entity import Entity
from entities.player import Player

class Enemy(Entity):
    def __init__(self, node, lives=2):
        super().__init__(node, lives)
        self.directions = ['up', 'down', 'left', 'right']

    def move_randomly(self):
        valid_directions = []
        for direction in self.directions:
            neighbor = self.node.neighbors[direction]
            if neighbor and neighbor.state != 'wall' and not neighbor.entity and not (isinstance(neighbor.item, Bomb)):
                valid_directions.append(direction)

        if valid_directions:
            direction = choice(valid_directions)
            self.move(direction)

    def place_bomb_if_needed(self, game_map):
        for direction in self.node.neighbors:
            neighbor = self.node.neighbors[direction]
            if neighbor and (isinstance(neighbor.entity, Player) or neighbor.state == 'barrier'):
                self.place_bomb(game_map)
                break

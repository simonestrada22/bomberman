# entities/entity.py

import time
from items.bomb import Bomb

class Entity:
    def __init__(self, node, lives=3):
        self.node = node
        self.lives = lives
        self.last_bomb_time = 0
        self.max_bombs = 1
        self.active_bombs = []

    def move(self, direction):
        neighbor = self.node.neighbors[direction]
        if neighbor and neighbor.state != 'wall' and neighbor.state != 'barrier':
            self.node.entity = None
            self.node = neighbor
            neighbor.entity = self

    def place_bomb(self, map_obj):
        current_time = time.time()
        # Check if the number of active bombs is less than the max bombs
        if len(self.active_bombs) < self.max_bombs:
            bomb = Bomb(self.node, self)
            map_obj.add_item(bomb)
            self.last_bomb_time = current_time
            bomb.set_explosion_frames(current_time)
            self.active_bombs.append(bomb)

    def decrease_active_bombs(self, bomb):
        self.active_bombs.remove(bomb)

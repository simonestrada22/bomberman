# entities/bomb.py

import time

class Bomb:
    def __init__(self, node, explosion_time=3):
        self.node = node
        self.explosion_time = explosion_time
        self.placed_time = time.time()

    def explode(self):
        # Explode the bomb
        pass

    def is_exploded(self):
        # Check if the bomb has exploded
        return time.time() - self.placed_time >= self.explosion_time
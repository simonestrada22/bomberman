# items/bomb.py

import time
from items.item import Item

class Bomb(Item):
    def __init__(self, node):
        super().__init__(node)
        self.placement_time = time.time()  # Store the time when the bomb was placed
        self.explosion_frames = []

    def set_explosion_frames(self, placement_time):
        self.placement_time = placement_time
        # self.explosion_frames = ['*', '+', 'x', '.', ' ']
        self.explosion_frames = ['💥', '💣', ' ']

    def tick(self):
        pass  # You can implement ticking functionality if needed

    def should_explode(self):
        current_time = time.time()
        return current_time - self.placement_time >= 3 and self.explosion_frames
    

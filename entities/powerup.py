# entities/powerup.py

import random

class Powerup:
    POWERUPS = ["shield", "bomb_range", "velocity", "bomb_capacity"]

    def __init__(self, node):
        self.node = node
        self.type = random.choice(self.POWERUPS)

    def apply_powerup(self, player):
        if self.type == "shield":
            player.activate_shield()
        elif self.type == "bomb_range":
            player.increase_bomb_range()
        elif self.type == "velocity":
            player.increase_velocity()
        elif self.type == "bomb_capacity":
            player.increase_bomb_capacity()

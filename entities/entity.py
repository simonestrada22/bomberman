# entities/entity.py

class Entity:
    def __init__(self, node):
        self.node = node
        self.lives = 3
        self.velocity = 1
        self.shield_active = False
        self.bomb_range = 1
        self.bombs_left = 1

    def move(self, direction):
        # Update entity position based on the direction of movement

        if direction == "up" and self.node.up:
            self.node = self.node.up
        elif direction == "down" and self.node.down:
            self.node = self.node.down
        elif direction == "left" and self.node.left:
            self.node = self.node.left
        elif direction == "right" and self.node.right:
            self.node = self.node.right

    def place_bomb(self):
        # Place a bomb at the entity current position
        pass

    def take_damage(self):
        # Reduce player's lives when hit by a bomb explosion
        self.lives -= 1

    def activate_shield(self):
        # Activate shield power-up
        self.shield_active = True

    def deactivate_shield(self):
        # Deactivate shield power-up
        self.shield_activate = False

    def increase_bomb_range(self):
        # Increase bomb range when picking up power-up
        self.bomb_range += 1

    def increase_velocity(self):
        # Increase player velocity when picking up power-up
        self.velocity += 1

    def increase_bomb_capacity(self):
        self.bombs_left += 1

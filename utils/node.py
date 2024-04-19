# utils/node.py

class Node:
    def __init__(self, state):
        self.state = state
        self.entity = None  # Entity occupying this node (player, enemy, or None)
        self.item = None    # Item occupying this node (powerup, bomb, or None)
        # List of neighboring nodes
        self.neighbors = {'up': None, 'down': None, 'left': None, 'right': None}

    def add_neighbor(self, direction, node):
        self.neighbors[direction] = node

    def remove_neighbor(self, direction):
        self.neighbors[direction] = None
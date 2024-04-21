# maps/map.py
from items.powerup import Powerup
from utils.doubly_linked_list import DoublyLinkedList
from utils.node import Node
import random

class Map:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.map_list = DoublyLinkedList()
        self.entities = []
        self.items = []
        self.create_map()

    def create_map(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if row == 0 or row == self.rows - 1 or col == 0 or col == self.cols - 1:
                    state = 'wall'  # Create walls around the edges of the map
                elif row % 2 == 0 and col % 2 == 0:
                    state = 'wall'  # Create walls at every even position
                else:
                    state = 'free'  # All other positions are initially free

                if state == 'free' and random.random() < 0.2:  # 20% chance of placing a barrier
                    state = 'barrier'

                node = Node(state)
                node.row = row
                node.col = col
                self.map_list.append(node)

        self.connect_neighbors()
        self.place_powerups()

    def connect_neighbors(self):
        current_node = self.map_list.head
        while current_node:
            node = current_node.node
            row, col = node.row, node.col
            if node.state != 'wall':
                up = self.get_node(row - 1, col)
                down = self.get_node(row + 1, col)
                left = self.get_node(row, col - 1)
                right = self.get_node(row, col + 1)

                if up:
                    node.add_neighbor('up', up)
                if down:
                    node.add_neighbor('down', down)
                if left:
                    node.add_neighbor('left', left)
                if right:
                    node.add_neighbor('right', right)

            current_node = current_node.next

    def add_entity(self, entity):
        self.entities.append(entity)
        entity.node.entity = entity

    def add_item(self, item):
        self.items.append(item)
        item.node.item = item

    def move_entity(self, entity, direction):
        neighbor = entity.node.neighbors[direction]
        if neighbor and neighbor.state != 'wall' and not neighbor.entity:
            entity.node.entity = None
            entity.node = neighbor
            neighbor.entity = entity

    def get_node(self, row, col):
        current_node = self.map_list.head
        while current_node:
            node = current_node.node
            if node.row == row and node.col == col:
                return node
            current_node = current_node.next
        return None
    
    def get_random_free_node(self):
        current_node = self.map_list.head
        free_nodes = []
        while current_node:
            node = current_node.node
            if node.state == 'free' and not node.entity and not node.item:
                free_nodes.append(node)
            current_node = current_node.next
        return random.choice(free_nodes) if free_nodes else None

    def place_powerups(self):
        for _ in range(int(self.rows * self.cols * 0.01)):
            node = self.get_random_free_node()
            if node:
                powerup = Powerup(node)
                self.add_item(powerup)

    def print_map(self):
        current_node = self.map_list.head
        while current_node:
            node = current_node.node
            if node.state == 'wall':
                print('#', end=' ')
            elif node.state == 'barrier':
                print('X', end=' ')
            else:
                print(' ', end=' ')
            if node.col == self.cols - 1:
                print()
            current_node = current_node.next

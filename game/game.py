# game/game.py

import os
import csv
import time
import curses
import random
from entities.player import Player
from entities.enemy import Enemy
from maps.map import Map
from items.bomb import Bomb
from items.powerup import Powerup
from .scoreboard import save_score, display_scoreboard

class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.player_name = ""

    def init_game(self):
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Wall color pair
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Barrier color pair
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Bomb color pair
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)  # Powerup color pair

        HEIGHT, WIDTH = self.stdscr.getmaxyx()

        # Add title
        title = "Bomberman created by Miguel Cárdenas"
        self.stdscr.addstr(0, int((WIDTH - len(title)) / 2), title, curses.A_BOLD)

        # Add menu options
        menu_options = ["Play", "Scoreboard", "Exit"]
        selected_option = 0

        while True:
            self.stdscr.clear()

            for i, option in enumerate(menu_options):
                if i == selected_option:
                    self.stdscr.addstr(2 + i, int((WIDTH - len(option)) / 2), option, curses.color_pair(1) | curses.A_REVERSE)
                else:
                    self.stdscr.addstr(2 + i, int((WIDTH - len(option)) / 2), option)

            self.stdscr.refresh()

            key = self.stdscr.getch()

            if key == curses.KEY_UP:
                selected_option = (selected_option - 1) % len(menu_options)
            elif key == curses.KEY_DOWN:
                selected_option = (selected_option + 1) % len(menu_options)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if selected_option == 0:
                    if not self.player_name:
                        self.player_name = self.get_player_name()
                    self.start_game()
                elif selected_option == 1:
                    display_scoreboard(self.stdscr)
                elif selected_option == 2:
                    curses.endwin()
                    quit()

    def get_player_name(self):
        self.stdscr.clear()
        self.stdscr.addstr(2, 2, "Enter your name: ")
        curses.echo()
        player_name = self.stdscr.getstr(2, 20).decode(encoding="utf-8").strip()
        curses.noecho()
        return player_name

    def start_game(self):
        # Initialize the game
        curses.curs_set(0)      # Hide cursor
        self.stdscr.nodelay(True)    # Make non-blocking input
        self.stdscr.clear()

        # Create map
        game_map = Map(rows=20, cols=80)

        # Create player
        player = Player(game_map.get_node(1, 1)) # Create player at position (1, 1)
        if not self.player_name:  # If player name is not set, prompt for it
            player.name = self.get_player_name()
            self.player_name = player.name
        else:
            player.name = self.player_name
        game_map.add_entity(player)

        # Create enemies
        num_enemies = 4
        for _ in range(num_enemies):
            enemy_node = game_map.get_random_free_node()
            enemy = Enemy(enemy_node, lives=2)
            game_map.add_entity(enemy)

        start_time = time.time()
        enemy_move_delay = 0.33
        last_enemy_move_time = time.time()

        # Game loop
        while True:
            # Update game state
            self.handle_input(player, game_map)

            current_time = time.time()
            if current_time - last_enemy_move_time >= enemy_move_delay:
                for entity in game_map.entities:
                    if isinstance(entity, Enemy):
                        entity.move_randomly()
                        entity.place_bomb_if_needed(game_map)
                last_enemy_move_time = current_time

            # Render game
            self.render_game(game_map, player, start_time=start_time)

            if not any(isinstance(entity, Enemy) for entity in game_map.entities):
                elapsed_time = time.time() - start_time
                save_score(player.name, elapsed_time)
                quit()

    def handle_input(self, player, game_map):
        key = self.stdscr.getch()

        if key == ord('q'):
            curses.endwin()
            quit()

        if key == ord('w'):
            player.move('up')
        elif key == ord('s'):
            player.move('down')
        elif key == ord('a'):
            player.move('left')
        elif key == ord('d'):
            player.move('right')
        elif key == ord('b'):
            player.place_bomb(game_map)

        for item in game_map.items:
            if isinstance(item, Bomb):
                if item.should_explode():
                    self.explode_bomb(item, game_map)

        for entity in game_map.entities:
            if entity.node.item and isinstance(entity.node.item, Powerup):
                entity.node.item.apply_powerup(entity)
                entity.node.item = None

    def explode_bomb(self, bomb, game_map):
        node = bomb.node
        explosion_frames = ['💥', '💣', ' ']
        explosion_duration = 0.5  # Duration of the explosion in seconds

        for direction in node.neighbors:
            neighbor = node.neighbors[direction]
            if neighbor and neighbor.state == "barrier":
                neighbor.state = "free"
                if random.random() < 0.05:
                    powerup = Powerup(neighbor)
                    game_map.add_item(powerup)
            if neighbor and neighbor.entity:
                self.kill_entity(neighbor.entity, game_map, neighbor)

        if node.entity:
            self.kill_entity(node.entity, game_map, node)

        game_map.add_explosion(node, explosion_frames, bomb.placement_time, explosion_duration)

        game_map.items.remove(bomb)
        bomb.node.item = None
        bomb.placed_by.decrease_active_bombs(bomb)

    def kill_entity(self, entity, game_map, node):
        if node.entity:
            if isinstance(node.entity, Player):
                entity.lives -= 1
                entity.node.entity = None
                entity.node = game_map.get_node(1, 1)
                game_map.add_entity(entity)
                if entity.lives == 0:
                    curses.endwin()
                    quit()
            elif isinstance(node.entity, Enemy):
                entity.lives -= 1
                entity.node.entity = None
                entity.node = game_map.get_random_free_node()

                if entity.lives == 0:
                    game_map.entities.remove(entity)

    def render_game(self, game_map, player, start_time):
        self.stdscr.clear()

        current_time = time.time()
        enemies = [entity for entity in game_map.entities if isinstance(entity, Enemy)]
        bombs = [item for item in game_map.items if isinstance(item, Bomb)]

        for row in range(game_map.rows):
            for col in range(game_map.cols):
                node = game_map.get_node(row, col)
                if node.state == 'wall':
                    self.stdscr.addstr(row, col, '#', curses.color_pair(1))
                elif node.state == 'barrier':
                    self.stdscr.addstr(row, col, 'X', curses.color_pair(2))
                elif node.entity:
                    if isinstance(node.entity, Player):
                        self.stdscr.addstr(row, col, '👾')
                    elif isinstance(node.entity, Enemy):
                        self.stdscr.addstr(row, col, '🤖')
                elif node.item:
                    if isinstance(node.item, Bomb):
                        self.stdscr.addstr(row, col, '💣', curses.color_pair(3))
                    elif isinstance(node.item, Powerup):
                        self.stdscr.addstr(row, col, 'o', curses.color_pair(4))
                    else:
                        self.stdscr.addstr(row, col, '💣')

        # Render active explosions and remove them after a certain duration
        for explosion in game_map.explosions:
            node = explosion['node']
            frames = explosion['frames']
            start_time = explosion['start_time']
            duration = explosion['duration']
            elapsed_time = current_time - start_time
            frame_index = int(elapsed_time / 0.2) % len(frames)
            self.stdscr.addstr(node.row, node.col, frames[frame_index], curses.color_pair(3))
            if elapsed_time >= duration:
                game_map.explosions.remove(explosion)

        self.game_stats(player, game_map, start_time, current_time, enemies, bombs)
        self.stdscr.refresh()

    def game_stats(self, player, game_map, start_time, current_time, enemies, bombs):
        elapsed_time = current_time - start_time
        self.stdscr.addstr(game_map.rows + 1, 0, f"Time Elapsed: {elapsed_time:.2f} seconds")

        self.stdscr.addstr(game_map.rows + 3, 0, f"{player.name}'s Position: ({player.node.row}, {player.node.col})")
        self.stdscr.addstr(game_map.rows + 4, 0, f"{player.name}'s Lives: {player.lives}")
        self.stdscr.addstr(game_map.rows + 5, 0, f"{player.name}'s Bombs: {player.max_bombs - len(player.active_bombs)}")

        for i, enemy in enumerate(enemies):
            self.stdscr.addstr(game_map.rows + 7 + i, 0, f"Enemy {i+1} Lives: {enemy.lives}")

        for i, bomb in enumerate(bombs):
            self.stdscr.addstr(game_map.rows + 8 + len(enemies) + i, 0, f"Bomb {i+1} Position: ({bomb.node.row}, {bomb.node.col})")

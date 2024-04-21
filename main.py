# main.py

import os
import csv
import time
import curses
import random
from entities.enemy import Enemy
from entities.player import Player
from items.bomb import Bomb
from items.powerup import Powerup
from maps.map import Map

SCOREBOARD_FILE = "scoreboard.csv"
player_name = ""  # Global variable to store player's name

def init_game(stdscr):
    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Wall color pair
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Barrier color pair
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Bomb color pair
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)  # Powerup color pair

    HEIGHT, WIDTH = stdscr.getmaxyx()

    # Add title
    title = "Bomberman created by Miguel Cárdenas"
    stdscr.addstr(0, int((WIDTH - len(title)) / 2), title, curses.A_BOLD)

    # Add menu options
    menu_options = ["Play", "Scoreboard", "Exit"]
    selected_option = 0

    while True:
        stdscr.clear()

        for i, option in enumerate(menu_options):
            if i == selected_option:
                stdscr.addstr(2 + i, int((WIDTH - len(option)) / 2), option, curses.color_pair(1) | curses.A_REVERSE)
            else:
                stdscr.addstr(2 + i, int((WIDTH - len(option)) / 2), option)

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_option = (selected_option - 1) % len(menu_options)
        elif key == curses.KEY_DOWN:
            selected_option = (selected_option + 1) % len(menu_options)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if selected_option == 0:
                global player_name  # Access global variable
                if not player_name:
                    player_name = get_player_name(stdscr)
                start_game(stdscr, player_name)
            elif selected_option == 1:
                display_scoreboard(stdscr)
            elif selected_option == 2:
                curses.endwin()
                quit()

def get_player_name(stdscr):
    stdscr.clear()
    stdscr.addstr(2, 2, "Enter your name: ")
    curses.echo()
    player_name = stdscr.getstr(2, 20).decode(encoding="utf-8").strip()
    curses.noecho()
    return player_name

def start_game(stdscr, player_name):
    # Initialize the game
    curses.curs_set(0)      # Hide cursor
    stdscr.nodelay(True)    # Make non-blocking input
    stdscr.clear()

    # Create map
    game_map = Map(rows=20, cols=80)

    # Create player
    player = Player(game_map.get_node(1, 1)) # Create player at position (1, 1)
    if not player_name:  # If player name is not set, prompt for it
        player.name = get_player_name(stdscr)
        player_name = player.name
    else:
        player.name = player_name
    game_map.add_entity(player)

    # Create enemies
    num_enemies = 0
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
        handle_input(stdscr, player, game_map)

        current_time = time.time()
        if current_time - last_enemy_move_time >= enemy_move_delay:
            for entity in game_map.entities:
                if isinstance(entity, Enemy):
                    entity.move_randomly()
                    entity.place_bomb_if_needed(game_map)
            last_enemy_move_time = current_time

        # Render game
        render_game(stdscr, game_map, player, start_time=start_time)

        if not any(isinstance(entity, Enemy) for entity in game_map.entities):
            elapsed_time = time.time() - start_time
            save_score(player.name, elapsed_time)
            quit()


def save_score(player_name, elapsed_time):
    scores = []
    updated = False

    # Read existing scores
    if os.path.exists(SCOREBOARD_FILE):
        with open(SCOREBOARD_FILE, "r") as f:
            reader = csv.reader(f)
            for line in reader:
                scores.append((line[0], float(line[1])))

    # Check if the player exists in the scoreboard
    for i, (name, time_played) in enumerate(scores):
        if name == player_name:
            # If the player's new time is less, update the score
            if elapsed_time < time_played:
                scores[i] = (player_name, elapsed_time)
                updated = True
            break

    # If the player doesn't exist or the time was updated, rewrite the scoreboard
    if not updated:
        scores.append((player_name, elapsed_time))

    # Sort the scores
    scores.sort(key=lambda x: x[1])

    # Write the updated scoreboard to the file
    with open(SCOREBOARD_FILE, "w", newline='') as f:
        writer = csv.writer(f)
        for score in scores:
            writer.writerow(score)


def display_scoreboard(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 2, "Scoreboard")
    stdscr.addstr(2, 2, "Player Name\tTime Played")
    stdscr.addstr(3, 2, "-"*40)

    if os.path.exists(SCOREBOARD_FILE):
        scores = []
        with open(SCOREBOARD_FILE, "r") as f:
            reader = csv.reader(f)
            for line in reader:
                scores.append((line[0], float(line[1])))
        
        scores.sort(key=lambda x: x[1])  # Sort by time played

        for i, (name, time_played) in enumerate(scores[:10]):
            stdscr.addstr(4 + i, 2, f"{name}\t\t{time_played:.2f} seconds")

    stdscr.addstr(18, 2, "Press 'q' to return to the main menu...")
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break


def explode_bomb(bomb, game_map):
    node = bomb.node

    for direction in node.neighbors:
        neighbor = node.neighbors[direction]
        if neighbor and neighbor.state == "barrier":
            neighbor.state = "free"
            if random.random() < 0.1:
                powerup = Powerup(neighbor)
                game_map.add_item(powerup)
        if neighbor and neighbor.entity:
            kill_entity(neighbor.entity, game_map, neighbor)

    if node.entity:
        kill_entity(node.entity, game_map, node)


    # if node.item and isinstance(node.item, Bomb):
    #     node.item.node.entity.active_bombs -= 1

    game_map.items.remove(bomb)
    bomb.node.item = None


def kill_entity(entity, game_map, node):
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

def handle_input(stdscr, player, game_map):
    key = stdscr.getch()

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
                explode_bomb(item, game_map)

    for entity in game_map.entities:
        if entity.node.item and isinstance(entity.node.item, Powerup):
            entity.node.item.apply_powerup(entity)
            entity.node.item = None

def game_stats(stdscr, player, game_map, start_time, current_time, enemies, bombs):
    elapsed_time = current_time - start_time
    stdscr.addstr(game_map.rows + 1, 0, f"Time Elapsed: {elapsed_time:.2f} seconds")

    stdscr.addstr(game_map.rows + 3, 0, f"{player.name}'s Position: ({player.node.row}, {player.node.col})")
    stdscr.addstr(game_map.rows + 4, 0, f"{player.name}'s Lives: {player.lives}")

    for i, enemy in enumerate(enemies):
        stdscr.addstr(game_map.rows + 6 + i, 0, f"Enemy {i+1} Lives: {enemy.lives}")

    for i, bomb in enumerate(bombs):
        stdscr.addstr(game_map.rows + 7 + len(enemies) + i, 0, f"Bomb {i+1} Position: ({bomb.node.row}, {bomb.node.col})")

def render_game(stdscr, game_map, player, start_time):
    stdscr.clear()

    current_time = time.time()
    enemies = [entity for entity in game_map.entities if isinstance(entity, Enemy)]
    bombs = [item for item in game_map.items if isinstance(item, Bomb)]

    for row in range(game_map.rows):
        for col in range(game_map.cols):
            node = game_map.get_node(row, col)
            if node.state == 'wall':
                stdscr.addstr(row, col, '#', curses.color_pair(1))
            elif node.state == 'barrier':
                stdscr.addstr(row, col, 'X', curses.color_pair(2))
            elif node.entity:
                if isinstance(node.entity, Player):
                    stdscr.addstr(row, col, '👾')
                elif isinstance(node.entity, Enemy):
                    stdscr.addstr(row, col, '🤖')
            elif node.item:
                if isinstance(node.item, Bomb):
                    bomb = node.item
                    if bomb.should_explode():
                        elapsed_time = current_time - bomb.placement_time
                        frame_index = int(elapsed_time / 0.2) % len(bomb.explosion_frames)
                        stdscr.addstr(row, col, bomb.explosion_frames[frame_index], curses.color_pair(3))
                        if frame_index == len(bomb.explosion_frames) - 1:
                            node.item = None
                    else:
                        stdscr.addstr(row, col, '💣', curses.color_pair(3))

                elif isinstance(node.item, Powerup):
                    stdscr.addstr(row, col, 'o', curses.color_pair(4))
                else:
                    stdscr.addstr(row, col, '💣')

    game_stats(stdscr, player, game_map, start_time, current_time, enemies, bombs)
    stdscr.refresh()

def main():
    if not os.path.exists(SCOREBOARD_FILE):
        with open(SCOREBOARD_FILE, "w", newline='') as f:
            pass  # Create the scoreboard file if it doesn't exist

    curses.wrapper(init_game)

if __name__ == "__main__":
    main()

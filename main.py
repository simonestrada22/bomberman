# main.py

import curses
import time
import random
from entities.player import Player
from items.bomb import Bomb
from maps.map import Map


def init_game(stdscr):
    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Wall color pair
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Barrier color pair

    WIDTH =  20
    HEIGHT = 80


    # Initialize the game
    curses.curs_set(0)      # Hide cursor
    stdscr.nodelay(True)    # Make non-blocking input
    stdscr.clear()

    # Create map
    game_map = Map(rows=WIDTH, cols=HEIGHT)
    player = Player(game_map.get_node(1, 1)) # Create player at position (1, 1)

    start_time = time.time()
    # Game loop
    while True:
        # Update game state
        handle_input(stdscr, player, game_map)

        # Render game
        render_game(stdscr, game_map, player, start_time=start_time)


def explode_bomb(bomb):
    node = bomb.node
    for direction in node.neighbors:
        neighbor = node.neighbors[direction]
        if neighbor and neighbor.state == "barrier":
            neighbor.state = "free"
    # remove the bomb from the items in the node

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
            item.tick()
            if item.should_explode():
                explode_bomb(item)

def render_game(stdscr, game_map, player, start_time):
    stdscr.clear()
    current_time = time.time()
    # Print map
    for row in range(game_map.rows):
        for col in range(game_map.cols):
            node = game_map.get_node(row, col)
            if node.state == 'wall':
                stdscr.addstr(row, col, '#', curses.color_pair(1))
            elif node.state == 'barrier':
                stdscr.addstr(row, col, 'X', curses.color_pair(2))
            elif node.entity:
                stdscr.addstr(row, col, '👾')
            elif node.item:
                if isinstance(node.item, Bomb):
                    bomb = node.item
                    if bomb.should_explode():
                        elapsed_time = current_time - bomb.placement_time
                        frame_index = int(elapsed_time / 0.2) % len(bomb.explosion_frames)
                        stdscr.addstr(row, col, bomb.explosion_frames[frame_index], curses.color_pair(3))
                        if frame_index == len(bomb.explosion_frames) - 1:
                            # Remove bomb from the map
                            node.item = None
                    else:
                        stdscr.addstr(row, col, '💣', curses.color_pair(3))
                else:
                    stdscr.addstr(row, col, '💣')


    # Display game data table
    stdscr.addstr(game_map.rows + 2, 0, f"Player Position: ({player.node.row}, {player.node.col})")
    stdscr.addstr(game_map.rows + 3, 0, f"Player Lives: {player.lives}")
    for i, bomb in enumerate(game_map.items):
        if isinstance(bomb, Bomb):
            stdscr.addstr(game_map.rows + 4 + i, 0, f"Bomb {i+1} Position: ({bomb.node.row}, {bomb.node.col})")
    elapsed_time = current_time - start_time
    stdscr.addstr(game_map.rows + 5 + len(game_map.items), 0, f"Time Elapsed: {elapsed_time:.2f} seconds")

    stdscr.refresh()

def main():
    curses.wrapper(init_game)

if __name__ == "__main__":
   main()

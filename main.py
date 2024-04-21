# main.py

import curses
import time
from entities.enemy import Enemy
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

    # Create player
    player = Player(game_map.get_node(1, 1)) # Create player at position (1, 1)
    game_map.add_entity(player)

    # Create enemies
    num_enemies = 3
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


def explode_bomb(bomb, game_map):
    node = bomb.node

    # Explode bomb in all directions
    for direction in node.neighbors:
        neighbor = node.neighbors[direction]
        if neighbor and neighbor.state == "barrier":
            neighbor.state = "free"
        if neighbor and neighbor.entity:
            kill_entity(neighbor.entity, game_map, neighbor)

    # Kill player if it's in the same node as the bomb
    if node.entity:
        kill_entity(node.entity, game_map, node)

    # Remove bomb from the map
    game_map.items.remove(bomb)
    bomb.node.item = None

# check if a node has an entity and kill it
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


def game_stats(stdscr, player, game_map, start_time, current_time, enemies, bombs):

    # Display game data table
    elapsed_time = current_time - start_time
    stdscr.addstr(game_map.rows + 1, 0, f"Time Elapsed: {elapsed_time:.2f} seconds")

    stdscr.addstr(game_map.rows + 3, 0, f"Player Position: ({player.node.row}, {player.node.col})")
    stdscr.addstr(game_map.rows + 4, 0, f"Player Lives: {player.lives}")

    for i, enemy in enumerate(enemies):
        stdscr.addstr(game_map.rows + 6 + i, 0, f"Enemy {i+1} Lives: {enemy.lives}")
        
    for i, bomb in enumerate(bombs):
        stdscr.addstr(game_map.rows + 7 + len(enemies) + i, 0, f"Bomb {i+1} Position: ({bomb.node.row}, {bomb.node.col})")


    
def render_game(stdscr, game_map, player, start_time):
    stdscr.clear()

    current_time = time.time()
    enemies = [entity for entity in game_map.entities if isinstance(entity, Enemy)]
    bombs = [item for item in game_map.items if isinstance(item, Bomb)]

    # Print map
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
                            # Remove bomb from the map
                            node.item = None
                    else:
                        stdscr.addstr(row, col, '💣', curses.color_pair(3))
                else:
                    stdscr.addstr(row, col, '💣')


    game_stats(stdscr, player, game_map, start_time, current_time, enemies, bombs)
    stdscr.refresh()
   
def main():
    curses.wrapper(init_game)

if __name__ == "__main__":
   main()

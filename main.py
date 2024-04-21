# main.py

import os
import curses
from game.game import Game

def main(stdscr):

    game = Game(stdscr)
    game.init_game()


if __name__ == "__main__":
    curses.wrapper(main)

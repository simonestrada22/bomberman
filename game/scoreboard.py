# game/scoreboard.py

import os
import csv

SCOREBOARD_FILE = "scoreboard.csv"

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

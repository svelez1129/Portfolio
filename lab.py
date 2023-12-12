"""
6.1010 Lab 4: 
Snekoban Game
"""

import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

# keeps track of variables that actually matter for the game
game_variables = ["player", "computer", "wall", "target"]


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]
    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    # store positions of player, computer, target,wall, height, and width
    positions = {
        "player": None,
        "computer": set(),
        "target": set(),
        "wall": set(),
        "height": len(level_description),
        "width": len(level_description[0]),
    }
    # for rows in level description
    for row_index, row in enumerate(level_description):
        # for cols in level description
        for col_index, value in enumerate(row):
            # gives position
            position = (row_index, col_index)
            # for objects inside each game box
            for item in value:
                if item == "player":
                    positions[item] = position
                else:
                    positions[item].add(position)
    # turns computer into a frozenset so its hashable
    positions["computer"] = frozenset(positions["computer"])
    return positions


def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    # returns locations of computers
    comp_locations = game["computer"]
    # returns locations of target
    target_locations = game["target"]

    # check if there exists target locations
    if target_locations:
        # returns True if all computers are in target locations
        return target_locations == comp_locations
    return False


def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    # gives position of player
    p_player = game["player"]
    # gives each position of computer, and turned into a set
    p_computers = set(game["computer"])
    # updated_game = {key: game[key][:] for key in game}  # creates copy of game
    new_pos = new_position(p_player, direction)  # new position of player
    # checks whether the new position is valid
    if new_pos in game["wall"]:
        return game  # Early return if new position is not valid
    # checks whether new position has a computer in it
    if new_pos in p_computers:
        # gives new possible position of the moved computer
        new_computer_pos = new_position(
            new_pos, direction
        )  # new_pos is the computer's old position
        #checks if the computer can be moved to the new position
        if new_computer_pos in game["wall"] or new_computer_pos in p_computers:
            return game  # Early return if new computer position is not valid
        p_player = new_pos
        p_computers.remove(new_pos)
        p_computers.add(new_computer_pos)
        return {
            "player": p_player,
            "computer": frozenset(p_computers),
            "target": game["target"],
            "wall": game["wall"],
            "height": game["height"],
            "width": game["width"],
        }
    # case for computer is not in the new position
    p_player = new_pos
    return {
        "player": p_player,
        "computer": frozenset(p_computers),
        "target": game["target"],
        "wall": game["wall"],
        "height": game["height"],
        "width": game["width"],
    }


def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    # Find the row and col needed for list
    # Initialize the original representation with empty lists
    game_representation = [
        [[] for _ in range(game["width"])] for _ in range(game["height"])
    ]
    # adds player to game representation
    row_player = game["player"][0]
    col_player = game["player"][1]
    game_representation[row_player][col_player].append("player")
    # adds computers,walls,and targets to game representation
    for items in game_variables:
        # item can't be player to ensure for loop works
        if items != "player":
            for row, col in game[items]:
                game_representation[row][col].append(items)
    return game_representation


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    # only gives positions of player and computers
    seen = {game_to_tuple(game)}
    # queue housing tuples with path and game state
    queue = [[[], game_to_tuple(game)]]
    # new games to assign new game states to
    new_games = game
    # while queue is non-empty
    while queue:
        path, temp_game = queue.pop(0)  # stores possible path and game state
        # if the game state passes the victory check, return its path
        if victory_check(game_state(temp_game, game)):
            return path
        # for each direction in the direction vector
        for directions in direction_vector:
            # step game
            new_games = step_game(game_state(temp_game, game), directions)
            # if the game state hasn't been seen yet
            if game_to_tuple(new_games) not in seen:
                # append the new path to the queue with the new game state
                queue.append([path + [directions], game_to_tuple(new_games)])
                # add game state to seen game states
                seen.add(game_to_tuple(new_games))
    # if there is no way to win, return None
    return None


# HELPER FUNCTION


# find new position of moved object
def new_position(pos, direction):
    """
    Given an old position and direction, returns the new position,
    which is the old position displaced by whatever direction is given,
    which can be "üp", "down", "left", or "right"
    """
    # returns the new position as a tuple
    return (
        pos[0] + direction_vector[direction][0],
        pos[1] + direction_vector[direction][1],
    )

# return tuple of player and computer
def game_to_tuple(game):
    """
    Given a game state, return a tuple of its player and computer positions
    """
    return (game["player"], game["computer"])


# return game state given tuple of player and computer
def game_state(player_and_computer, game):
    """
    Given a tuple of player and computer positions, return the game state
    given the original game
    """
    return {
        "player": player_and_computer[0],
        "computer": player_and_computer[1],
        "target": game["target"],
        "wall": game["wall"],
        "height": game["height"],
        "width": game["width"],
    }


# NAME == MAIN
if __name__ == "__main__":
    l_description = []
    # creates updated game
    print("normal: ", l_description)
    dict_game = new_game(l_description)
    print("dict game: ", dict_game)
    # dump game
    print("dump_gamee ", dump_game(dict_game))
    # step game
    print("step game ", step_game(dict_game, "right"))

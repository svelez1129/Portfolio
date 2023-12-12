"""
6.101 Lab 7:
Six Double-Oh Mines
"""
#!/usr/bin/env python3

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    keys = ("board", "dimensions", "state", "visible")
    # ^ Uses only default game keys. If you modify this you will need
    # to update the docstrings in other functions!
    for key in keys:
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def new_game_2d(nrows, ncolumns, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       nrows (int): Number of rows
       ncolumns (int): Number of columns
       mines (list): List of mines, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    return new_game_nd((nrows, ncolumns), mines)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent mines (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one mine
    is visible on the board after digging (i.e. game['visible'][mine_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    mine) and no mines are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    return dig_nd(game, (row, col))


def render_2d_locations(game, all_visible=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  game['visible'] indicates which squares should be visible.  If
    all_visible is True (the default is False), game['visible'] is ignored
    and all cells are shown.

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                    by game['visible']

    Returns:
       A 2D array (list of lists)

    >>> game = {'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}
    >>> render_2d_locations(game, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations(game, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, all_visible)


def render_2d_board(game, all_visible=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    # empty string to hold ASCII art representation
    str_art = ""
    # grab rows of the board and the indices
    for row_i, rows in enumerate(render_2d_locations(game, all_visible)):
        # grab value inside row and the indices
        for value in rows:
            # check if position is visible or not
            str_art += value
        # if this isn't the last row
        if row_i != len(render_2d_locations(game, all_visible)) - 1:
            str_art += "\n"
    return str_art


# N-D IMPLEMENTATION


def new_game_nd(dimensions, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Args:
       dimensions (tuple): Dimensions of the board
       mines (list): mine locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    nd_game = {
        "board": create_board(dimensions, 0),
        "visible": create_board(dimensions, False),
        "dimensions": dimensions,
        "state": "ongoing",
    }
    #for each mine 
    for mine in mines:
        #set the location of each mine
        set(nd_game["board"], mine, ".")
        #for each neighbor of a mine, in order to set number for cell
        for other_mines in neighbors(mine, dimensions):
            neighbor_value = get(nd_game["board"], other_mines)
            # if the neighbor value is an int, then it puts more mines and increases the value to account for more mines neighboring it
            if type(neighbor_value) == int:
                set(nd_game["board"], other_mines, neighbor_value + 1)
    return nd_game


def dig_nd(game, coordinates, check_victory=True):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    mine.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one mine is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a mine) and no mines are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    #if the game is not ongoing or the cell is visible 
    if game["state"] != "ongoing" or get(game["visible"], coordinates):
        #0 holes dug
        return 0
    #sets coordinate dug to true
    set(game["visible"], coordinates, True)
    #hole to dig
    hole = get(game["board"], coordinates)
    # if the hole has a mine, the game state is defeated
    if hole == ".":
        game["state"] = "defeat"
        #one hole dug
        return 1
    holes_dug = 1
    #if hole is zero use recursion to find how many other holes are dug
    if hole == 0:
        #for each neighbor of the dug hole
        for neighbor in neighbors(coordinates, game["dimensions"]):
            #holes_dug increases by one for each extra hole dug
            holes_dug += dig_nd(game, neighbor, check_victory=False)
    #if the game is won, game state is now victory
    if victory(game):
        game["state"] = "victory"
    return holes_dug


def render_nd(game, all_visible=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  The game['visible'] array indicates which squares should be
    visible.  If all_visible is True (the default is False), the game['visible']
    array is ignored and all cells are shown.

    Args:
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       An neighbor-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    # creates new board
    new_board = create_board(game["dimensions"], None)
    #for each corrdinate in the game
    for coord in get_coord(game["dimensions"]):
        #get the visibility of the game board
        visible = get(game["visible"], coord)
        #get the item in the game board
        item = get(game["board"], coord)
        if item == 0:
            #how 0 is represented on the board
            item = " "
        #if not all visible and item isn't visible
        if not all_visible and not visible:
            set(new_board,coord,"_")
        #else add representation as item
        else:
            set(new_board,coord,str(item))
    return new_board


# HELPER FUNCTIONS
def mine_neighbors_2d(board, nrows, ncolumns, r, coord):
    """
    find the neighbors that a mine has
    """
    # Find the amount of mines that neighbor a region
    offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    m_neighbors = 0
    # for bordering rows and col
    for row, col in offsets:
        nr, nc = r + row, coord + col
        # if row and col are valid, and their is a mine in them, then add one to neighbor
        if 0 <= nr < nrows and 0 <= nc < ncolumns and board[nr][nc] == ".":
            m_neighbors += 1

    return neighbors


# Make board with n-dimensions
def create_board(dimensions, element):
    """
    create new board with dimensions given and add a element in it
    """
    # base case if dimensions is one
    if len(dimensions) == 1:
        return [element] * dimensions[0]
    else:
        # recursive case if more than one dimension
        return [create_board(dimensions[1:], element) for _ in range(dimensions[0])]

# set value inside location
def set(nested_ls, location, value):
    """
    sets the element at the given location in a nested list to be the given
    value.
    """
    # base case
    if len(location) == 1:
        nested_ls[location[0]] = value
    # recursive case to go deeper in the list
    else:
        set(nested_ls[location[0]], location[1:], value)

def get(nested_ls, location):
    """
    returns the element at a location in the list.
    """
    # base case if only one dimension is left
    if len(location) == 1:
        return nested_ls[location[0]]
    # Recursive case to go deeper into list
    else:
        return get(nested_ls[location[0]], location[1:])

# get the neighbors of all locations
def neighbors(location, dimensions):
    """
    gets neighbors of a given location and given a dimension
    """
    # Create a list of offsets for each dimension
    offsets = [-1, 0, 1]
    # list for neighbors
    neighbors_ls = []
    # Find different neighbors according to offset by dimension
    def combinations(visited):
        #visited keeps track of coordinates being generated
        #if both lengths are the same then all neighbors have been added
        if len(visited) == len(location):
            neighbors_ls.append(tuple(visited))
            return
        #offset for different dimensions
        for offset in offsets:
            #gets neighbor in new offset
            new_coord = location[len(visited)] + offset
            #if location is valid
            if 0 <= new_coord < dimensions[len(visited)]:
                #calls combinations again, but with a new neighbor
                combinations(visited + [new_coord])
    combinations([])
    # remove the original location from the neighbors list
    neighbors_ls.remove(tuple(location))
    return neighbors_ls



def get_coord(dimensions):
    """
    gets all the coordinates with the given dimension.
    """
    # base case if there is 0 dimensions
    if len(dimensions) == 0:
        yield tuple()
    else:
        # recursive case for when there is more than one dimension
        #for the first dimension
        for row in range(dimensions[0]):
            #for other dimensions
            for col in get_coord(dimensions[1:]):
                #gets coordinates
                yield (row,) + col


def victory(game):
    """
    return game victory conditition
    """
    #for each coordinate
    for coord in get_coord(game["dimensions"]):
        #get visibility
        visible = get(game["visible"], coord)
        #get value for board
        item = get(game["board"], coord)
        # if a mine has been revealed
        if item == "." and visible:
            return False
        # if a safe cell has not been revealed
        if not visible and item != ".":
            return False
    return True


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )

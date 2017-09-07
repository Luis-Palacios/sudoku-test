"""Solution for first module of AI Nanodegree"""
# Initial constants needed
ROWS = 'ABCDEFGHI'
COLS = '123456789'
# Used to create diagonal units 2
REVERSED_COLS = COLS[::-1]


def cross(a, b):
    # Cross product of elements in A and elements in B."
    return [s + t for s in a for t in b]


# Additional constants used for solution
BOXES = cross(ROWS, COLS)
ROW_UNITS = [cross(r, COLS) for r in ROWS]
COLUMN_UNITS = [cross(ROWS, c) for c in COLS]
SQUARE_UNITS = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI')
                for cs in ('123', '456', '789')]
# Form Diagonal Units
DIAGONAL_UNITS = [[ROWS[i] + COLS[i] for i in range(9)]]
DIAGONAL_UNITS_2 = [[ROWS[i] + REVERSED_COLS[i] for i in range(9)]]
# The unit list include the diagonals
UNITLIST = ROW_UNITS + COLUMN_UNITS + \
    SQUARE_UNITS + DIAGONAL_UNITS + DIAGONAL_UNITS_2
UNITS = dict((s, [u for u in UNITLIST if s in u]) for s in BOXES)
PEERS = dict((s, set(sum(UNITS[s], [])) - set([s])) for s in BOXES)

assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions
    # that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # First select boxes with 2 entries since they are possible twins
    possible_twins = [box for box in BOXES if len(values[box]) == 2]

    # Store boxes that are naked twins
    naked_twins = []
    for box in possible_twins:
        for peer in PEERS[box]:
            if values[box] == values[peer]:
                naked_twins.append({
                    'twin1': box,
                    'twin2': peer
                })

    # For each pair of naked twins,
    for naked_twin in naked_twins:
        twin1 = naked_twin['twin1']
        twin2 = naked_twin['twin2']
        # Get all peers from the naked twins
        peers1 = PEERS[twin1]
        peers2 = PEERS[twin2]
        # The peers that exist in both twins
        peers_to_check = peers1 & peers2

        # Delete the two digits in naked twins from all common peers.
        for peer in peers_to_check:
            if len(values[peer]) >= 2:
                digits = values[twin1]
                for digit in digits:
                    values = assign_value(
                        values, peer, values[peer].replace(digit, ''))
    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value,
            then the value will be '123456789'.
    """
    grid_dict = {}
    # Iterate trough all boxes
    for index, box in enumerate(BOXES):
        # If the value is not a '.' we assign the grid value
        # to the dict if it is a '.' we replace it for 123456789
        value = grid[index] if grid[index] != '.' else '123456789'
        grid_dict[box] = value
    return grid_dict


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    pass


def eliminate(values):
    # Get the boxes that already have a valid value
    boxes_with_values = (box for box in BOXES if len(values[box]) == 1)
    for box in boxes_with_values:
        # Iterate trough each peer of the box
        # with a valid value to eliminate that
        # as a possible value
        for peer in PEERS[box]:
            value = values[peer].replace(values[box], '')
            values = assign_value(values, peer, value)
    return values


def only_choice(values):
    # Iterate trough each unit
    for unit in UNITLIST:
        for digit in '123456789':
            # For each digit if it is
            # the only aviable for one box
            # we assign that value in that box
            counter = 0
            box_for_value = ''
            for box in unit:
                if digit in values[box]:
                    box_for_value = box
                    counter = counter + 1
            if counter == 1:
                values = assign_value(values, box_for_value, digit)
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len(
            [box for box in values.keys() if len(values[box]) == 1])

        # First the Eliminate Strategy
        values = eliminate(values)

        # Then the Only Choice Strategy
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len(
            [box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check,
        # return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Using depth-first search and propagation, create a search tree
     and solve the sudoku."""

    # Reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    # If for some reason the reduce puzzle fail we quit
    if values is False:
        return False

    # Lets assume is solved
    is_solved = True
    # If there is any box with an invalid value then is not solved
    for box in BOXES:
        if len(values[box]) != 1:
            is_solved = False

    # If is solved we are done!
    if is_solved:
        return values

    # Lets start our search
    # Choose one of the unfilled squares with the fewest possibilities
    unsolved_boxes = [box for box in BOXES if len(values[box]) != 1]
    # Random high min len value
    min_len = 20
    for box in unsolved_boxes:
        if(len(values[box]) < min_len):
            # We store the reference to the box that has the min len
            min_len = len(values[box])
            box_with_min_len = box
    # Iterate trough each digit in the box with the fewest possibilities
    for digit in values[box_with_min_len]:
        # A Copy of our values not a reference
        new_values = values.copy()
        # Assign the first digit to that box
        new_values[box_with_min_len] = digit
        # And lets see the results!
        result = search(new_values)
        if result:
            return result


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid.
        False if no solution exists.
    """
    dict_values = grid_values(grid)
    dict_values = search(dict_values)

    return dict_values


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

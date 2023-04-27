from pulp import (
    LpProblem,
    LpMinimize,
    LpVariable,
    LpInteger,
    PULP_CBC_CMD,
    LpStatusOptimal,
)

board: dict[tuple[int, int], str] = {}
COLOR_YELLOW = "yellow"
COLOR_BLUE = "blue"
COLOR_GREEN = "green"
COLOR_RED = "red"
COLOR_ORANGE = "orange"


def get_peripheric_positions(
    x_position: int, y_position: int, width: int, height: int
) -> list[tuple[int, int]]:
    check_positions = [
        (x_position - 1, y_position),
        (x_position + 1, y_position),
        (x_position, y_position - 1),
        (x_position, y_position + 1),
    ]
    check_positions = [
        x
        for x in check_positions
        if x[0] >= 0 and x[0] < width and x[1] >= 0 and x[1] < height
    ]
    return check_positions


def solve_flow_free(
    width: int, height: int, positions: dict[tuple[int, int], str]
) -> None:
    different_colors = list(set(positions.values()))

    # doesnt matter if it is a minimize or maximize problem
    problem = LpProblem("flow_free", LpMinimize)

    positions_with_colors = list(positions.keys())

    all_vars: dict[tuple[int, int, str], LpVariable] = {}

    positions_without_colors: list[tuple[int, int]] = []
    for x in range(width):
        for y in range(height):
            if (x, y) not in positions_with_colors:
                positions_without_colors.append((x, y))

    # now we create all variables, which are boolean (one per position and color)

    all_vars: dict[tuple[int, int, str], LpVariable] = {}

    for x in range(width):
        for y in range(height):
            vars_by_color: dict[str, LpVariable] = {}

            for color in different_colors:
                var_name = f"{color}_{x},{y}"
                cur_var = LpVariable(var_name, lowBound=0, upBound=1, cat=LpInteger)

                vars_by_color[color] = cur_var
                all_vars[(x, y, color)] = cur_var

            # we set the contraint that there can only be 1 color per position
            problem += sum(vars_by_color.values()) == 1

    # now we iterate over the positions of start and end of color
    for position, color in positions.items():
        x_position, y_position = position

        # here he set the contraint that the variable at the position
        # of that color must be 1
        problem += all_vars[(x_position, y_position, color)] == 1

        # now we get the peripheric variables (up, down,left,right)
        check_positions = get_peripheric_positions(
            x_position, y_position, width, height
        )

        cur_vars = []
        for pos in check_positions:
            pos_x, pos_y = pos
            cur_vars.append(all_vars[(pos_x, pos_y, color)])

        # we set the variable that the peripheric variables of the same color
        problem += sum(cur_vars) == 1

    # now we iterate on the positions without colors
    for position in positions_without_colors:
        for color in different_colors:
            pos_x, pos_y = position
            var_at_position_of_color = all_vars[(pos_x, pos_y, color)]

            # now we get the peripheric variables (up, down,left,right)
            check_positions = get_peripheric_positions(
                x_position, y_position, width, height
            )
            cur_vars = []
            for poz in check_positions:
                poz_x, poz_y = poz
                cur_vars.append(all_vars[(poz_x, poz_y, color)])

            # for each color, we say that:
            # - if the position is of this color, then it must have at
            #   least 2 neighbors with the same color

            problem += sum(cur_vars) >= 2 * var_at_position_of_color

    status = problem.solve(PULP_CBC_CMD(msg=False))
    assert status == LpStatusOptimal

    for color in different_colors:
        print("COLOR: ", color)
        print()
        for var in all_vars.values():
            if var.varValue == 1 and color in var.name:
                print(var)
        print()


if __name__ == "__main__":
    my_width = 5
    my_height = 5

    my_positions: dict[tuple[int, int], str] = {
        (0, 1): COLOR_YELLOW,
        (0, 2): COLOR_BLUE,
        (0, 3): COLOR_GREEN,
        (1, 3): COLOR_RED,
        (2, 2): COLOR_RED,
        (3, 0): COLOR_YELLOW,
        (3, 3): COLOR_ORANGE,
        (4, 0): COLOR_BLUE,
        (4, 2): COLOR_ORANGE,
        (4, 3): COLOR_GREEN,
    }

    solve_flow_free(my_width, my_height, my_positions)

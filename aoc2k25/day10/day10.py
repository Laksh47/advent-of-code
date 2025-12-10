import sys
from pathlib import Path
from typing import List, Set, Tuple

# Import explicitly to satisfy lint rules and keep namespace clean.
from pulp import (
    PULP_CBC_CMD,
    LpMinimize,
    LpProblem,
    LpStatusOptimal,
    LpVariable,
    lpSum,
    value,
)

# https://adventofcode.com/2025/day/10


def parse_machine(line: str) -> Tuple[List[int], List[Set[int]], List[int]]:
    """
    Parse a machine line into target state, button configurations, and joltage requirements.

    Returns:
        target_state: List of 0s and 1s representing desired light states (Part 1)
        buttons: List of sets, where each set contains the indices that button affects
        joltages: List of target joltage values (Part 2)
    """
    line = line.strip()

    # Extract indicator light diagram [.##.]
    bracket_start = line.index("[")
    bracket_end = line.index("]")
    light_diagram = line[bracket_start + 1 : bracket_end]
    target_state = [1 if c == "#" else 0 for c in light_diagram]

    # Extract button configurations (0,1,2) (3,4) etc.
    buttons = []
    i = bracket_end + 1
    while i < len(line):
        if line[i] == "(":
            # Find matching closing parenthesis
            paren_end = line.index(")", i)
            button_str = line[i + 1 : paren_end]
            # Parse the indices
            indices = set(int(x.strip()) for x in button_str.split(","))
            buttons.append(indices)
            i = paren_end + 1
        elif line[i] == "{":
            break
        else:
            i += 1

    # Extract joltage requirements {3,5,4,7}
    brace_start = line.index("{")
    brace_end = line.index("}")
    joltage_str = line[brace_start + 1 : brace_end]
    joltages = [int(x.strip()) for x in joltage_str.split(",")]

    return target_state, buttons, joltages


def solve_machine_lights_ilp(target_state: List[int], buttons: List[Set[int]]) -> int:
    """
    Solve the light configuration problem using Integer Linear Programming.

    For Part 1, we need to handle mod 2 arithmetic:
    - Each button can be pressed 0 or 1 times
    - Sum of presses affecting each light (mod 2) must equal target

    Returns:
        Minimum number of button presses needed, or -1 if impossible
    """
    num_lights = len(target_state)
    num_buttons = len(buttons)

    # Create the problem
    prob = LpProblem("LightConfig", LpMinimize)

    # Decision variables: whether to press each button (0 or 1)
    button_vars = [LpVariable(f"b{i}", cat="Binary") for i in range(num_buttons)]

    # Objective: minimize total button presses
    prob += lpSum(button_vars), "TotalPresses"

    # Constraints: for each light, sum of affecting buttons (mod 2) = target
    # To handle mod 2, we introduce auxiliary variables
    # If sum is odd, it equals 1 (mod 2), if even, it equals 0 (mod 2)

    for light_idx in range(num_lights):
        # Find which buttons affect this light
        affecting_buttons = [button_vars[b_idx] for b_idx, button in enumerate(buttons) if light_idx in button]

        if not affecting_buttons:
            # No buttons affect this light
            if target_state[light_idx] == 1:
                return -1  # Impossible
            continue

        # Sum of affecting buttons
        button_sum = lpSum(affecting_buttons)

        # We need: button_sum ≡ target_state[light_idx] (mod 2)
        # This means: button_sum = target_state[light_idx] + 2k for some integer k ≥ 0

        # Introduce auxiliary variable for the quotient
        k = LpVariable(f"k{light_idx}", lowBound=0, cat="Integer")

        # Constraint: button_sum = target_state[light_idx] + 2*k
        prob += button_sum == target_state[light_idx] + 2 * k, f"Light{light_idx}_mod2"

    # Solve
    prob.solve(PULP_CBC_CMD(msg=0))

    # Check if solution was found
    if prob.status != LpStatusOptimal:
        return -1

    return int(value(prob.objective))


def solve_machine_joltage_ilp(joltages: List[int], buttons: List[Set[int]]) -> int:
    """
    Solve the joltage configuration problem using Integer Linear Programming.

    For Part 2, this is straightforward:
    - Each button can be pressed any number of times (≥ 0)
    - Sum of presses affecting each counter must equal target

    Returns:
        Minimum number of button presses needed, or -1 if impossible
    """
    num_counters = len(joltages)
    num_buttons = len(buttons)

    # Create the problem
    prob = LpProblem("JoltageConfig", LpMinimize)

    # Decision variables: number of times to press each button (≥ 0)
    button_vars = [LpVariable(f"b{i}", lowBound=0, cat="Integer") for i in range(num_buttons)]

    # Objective: minimize total button presses
    prob += lpSum(button_vars), "TotalPresses"

    # Constraints: for each counter, sum of affecting buttons = target
    for counter_idx in range(num_counters):
        # Find which buttons affect this counter
        affecting_buttons = [button_vars[b_idx] for b_idx, button in enumerate(buttons) if counter_idx in button]

        if not affecting_buttons:
            # No buttons affect this counter
            if joltages[counter_idx] != 0:
                return -1  # Impossible
            continue

        # Constraint: sum = target
        prob += lpSum(affecting_buttons) == joltages[counter_idx], f"Counter{counter_idx}"

    # Solve
    prob.solve(PULP_CBC_CMD(msg=0))

    # Check if solution was found
    if prob.status != LpStatusOptimal:
        return -1

    return int(value(prob.objective))


def solve_part1(lines: List[str]) -> int:
    """Solve part 1: Find minimum button presses for light configuration."""
    total_presses = 0

    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue

        target_state, buttons, _ = parse_machine(line)
        min_presses = solve_machine_lights_ilp(target_state, buttons)

        if min_presses == -1:
            print(f"Machine {line_num}: No solution possible!")
        else:
            print(f"Machine {line_num}: {min_presses} presses needed")
            total_presses += min_presses

    return total_presses


def solve_part2(lines: List[str]) -> int:
    """Solve part 2: Find minimum button presses for joltage configuration."""
    total_presses = 0

    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue

        _, buttons, joltages = parse_machine(line)
        min_presses = solve_machine_joltage_ilp(joltages, buttons)

        if min_presses == -1:
            print(f"Machine {line_num}: No solution possible!")
        else:
            print(f"Machine {line_num}: {min_presses} presses needed")
            total_presses += min_presses

    return total_presses


def main(filename: str = "input_test.txt"):
    print(f"Processing file: {filename}")
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    with open(file_path, "r") as file:
        lines = file.readlines()

    print("\n=== Part 1: Light Configuration ===")
    result1 = solve_part1(lines)
    print(f"Total minimum button presses: {result1}")

    print("\n=== Part 2: Joltage Configuration ===")
    result2 = solve_part2(lines)
    print(f"Total minimum button presses: {result2}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

import sys
from pathlib import Path

# https://adventofcode.com/2025/day/7


def solve_tachyon_manifold(grid_input: list[str]) -> int:
    """
    Simulates the tachyon beam splitting process to count the total splits.

    Args:
        grid_input: A list of strings representing the tachyon manifold diagram.

    Returns:
        The total number of times a tachyon beam is split.
    """
    if not grid_input:
        return 0

    R = len(grid_input)
    C = len(grid_input[0])

    start_col = -1
    for c in range(C):
        if grid_input[0][c] == "S":
            start_col = c
            break


    active_beams = {start_col}
    split_count = 0

    for r in range(1, R):
        next_beams = set()
        for c in active_beams:
            cell = grid_input[r][c]

            if cell == ".":
                next_beams.add(c)
            elif cell == "^":
                split_count += 1

                left_col = c - 1
                if 0 <= left_col < C:
                    next_beams.add(left_col)

                right_col = c + 1
                if 0 <= right_col < C:
                    next_beams.add(right_col)

        active_beams = next_beams
        if not active_beams:
            break

    return split_count


def main(filename: str = "input_test.txt"):
    print(f"Processing file: {filename}")
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    with open(file_path, "r") as file:
        lines = file.readlines()

    total_splits = solve_tachyon_manifold(lines)
    print(f"Total splits: {total_splits}")


if __name__ == "__main__":
    # If a filename is provided as the first CLI argument, use it; otherwise use the default.
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

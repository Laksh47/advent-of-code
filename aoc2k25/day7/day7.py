import sys
from collections import defaultdict
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


def quantum_split(grid_input, start_col):
    R = len(grid_input)
    C = len(grid_input[0])

    timeline_counts = defaultdict(int)
    timeline_counts[start_col] = 1

    total_completed_timelines = 0

    for r in range(1, R):
        next_timeline_counts = defaultdict(int)

        for c, count in timeline_counts.items():
            if c < 0 or c >= C:
                total_completed_timelines += count
                continue

            cell = grid_input[r][c]

            if cell == "S" or cell == ".":
                next_timeline_counts[c] += count

            elif cell == "^":
                left_target = c - 1
                right_target = c + 1

                if 0 <= left_target < C:
                    next_timeline_counts[left_target] += count
                else:
                    total_completed_timelines += count

                if 0 <= right_target < C:
                    next_timeline_counts[right_target] += count
                else:
                    total_completed_timelines += count

        timeline_counts = next_timeline_counts

        if not timeline_counts:
            break

    total_completed_timelines += sum(timeline_counts.values())
    return total_completed_timelines


def solve_quantum_tachyon_manifold(grid_input):
    if not grid_input:
        return 0

    C = len(grid_input[0])
    start_col = -1
    for c in range(C):
        if grid_input[0][c] == "S":
            start_col = c
            break

    return quantum_split(grid_input, start_col)


def main(filename: str = "input_test.txt"):
    print(f"Processing file: {filename}")
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    with open(file_path, "r") as file:
        lines = file.readlines()

    total_splits = solve_tachyon_manifold(lines)
    print(f"Total splits: {total_splits}")

    total_completed_timelines = solve_quantum_tachyon_manifold(lines)
    print(f"Total timelines: {total_completed_timelines}")


if __name__ == "__main__":
    # If a filename is provided as the first CLI argument, use it; otherwise use the default.
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

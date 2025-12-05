import sys
from pathlib import Path
from copy import deepcopy
# https://adventofcode.com/2025/day/4


def can_access_roll(matrix: list[list[str]], row: int, col: int):
    count = 0
    offsets = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    for offset in offsets:
        new_row = row + offset[0]
        new_col = col + offset[1]
        if 0 <= new_row < len(matrix) and 0 <= new_col < len(matrix[0]):
            if matrix[new_row][new_col] == "@":
                count += 1
    return count < 4


def remove_rolls(matrix: list[list[str]]):
    new_matrix = deepcopy(matrix)

    count = 0
    for row in range(len(matrix)):
        for col in range(len(matrix[0])):
            if matrix[row][col] == "@" and can_access_roll(matrix, row, col):
                new_matrix[row][col] = "x"
                count += 1

    return new_matrix, count


def main(filename: str = "input_test.txt"):
    print(f"Processing file: {filename}")
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    with open(file_path, "r") as file:
        matrix = [list(line.strip()) for line in file if line.strip()]

    total_count = 0
    while True:
        new_matrix, count = remove_rolls(matrix)
        if count == 0:
            break

        matrix = new_matrix
        total_count += count

    print(f"The number of rolls of paper that can be accessed by a forklift is {total_count}")


if __name__ == "__main__":
    # If a filename is provided as the first CLI argument, use it; otherwise use the default.
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

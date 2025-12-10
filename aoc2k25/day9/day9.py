import sys
from itertools import combinations
from pathlib import Path

# https://adventofcode.com/2025/day/9


def main(filename: str = "input_test.txt"):
    print(f"Processing file: {filename}")
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    # Check if file exists to prevent crashing
    if not file_path.exists():
        print(f"Error: File '{filename}' not found at {file_path}")
        return

    with open(file_path, "r") as file:
        lines = file.readlines()

    # 1. Parse the input into a list of tuples (x, y)
    red_tiles = []
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Split "7,1" into integers 7 and 1
        try:
            parts = line.split(",")
            x = int(parts[0])
            y = int(parts[1])
            red_tiles.append((x, y))
        except ValueError:
            print(f"Skipping invalid line: {line}")
            continue

    print(f"Found {len(red_tiles)} red tiles.")

    # 2. Iterate through every possible pair of tiles to find the max area
    max_area = 0

    # combinations(list, 2) gives us every unique pair (A, B)
    # This is O(N^2), which is fine for typical puzzle input sizes
    for tile_a, tile_b in combinations(red_tiles, 2):
        x1, y1 = tile_a
        x2, y2 = tile_b

        # Calculate inclusive width and height
        # Formula: |p1 - p2| + 1
        width = abs(x1 - x2) + 1
        height = abs(y1 - y2) + 1

        area = width * height

        if area > max_area:
            max_area = area

    print(f"Result: {max_area}")


if __name__ == "__main__":
    # If a filename is provided as the first CLI argument, use it; otherwise use the default.
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

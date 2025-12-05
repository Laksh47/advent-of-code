import sys
from pathlib import Path

# https://adventofcode.com/2025/day/5


def is_spoiled(fresh_ingredient_ranges, ingredient):
    for start, end in fresh_ingredient_ranges:
        if start <= ingredient <= end:
            return False

    return True


def main(filename: str = "input_test.txt"):
    print(f"Processing file: {filename}")
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    with open(file_path, "r") as file:
        lines = file.readlines()

    fresh_ingredient_ranges = []
    ingredients = []
    seen_empty_line = False

    for line in lines:
        line = line.strip()
        if not line:
            seen_empty_line = True
            continue

        if not seen_empty_line:
            # Parse range format: "start-end" and add as tuple
            start, end = map(int, line.split("-"))
            fresh_ingredient_ranges.append((start, end))
        else:
            # Add ingredient (just a number)
            ingredients.append(int(line))

    print(f"Fresh ingredient ranges: {fresh_ingredient_ranges}")
    print(f"Ingredients: {ingredients}")

    count = 0
    for ingredient in ingredients:
        if is_spoiled(fresh_ingredient_ranges, ingredient):
            continue
        count += 1

    print(f"Fresh ingredients count: {count}")


if __name__ == "__main__":
    # If a filename is provided as the first CLI argument, use it; otherwise use the default.
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

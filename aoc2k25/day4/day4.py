import sys
from pathlib import Path

# https://adventofcode.com/2025/day/4


def main(filename: str = "input_test.txt"):
    print(f"Processing file: {filename}")
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    with open(file_path, "r") as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Process each line here
        print(f"Processing: {line}")

    print("Result: ")


if __name__ == "__main__":
    # If a filename is provided as the first CLI argument, use it; otherwise use the default.
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

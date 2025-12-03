import sys
from pathlib import Path

# https://adventofcode.com/2025/day/3


def get_largest_joltage(bank: str):
    max_joltage = 0
    for i in range(len(bank)):
        for j in range(i + 1, len(bank)):
            joltage = int(bank[i] + bank[j])
            if joltage > max_joltage:
                max_joltage = joltage
    return max_joltage


def main(filename: str = "input_test.txt"):
    print(f"Processing file: {filename}")
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    with open(file_path, "r") as file:
        lines = file.readlines()

    sum_joltage = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Process each line here
        print(f"Processing: {line}")
        curr_max_joltage = get_largest_joltage(line)
        print(f"The largest joltage for bank {line} is {curr_max_joltage}")
        print()
        sum_joltage += curr_max_joltage

    print(f"The total output joltage is {sum_joltage}")


if __name__ == "__main__":
    # If a filename is provided as the first CLI argument, use it; otherwise use the default.
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

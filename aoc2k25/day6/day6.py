import operator
import sys
from pathlib import Path

# https://adventofcode.com/2025/day/6


def parse_file(file_path: Path) -> dict:
    """Parse the file and build a dictionary with 1-indexed keys containing lists of values."""
    result = {}

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            values = line.split()

            for i, val in enumerate(values):
                key = i + 1
                if key not in result:
                    result[key] = []
                try:
                    result[key].append(int(val))
                except ValueError:
                    result[key].append(val)

    return result


def apply_operators(data: dict, left_to_right: bool = False) -> dict:
    """Apply the operator (last value) to the rest of the list for each column."""
    operator_map = {"+": operator.add, "*": operator.mul}

    results = {}
    for key, values in data.items():
        if not values:
            continue

        op_str = str(values[-1])
        numbers = values[:-1]

        if left_to_right:
            numbers = transform(numbers)

        if op_str not in operator_map:
            print(f"Warning: Unknown operator '{op_str}' in line[{key}]")
            continue

        op_func = operator_map[op_str]

        if not numbers:
            results[key] = None
        else:
            result_value = numbers[0]
            for num in numbers[1:]:
                result_value = op_func(result_value, num)
            results[key] = result_value
            print(f"line[{key}] = {numbers} {op_str} = {result_value}")

    return results


def part1(filename: str = "input_test.txt"):
    print(f"Processing file: {filename}")
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    data = parse_file(file_path)

    results = apply_operators(data)

    total_sum = sum(results.values())
    print(f"Sum of all results: {total_sum}")

    return total_sum


def main(filename: str = "input_test.txt"):
    part1(filename)
    print()


if __name__ == "__main__":
    # If a filename is provided as the first CLI argument, use it; otherwise use the default.
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

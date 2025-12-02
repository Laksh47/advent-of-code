import sys
from pathlib import Path

# https://adventofcode.com/2025/day/2

# def is_invalid_id(id_val):
#     s = str(id_val)
#     length = len(s)

#     if length % 2 != 0:
#         return False

#     midpoint = length // 2
#     first_half = s[:midpoint]
#     second_half = s[midpoint:]

#     return first_half == second_half


def is_invalid_id(id_val):
    s = str(id_val)
    length = len(s)

    for i in range(1, length // 2 + 1):
        if length % i == 0:
            pattern = s[:i]
            repeats = length // i

            if pattern * repeats == s:
                return True

    return False


def find_invalid_ids_sum(input_test: str):
    invalid_ids = []
    for range_str in input_test.split(","):
        start, end = range_str.split("-")
        for id in range(int(start), int(end) + 1):
            if is_invalid_id(id):
                invalid_ids.append(id)
    return sum(invalid_ids)


def main(filename: str = "input_test.txt"):
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename
    with open(file_path, "r") as file:
        input_test = file.read()

    print(f"The sum of the invalid IDs is {find_invalid_ids_sum(input_test)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

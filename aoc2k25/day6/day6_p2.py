import operator
import sys
from pathlib import Path
from typing import List, Tuple

OPERATORS_MAP = {
    "+": operator.add,
    "*": operator.mul,
}


def get_simplified_column_ranges(pattern_line: str) -> List[Tuple[int, int]]:
    """
    Optimized function to define column slice ranges.

    The segment begins after the previous operator and ends immediately before
    the current one. The final segment is handled after the loop.

    Args:
        pattern_line: The last row containing operators (e.g., "* +   * +  ").

    Returns:
        A list of (start_index, end_index) tuples for string slicing.
    """
    operators = OPERATORS_MAP.keys()
    column_ranges: List[Tuple[int, int]] = []
    current_content_start = 0

    extracted_operators = []

    for i in range(len(pattern_line)):
        char = pattern_line[i]

        if char in operators:
            extracted_operators.append(char)
            if i > current_content_start:
                column_ranges.append((current_content_start, i - 1))  # adjust for the delimiter white space
            current_content_start = i

    final_segment_end = len(pattern_line)
    if final_segment_end > current_content_start:
        column_ranges.append((current_content_start, final_segment_end))

    return extracted_operators, column_ranges


def parse_right_to_left(nums_as_str):
    col_width = len(nums_as_str[0])
    vertical_numbers: List[str] = []

    for col_idx in range(col_width):
        vertical_string_parts: List[str] = []

        for row_str in nums_as_str:
            char = row_str[col_idx]

            if not char.isspace():
                vertical_string_parts.append(char)

        if vertical_string_parts:
            new_number_str = "".join(vertical_string_parts)
            vertical_numbers.append(int(new_number_str))

    return vertical_numbers


def apply_operation(op, operands):
    func = OPERATORS_MAP[op]
    res = operands[0]
    for x in operands[1:]:
        res = func(res, x)

    return res


def solve_puzzle(data_lines, extracted_operators, column_ranges):
    puzzle_answer = 0
    for op, (start, end) in zip(extracted_operators, column_ranges):
        nums_as_str = [data_line[start:end] for data_line in data_lines]
        nums = parse_right_to_left(nums_as_str)
        answer = apply_operation(op, nums)
        print(op, nums, answer)
        puzzle_answer += answer
    return puzzle_answer


def main(filename: str = "input_test.txt"):
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename
    with open(file_path, "r") as f:
        test_input = f.readlines()

    # --- Test Input and Execution ---
    # test_input = ["123 328  51 64 ", " 45 64  387 23 ", "  6 98  215 314", "*   +   *   +  "]

    pattern_line = test_input[-1]
    data_lines = test_input[:-1]

    extracted_operators, column_ranges = get_simplified_column_ranges(pattern_line)

    print("### 📏 Optimized Extracted Column Ranges (Indices) ###")
    for start, end in column_ranges:
        print(f"Slice Range: ({start}, {end})")

    print(solve_puzzle(data_lines, extracted_operators, column_ranges))


if __name__ == "__main__":
    # If a filename is provided as the first CLI argument, use it; otherwise use the default.
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

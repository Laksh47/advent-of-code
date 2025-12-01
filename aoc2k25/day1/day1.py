import sys
from pathlib import Path

# https://adventofcode.com/2025/day/1


class Dial:
    def __init__(self, position: int = 50, direction: str = ""):
        self.position = position
        self.direction = direction

    def turn(self, direction: int, amount: int):
        # Count how many times we point at 0 *during* this rotation (excluding the starting
        # position and the final landing, which is handled separately).
        if direction == "R":
            start = self.position  # 0..99
            zeros_during = (start + amount - 1) // 100
            new_position = (self.position + amount) % 100
        else:  # "L"
            # Mirror the dial so a left rotation becomes a right rotation from 100 - start.
            start_mirrored = (100 - self.position) % 100
            zeros_during = (start_mirrored + amount - 1) // 100
            new_position = (self.position - amount) % 100

        self.position = new_position
        return self.position, zeros_during

    def get_position(self):
        return self.position


def main(filename: str = "input_test.txt"):
    dial = Dial()
    zero_count = 0

    print(f"Processing file: {filename}")
    print(f"The dial starts by pointing at {dial.get_position()}")
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    with open(file_path, "r") as file:
        lines = file.readlines()

    for line in lines:
        direction, amount = line[:1], int(line[1:])
        current_position, zeros_during = dial.turn(direction, amount)
        zero_count += zeros_during
        if current_position == 0:
            zero_count += 1

        print(f"The dial is rotated {direction}{amount} to point at {current_position}")
        print(f"During this rotation, the dial points at 0: {zeros_during} times")
        print()

    print(f"The dial points at {dial.get_position()} after all rotations")
    print(f"The dial points at 0: {zero_count} times")


if __name__ == "__main__":
    # If a filename is provided as the first CLI argument, use it; otherwise use the default.
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

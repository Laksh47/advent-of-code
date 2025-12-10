import sys
from itertools import combinations
from pathlib import Path

# https://adventofcode.com/2025/day/9

# --- Geometry Helpers for Part 2 ---


def is_point_in_polygon(x, y, poly_edges):
    """
    Ray Casting Algorithm: Checks if point (x,y) is inside the polygon.
    Returns True if inside, False if outside.
    """
    collisions = 0
    for (x1, y1), (x2, y2) in poly_edges:
        # Check if the ray (moving right from x,y) crosses this vertical edge
        if x1 == x2:
            # Check if edge spans our y-coord
            if min(y1, y2) <= y < max(y1, y2):
                # Check if edge is strictly to the right
                if x1 > x:
                    collisions += 1
    return collisions % 2 == 1


def edge_intersects_rect_interior(edge, rect):
    """
    Checks if a polygon edge slices strictly through the INTERIOR of the rectangle.
    Touching the boundary of the rectangle is allowed and valid.
    """
    (ex1, ey1), (ex2, ey2) = edge
    rx_min, rx_max, ry_min, ry_max = rect

    # If edge is vertical
    if ex1 == ex2:
        # Edge X must be strictly inside Rect X bounds
        if rx_min < ex1 < rx_max:
            # Edge Y interval must overlap Rect Y interval
            if max(min(ey1, ey2), ry_min) < min(max(ey1, ey2), ry_max):
                return True

    # If edge is horizontal
    elif ey1 == ey2:
        # Edge Y must be strictly inside Rect Y bounds
        if ry_min < ey1 < ry_max:
            # Edge X interval must overlap Rect X interval
            if max(min(ex1, ex2), rx_min) < min(max(ex1, ex2), rx_max):
                return True

    return False


# --- Part Solvers ---


def solve_part1(red_tiles):
    """
    Finds the largest rectangle defined by any two red tiles.
    No restrictions on what lies between them.
    """
    max_area = 0

    for tile_a, tile_b in combinations(red_tiles, 2):
        x1, y1 = tile_a
        x2, y2 = tile_b

        # Inclusive Area = (Diff + 1) * (Diff + 1)
        width = abs(x1 - x2) + 1
        height = abs(y1 - y2) + 1
        area = width * height

        if area > max_area:
            max_area = area

    return max_area


def solve_part2(red_tiles):
    """
    Finds the largest rectangle that is completely CONTAINED within
    the polygon formed by the red tiles.
    """
    # 1. Build Polygon Edges (Connect points in order)
    poly_edges = []
    num_tiles = len(red_tiles)
    for i in range(num_tiles):
        p1 = red_tiles[i]
        p2 = red_tiles[(i + 1) % num_tiles]  # Wrap to start
        poly_edges.append((p1, p2))

    max_area = 0

    # 2. Check every pair
    for tile_a, tile_b in combinations(red_tiles, 2):
        x1, y1 = tile_a
        x2, y2 = tile_b

        rx_min, rx_max = min(x1, x2), max(x1, x2)
        ry_min, ry_max = min(y1, y2), max(y1, y2)

        width = (rx_max - rx_min) + 1
        height = (ry_max - ry_min) + 1
        area = width * height

        # Optimization: Skip complex checks if area is too small
        if area <= max_area:
            continue

        # 3. Validity Checks
        # Test A: Is the center of the rectangle inside the polygon?
        mid_x = (rx_min + rx_max) / 2
        mid_y = (ry_min + ry_max) / 2

        if not is_point_in_polygon(mid_x, mid_y, poly_edges):
            # Special case: Thin rectangles (width 1) lie on the boundary.
            # We assume valid if they don't fail Test B.
            # But strictly, if it's 1-wide, we check if it aligns with an edge.
            # For simplicity in this puzzle context, usually center check + intersect check is enough.
            # If center is OUT, we discard unless it's a boundary line case.
            if width > 1 and height > 1:
                continue

        # Test B: Does any polygon edge cut through the rectangle?
        rect_tuple = (rx_min, rx_max, ry_min, ry_max)
        intersection_found = False
        for edge in poly_edges:
            if edge_intersects_rect_interior(edge, rect_tuple):
                intersection_found = True
                break

        if not intersection_found:
            max_area = area

    return max_area


# --- Main Execution ---


def main(filename: str = "input_test.txt"):
    print(f"Processing file: {filename}")
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    if not file_path.exists():
        print(f"Error: File '{filename}' not found.")
        return

    with open(file_path, "r") as file:
        lines = file.readlines()

    # Shared Parsing
    red_tiles = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            x, y = map(int, line.split(","))
            red_tiles.append((x, y))
        except ValueError:
            continue

    print(f"Loaded {len(red_tiles)} coordinates.")
    print("-" * 30)

    # Run Part 1
    result_p1 = solve_part1(red_tiles)
    print(f"Part 1 Result: {result_p1}")

    # Run Part 2
    result_p2 = solve_part2(red_tiles)
    print(f"Part 2 Result: {result_p2}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

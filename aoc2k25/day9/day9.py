import sys
from pathlib import Path


def is_point_in_polygon(x, y, poly_edges):
    """
    Ray casting algorithm: checks if point (x,y) is inside the polygon.
    Counts how many times a ray going right from (x,y) crosses polygon edges.
    Odd = inside, Even = outside.
    """
    collisions = 0
    for (x1, y1), (x2, y2) in poly_edges:
        # Only consider vertical edges (x1 == x2)
        if x1 == x2:
            # Check if edge spans our y-coordinate
            if min(y1, y2) <= y < max(y1, y2):
                # Check if edge is to the right of our point
                if x1 > x:
                    collisions += 1

    return collisions % 2 == 1


def edge_intersects_rect_interior(edge, rect):
    """
    Checks if a polygon edge cuts through the INTERIOR of the rectangle.
    Touching the boundary is allowed (returns False).
    Only cutting through the interior is invalid (returns True).
    """
    (ex1, ey1), (ex2, ey2) = edge
    rx_min, rx_max, ry_min, ry_max = rect

    # Case 1: Vertical edge
    if ex1 == ex2:
        # Edge X must be STRICTLY inside rectangle X bounds
        if rx_min < ex1 < rx_max:
            # Edge Y interval must overlap with rectangle Y interval
            edge_y_min = min(ey1, ey2)
            edge_y_max = max(ey1, ey2)
            overlap_start = max(edge_y_min, ry_min)
            overlap_end = min(edge_y_max, ry_max)
            if overlap_start < overlap_end:
                return True

    # Case 2: Horizontal edge
    elif ey1 == ey2:
        # Edge Y must be STRICTLY inside rectangle Y bounds
        if ry_min < ey1 < ry_max:
            # Edge X interval must overlap with rectangle X interval
            edge_x_min = min(ex1, ex2)
            edge_x_max = max(ex1, ex2)
            overlap_start = max(edge_x_min, rx_min)
            overlap_end = min(edge_x_max, rx_max)
            if overlap_start < overlap_end:
                return True

    return False


def solve_part1(red_tiles):
    """Find largest rectangle with red tiles at opposite corners."""
    max_area = 0

    # Check all pairs of red tiles
    for i in range(len(red_tiles)):
        for j in range(i + 1, len(red_tiles)):
            x1, y1 = red_tiles[i]
            x2, y2 = red_tiles[j]

            # They must be diagonal (different x AND different y)
            if x1 != x2 and y1 != y2:
                width = abs(x2 - x1) + 1
                height = abs(y2 - y1) + 1
                area = width * height
                max_area = max(max_area, area)

    return max_area


def solve_part2(red_tiles):
    """Find largest rectangle using only red and green tiles."""

    # Build polygon edges (connecting consecutive red tiles)
    poly_edges = []
    n = len(red_tiles)
    for i in range(n):
        p1 = red_tiles[i]
        p2 = red_tiles[(i + 1) % n]  # Wrap around
        poly_edges.append((p1, p2))

    max_area = 0

    # Check all pairs of red tiles
    for i in range(len(red_tiles)):
        for j in range(i + 1, len(red_tiles)):
            x1, y1 = red_tiles[i]
            x2, y2 = red_tiles[j]

            # They must be diagonal
            if x1 == x2 or y1 == y2:
                continue

            # Define rectangle bounds
            rx_min, rx_max = min(x1, x2), max(x1, x2)
            ry_min, ry_max = min(y1, y2), max(y1, y2)

            width = rx_max - rx_min + 1
            height = ry_max - ry_min + 1
            area = width * height

            # Optimization: skip if area won't improve our max
            if area <= max_area:
                continue

            # Validity Check 1: Is the center of the rectangle inside the polygon?
            mid_x = (rx_min + rx_max) / 2.0
            mid_y = (ry_min + ry_max) / 2.0

            if not is_point_in_polygon(mid_x, mid_y, poly_edges):
                # Special case for thin rectangles on the boundary
                if width > 1 and height > 1:
                    continue

            # Validity Check 2: Does any polygon edge cut through the rectangle interior?
            rect = (rx_min, rx_max, ry_min, ry_max)
            intersection_found = False
            for edge in poly_edges:
                if edge_intersects_rect_interior(edge, rect):
                    intersection_found = True
                    break

            if not intersection_found:
                max_area = area

    return max_area


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

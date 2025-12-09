import math
import sys
from pathlib import Path

# https://adventofcode.com/2025/day/8


class UnionFind:
    """Helper class to manage connected components (circuits)."""

    def __init__(self, n):
        # Initially, every node is its own parent (its own circuit)
        self.parent = list(range(n))

    def find(self, i):
        """Finds the root representative of the set containing i."""
        if self.parent[i] != i:
            # Path compression: point directly to the root
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        """Merges the sets containing i and j. Returns True if merged, False if already same."""
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j
            return True
        return False

    def get_component_sizes(self):
        """Returns a list of sizes for all distinct circuits."""
        counts = {}
        for i in range(len(self.parent)):
            root = self.find(i)
            counts[root] = counts.get(root, 0) + 1
        return list(counts.values())


def main(filename: str = "input_test.txt", connections_to_make=10):
    print(f"Processing file: {filename}")
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    # 1. Parse Input
    junction_boxes = []
    with open(file_path, "r") as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Convert "162,817,812" -> (162, 817, 812)
        coords = tuple(map(int, line.split(",")))
        junction_boxes.append(coords)

    # 2. Generate all possible edges (pairs of boxes)
    edges = []
    num_boxes = len(junction_boxes)

    for i in range(num_boxes):
        for j in range(i + 1, num_boxes):
            p1 = junction_boxes[i]
            p2 = junction_boxes[j]

            # Calculate 3D Euclidean distance
            dist = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)
            # Store as (distance, index_1, index_2)
            edges.append((dist, i, j))

    # 3. Sort edges by distance (shortest first)
    edges.sort(key=lambda x: x[0])

    # 4. Process the "10 shortest connections"
    uf = UnionFind(num_boxes)

    # Ensure we don't crash if input is tiny (fewer than 10 edges)
    limit = min(len(edges), connections_to_make)

    print(f"Attempting the first {limit} connections...")

    for k in range(limit):
        dist, u, v = edges[k]
        was_merged = uf.union(u, v)
        _status = "merged" if was_merged else "already connected"
        # Optional: Print detail similar to the prompt example
        # print(f"Connection {k+1}: Box {u} <-> Box {v} (dist {dist:.2f}) -> {status}")

    # 5. Calculate Result
    # Get all circuit sizes
    sizes = uf.get_component_sizes()

    # Sort sizes descending to find the largest ones
    sizes.sort(reverse=True)

    # Multiply the 3 largest sizes
    # (Safety check: assumes at least 3 circuits exist, which is true for the puzzle input)
    result = 1
    if len(sizes) >= 3:
        result = sizes[0] * sizes[1] * sizes[2]
        print(f"Largest circuit sizes: {sizes[:3]}")
    else:
        # Fallback for tiny inputs
        for s in sizes:
            result *= s
        print(f"Circuit sizes: {sizes}")

    print(f"Result: {result}")


def part2(filename: str = "input_test.txt"):
    print(f"Processing file: {filename}")
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    # 1. Parse Input
    junction_boxes = []
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return

    for line in lines:
        line = line.strip()
        if not line:
            continue
        coords = tuple(map(int, line.split(",")))
        junction_boxes.append(coords)

    num_boxes = len(junction_boxes)
    print(f"Found {num_boxes} junction boxes.")

    # 2. Generate and Sort Edges
    # ... (Edge generation and sorting logic remains the same) ...
    edges = []
    for i in range(num_boxes):
        for j in range(i + 1, num_boxes):
            p1 = junction_boxes[i]
            p2 = junction_boxes[j]
            # Use squared distance for sorting speed if needed, but for simplicity/clarity,
            # we'll keep the full distance calculation as before.
            dist = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)
            # Store distance and original indices
            edges.append((dist, i, j))

    print("Sorting all pairs by distance...")
    edges.sort(key=lambda x: x[0])

    # 3. Find the Last Connection
    uf = UnionFind(num_boxes)
    successful_merges = 0
    final_pair_indices = None

    # We need N - 1 successful merges to connect N nodes into one circuit.
    target_merges = num_boxes - 1

    print(f"Targeting {target_merges} successful merges...")

    for k in range(len(edges)):
        dist, u_idx, v_idx = edges[k]

        # Attempt to merge the two boxes
        was_merged = uf.union(u_idx, v_idx)

        if was_merged:
            successful_merges += 1

            # If this was the final successful merge, record the pair and break
            if successful_merges == target_merges:
                final_pair_indices = (u_idx, v_idx)
                # print(f"Connection {successful_merges}: Final merge found at edge index {k}")
                break

        # Safety break if we run out of edges
        if k == len(edges) - 1 and successful_merges < target_merges:
            print("Error: Ran out of edges before connecting all boxes.")

    # 4. Calculate the Final Result
    if final_pair_indices:
        idx1, idx2 = final_pair_indices
        x1 = junction_boxes[idx1][0]
        x2 = junction_boxes[idx2][0]

        result = x1 * x2

        print(f"\nThe last two junction boxes connected were at indices {idx1} (X={x1}) and {idx2} (X={x2}).")
        print(f"Multiplying their X coordinates ({x1} * {x2}) gives:")
        print(f"Result: {result}")
        return result
    else:
        print("Could not find the final connecting pair.")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1], connections_to_make=1000)
        part2(sys.argv[1])
    else:
        main(connections_to_make=10)
        part2()

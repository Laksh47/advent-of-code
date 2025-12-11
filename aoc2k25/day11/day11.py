import sys
from functools import lru_cache
from pathlib import Path


def parse_graph(lines):
    graph = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        name, rest = line.split(":")
        targets = rest.strip().split() if rest.strip() else []
        graph[name.strip()] = targets
    return graph


def count_paths(graph, start, end, must_visit=None):
    """
    Count all paths from start -> end.
    If must_visit is provided (list or set), count only paths that visit all of them.
    """

    # Normalize must_visit
    if not must_visit:
        must_visit = []
    else:
        must_visit = list(must_visit)

    index = {node: i for i, node in enumerate(must_visit)}
    full_mask = (1 << len(must_visit)) - 1

    @lru_cache(None)
    def dfs(node, mask):
        # If node is a required point, update mask
        if node in index:
            mask |= 1 << index[node]

        # End condition
        if node == end:
            # Must visit all required nodes
            return 1 if mask == full_mask else 0

        total = 0
        for nxt in graph.get(node, []):
            total += dfs(nxt, mask)
        return total

    return dfs(start, 0)


# ---------------------------------------------------------------------


def main(filename: str = "input_test.txt"):
    print(f"Processing file: {filename}")
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename

    with open(file_path, "r") as file:
        lines = file.readlines()

    graph = parse_graph(lines)

    # --------------------- PART 1 ---------------------
    if "you" in graph:
        part1 = count_paths(graph, "you", "out")
        print(f"Part 1: Number of paths from 'you' to 'out' = {part1}")

    # --------------------- PART 2 ---------------------
    if "svr" in graph:
        part2 = count_paths(graph, "svr", "out", {"dac", "fft"})
        print(f"Part 2: Number of paths from 'svr' to 'out' visiting dac and fft = {part2}")

    print("Done.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

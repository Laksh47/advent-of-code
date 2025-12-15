# save as day12_christmas_both_solvers.py
import re
import sys
import time
from collections import defaultdict
from pathlib import Path


# ---------- Parsing (robust) ----------
def parse_input(lines):
    shapes = {}
    i = 0
    # read shapes block
    while i < len(lines):
        line = lines[i].rstrip("\n")
        if not line.strip():
            i += 1
            continue
        # If region line starts, break
        if re.match(r"^\d+x\d+\s*:", line):
            break
        m = re.match(r"^(\d+):\s*$", line)
        if not m:
            raise ValueError(f"Unexpected shape header: {line!r}")
        idx = int(m.group(1))
        i += 1
        rows = []
        while i < len(lines):
            ln = lines[i].rstrip("\n")
            # blank or start of next block
            if not ln.strip():
                i += 1
                break
            if re.match(r"^\d+:\s*$", ln) or re.match(r"^\d+x\d+\s*:", ln):
                break
            rows.append(ln)
            i += 1
        shapes[idx] = rows
    # regions
    regions = []
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if re.match(r"^\d+:\s*$", line):
            continue
        m = re.match(r"^(\d+)x(\d+)\s*:\s*(.*)$", line)
        if not m:
            raise ValueError(f"Unexpected region line: {line!r}")
        W = int(m.group(1))
        H = int(m.group(2))
        counts = [int(x) for x in m.group(3).split()]
        regions.append((W, H, counts))
    return shapes, regions


# ---------- Shape utilities ----------
def shape_coords_from_rows(rows):
    coords = set()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "#":
                coords.add((x, y))
    return coords


def normalize(coords):
    xs = [x for x, y in coords]
    ys = [y for x, y in coords]
    minx = min(xs)
    miny = min(ys)
    return tuple(sorted(((x - minx, y - miny) for x, y in coords)))


def all_orientations(coords):
    out = set()
    for flip_x in (False, True):
        for rot in (0, 1, 2, 3):
            transformed = []
            for x, y in coords:
                xx, yy = x, y
                if flip_x:
                    xx = -xx
                for _ in range(rot):
                    xx, yy = -yy, xx
                transformed.append((xx, yy))
            out.add(normalize(transformed))
    return list(out)


def bbox(coords_tuple):
    xs = [x for x, y in coords_tuple]
    ys = [y for x, y in coords_tuple]
    return max(xs) + 1, max(ys) + 1


# ---------- Placement enumeration (returns bitmask placements) ----------
def placements_bitmasks_for_shape_in_region(orientation_coords, W, H):
    w_s, h_s = bbox(orientation_coords)
    placements = []
    for ox in range(0, W - w_s + 1):
        for oy in range(0, H - h_s + 1):
            mask = 0
            valid = True
            for sx, sy in orientation_coords:
                cx = ox + sx
                cy = oy + sy
                if not (0 <= cx < W and 0 <= cy < H):
                    valid = False
                    break
                pos = cy * W + cx
                mask |= 1 << pos
            if valid:
                placements.append(mask)
    return placements


def unique_placements_for_shape(sh_rows, W, H):
    coords = shape_coords_from_rows(sh_rows)
    orients = all_orientations(coords)
    seen = set()
    placements = []
    for o in orients:
        for m in placements_bitmasks_for_shape_in_region(o, W, H):
            if m not in seen:
                seen.add(m)
                placements.append(m)
    return placements


# ---------- Bitmask backtracking solver ----------
def can_pack_bitmask(W, H, shapes, counts, placements_cache=None):
    """
    shapes: dict mapped indices 0..n-1 -> rows list
    counts: list aligned with shapes
    placements_cache: optional dict key (t,W,H) -> placements list
    """
    # quick area check
    total_needed = 0
    for t, cnt in enumerate(counts):
        if cnt <= 0:
            continue
        total_needed += len(shape_coords_from_rows(shapes[t])) * cnt
    if total_needed > W * H:
        return False

    if placements_cache is None:
        placements_cache = {}

    shape_types = [t for t in range(len(shapes)) if counts[t] > 0]

    # precompute placement lists (bitmasks) per shape type
    placements_per_shape = {}
    for t in shape_types:
        key = (t, W, H)
        if key in placements_cache:
            plist = placements_cache[key]
        else:
            plist = unique_placements_for_shape(shapes[t], W, H)
            placements_cache[key] = plist
        if not plist:
            # If shape required but has zero placements -> impossible
            return False
        # Optional heuristic: sort placements by popcount ascending (place compact ones first)
        plist.sort(key=lambda x: x.bit_count())
        placements_per_shape[t] = plist

    # order shapes by difficulty (fewest placements first)
    order = sorted(shape_types, key=lambda t: len(placements_per_shape[t]))

    # Precompute remaining cells lower bound per future shapes for pruning:
    units_per_shape = {t: len(shape_coords_from_rows(shapes[t])) for t in shape_types}
    suffix_cells_needed = []
    acc = 0
    for t in reversed(order):
        acc += units_per_shape[t] * counts[t]
        suffix_cells_needed.append(acc)
    suffix_cells_needed = list(reversed(suffix_cells_needed))

    # Backtracking:
    sys.setrecursionlimit(10000)

    def place_shape_at_index(idx, used_mask):
        if idx == len(order):
            return True
        t = order[idx]
        needed = counts[t]
        plist = placements_per_shape[t]
        # quick pruning: remaining free cells less than needed cells
        free_cells = (W * H) - used_mask.bit_count()
        if free_cells < units_per_shape[t] * needed:
            return False
        # if there are future shapes, check combined lower bound:
        remaining_needed_after = suffix_cells_needed[idx] - units_per_shape[t] * needed
        if free_cells < (units_per_shape[t] * needed + remaining_needed_after):
            # This check is rough and often true; we keep it
            return False

        # choose k placements from plist (combinatorial selection) without overlap
        # We'll backtrack selecting placements in increasing order index to avoid permutations
        def choose_k(start_idx, k, cur_mask):
            if k == 0:
                # proceed to next shape
                return place_shape_at_index(idx + 1, cur_mask)
            # heuristic: if not enough placements left to choose k -> prune
            if start_idx >= len(plist):
                return False
            # Also compute an optimistic bound on unique cells available among remaining placements:
            # skip heavy analysis for simplicity; try placements greedily with recursion
            for j in range(start_idx, len(plist)):
                pm = plist[j]
                if pm & cur_mask:
                    continue
                # place it
                if choose_k(j + 1, k - 1, cur_mask | pm):
                    return True
            return False

        return choose_k(0, needed, used_mask)

    return place_shape_at_index(0, 0)


# ---------- DLX implementation ----------
class DLXNode:
    def __init__(self):
        self.left = self.right = self.up = self.down = self
        self.col = None
        self.row_id = None


class DLXColumn(DLXNode):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.size = 0  # number of nodes in column


class DLX:
    def __init__(self, ncols):
        self.header = DLXColumn("header")
        self.cols = []
        last = self.header
        for i in range(ncols):
            c = DLXColumn(i)
            c.left = last
            last.right = c
            last = c
            self.cols.append(c)
        last.right = self.header
        self.header.left = last
        # mapping for building rows
        self.row_nodes = {}

    def add_row(self, row_id, col_indices):
        first = None
        for ci in col_indices:
            col = self.cols[ci]
            node = DLXNode()
            node.col = col
            node.row_id = row_id
            # insert into column at bottom
            node.up = col.up
            node.down = col
            col.up.down = node
            col.up = node
            col.size += 1
            if first is None:
                first = node
                node.left = node.right = node
            else:
                # link into row (circular)
                node.left = first.left
                node.right = first
                first.left.right = node
                first.left = node
        self.row_nodes[row_id] = first

    def cover(self, col):
        # remove column header
        col.right.left = col.left
        col.left.right = col.right
        # remove rows
        i = col.down
        while i is not col:
            j = i.right
            while j is not i:
                j.down.up = j.up
                j.up.down = j.down
                j.col.size -= 1
                j = j.right
            i = i.down

    def uncover(self, col):
        i = col.up
        while i is not col:
            j = i.left
            while j is not i:
                j.col.size += 1
                j.down.up = j
                j.up.down = j
                j = j.left
            i = i.up
        col.right.left = col
        col.left.right = col

    def search(self, k=0, solution_limit=1, required_col_indices=None):
        """
        required_col_indices: set of column indices that must be covered (we will treat them as primary)
        returns True if a solution found (short-circuits on first solution)
        """
        if required_col_indices is None:
            required_col_indices = set()

        # If no required columns remain (i.e., they are all removed), success
        # We'll check presence of any required-related header in the circular list
        def any_required_present():
            h = self.header.right
            while h is not self.header:
                if h.name in required_col_indices:
                    return True
                h = h.right
            return False

        if not any_required_present():
            return True

        # choose column with smallest size among required columns
        # iterate header->right to find eligible column
        # find col object for chosen index
        best = None
        h = self.header.right
        while h is not self.header:
            if h.name in required_col_indices:
                if best is None or h.size < best.size:
                    best = h
            h = h.right
        if best is None:
            # no required columns left
            return True

        col = best
        # if no rows -> dead end
        if col.size == 0:
            return False

        # cover and try
        self.cover(col)
        r = col.down
        while r is not col:
            # cover other columns in the row
            j = r.right
            while j is not r:
                self.cover(j.col)
                j = j.right
            # recurse
            found = self.search(k + 1, solution_limit, required_col_indices)
            if found:
                return True
            # uncover in reverse
            j = r.left
            while j is not r:
                self.uncover(j.col)
                j = j.left
            r = r.down
        self.uncover(col)
        return False


def build_exact_cover_model(W, H, shapes, counts):
    """
    Build exact-cover matrix columns:
      - cell columns: 0..(W*H-1)
      - instance columns: next columns for each present instance (shape t with count c gives c columns)
    Rows:
      For each placement (unique cells set) of shape t create a row that includes:
          - the cell columns (cells occupied)
          - one instance column for that shape (representing "this placement is used to fill that instance")
      BUT to avoid duplicating placements per instance, we'll still create a row for each (placement × instance_column)
      (DLX will handle it efficiently)
    Returns: (ncols, list_of_rows, required_instance_cols_set)
    """
    n_cell_cols = W * H
    instance_cols = []
    shape_inst_cols = {}
    next_col = n_cell_cols
    for t, c in enumerate(counts):
        shape_inst_cols[t] = []
        for inst in range(c):
            shape_inst_cols[t].append(next_col)
            instance_cols.append(next_col)
            next_col += 1

    rows = []
    # orientations
    shape_orients = {}
    for t, r in shapes.items():
        shape_orients[t] = all_orientations(shape_coords_from_rows(r))
    for t, c in enumerate(counts):
        if c <= 0:
            continue
        placements_set = set()
        for orient in shape_orients[t]:
            # enumerate placements by cell indices
            w_s, h_s = bbox(orient)
            for ox in range(0, W - w_s + 1):
                for oy in range(0, H - h_s + 1):
                    cells = []
                    ok = True
                    for sx, sy in orient:
                        cx = ox + sx
                        cy = oy + sy
                        if not (0 <= cx < W and 0 <= cy < H):
                            ok = False
                            break
                        cells.append(cy * W + cx)
                    if not ok:
                        continue
                    cells_t = tuple(sorted(cells))
                    if cells_t in placements_set:
                        continue
                    placements_set.add(cells_t)
                    # for each instance column, create a row mapping this placement to that instance
                    for inst_col in shape_inst_cols[t]:
                        rows.append((cells_t, inst_col))
    # convert rows into list of column indices
    rows_cols = []
    for cells_t, inst_col in rows:
        cols = [c for c in cells_t]
        cols.append(inst_col)
        rows_cols.append(cols)
    return next_col, rows_cols, set(instance_cols)


def can_pack_dlx(W, H, shapes, counts):
    # quick area check
    total_needed = 0
    for t, cnt in enumerate(counts):
        if cnt <= 0:
            continue
        total_needed += len(shape_coords_from_rows(shapes[t])) * cnt
    if total_needed > W * H:
        return False

    ncols, rows_cols, required_instance_cols = build_exact_cover_model(W, H, shapes, counts)
    if not required_instance_cols:
        return True
    # If any required column has zero possible rows -> impossible
    possible_rows_by_col = defaultdict(int)
    for rcols in rows_cols:
        for c in rcols:
            possible_rows_by_col[c] += 1
    for rc in required_instance_cols:
        if possible_rows_by_col[rc] == 0:
            return False

    dlx = DLX(ncols)
    for ridx, cols in enumerate(rows_cols):
        dlx.add_row(ridx, cols)
    # DLX expects column objects; our DLXColumn.name stores the numeric index (0..ncols-1)
    # We'll pass required_instance_cols directly
    return dlx.search(required_col_indices=required_instance_cols)


# ---------- Main runner ----------
def remap_shapes_to_dense(shapes):
    shape_keys = sorted(shapes.keys())
    key_map = {old: new for new, old in enumerate(shape_keys)}
    shapes_mapped = {new: shapes[old] for old, new in key_map.items()}
    return shapes_mapped, key_map


def remap_counts_line(counts_line, key_map, n_shapes):
    # counts_line is aligned with original indices; we must produce a list length n_shapes
    counts = []
    # inverse map
    inv = {v: k for k, v in key_map.items()}
    for new_idx in range(n_shapes):
        orig_idx = inv[new_idx]
        if orig_idx < len(counts_line):
            counts.append(counts_line[orig_idx])
        else:
            counts.append(0)
    return counts


def main(filename="input_test.txt", only=None):
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / filename
    with open(file_path, "r") as f:
        lines = f.readlines()

    shapes, regions = parse_input(lines)
    shapes_mapped, key_map = remap_shapes_to_dense(shapes)
    n_shapes = len(shapes_mapped)

    print(f"Loaded {n_shapes} shapes, {len(regions)} regions from {filename}")

    # caches
    placements_cache = {}  # (t,W,H)->list of masks

    total_fit_bitmask = 0
    total_fit_dlx = 0

    for W, H, counts_line in regions:
        counts = remap_counts_line(counts_line, key_map, n_shapes)
        print(f"\nRegion {W}x{H} counts={counts}")

        # run bitmask solver
        t0 = time.perf_counter()
        try:
            ok_bit = can_pack_bitmask(W, H, shapes_mapped, counts, placements_cache=placements_cache)
        except RecursionError:
            ok_bit = False
        t1 = time.perf_counter()
        print(f"  Bitmask solver: {'fits' if ok_bit else 'does NOT fit'} (time {t1 - t0:.4f}s)")
        if ok_bit:
            total_fit_bitmask += 1

        if only == "bitmask":
            continue

        # run DLX solver
        t0 = time.perf_counter()
        ok_dlx = can_pack_dlx(W, H, shapes_mapped, counts)
        t1 = time.perf_counter()
        print(f"  DLX solver:     {'fits' if ok_dlx else 'does NOT fit'} (time {t1 - t0:.4f}s)")
        if ok_dlx:
            total_fit_dlx += 1

    print("\nSummary:")
    print(f"  Bitmask solver found {total_fit_bitmask} packable regions")
    if only != "bitmask":
        print(f"  DLX solver found     {total_fit_dlx} packable regions")
    return total_fit_bitmask, total_fit_dlx


# ---------- CLI ----------
if __name__ == "__main__":
    args = sys.argv[1:]
    only = None
    filename = "input_test.txt"
    if args:
        for a in args:
            if a == "--only-bitmask":
                only = "bitmask"
            elif a == "--only-dlx":
                only = "dlx"
            else:
                filename = a
    main(filename, only)

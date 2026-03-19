import heapq
import random
import time
import math
from enum import Enum


class Density(Enum):
    LOW    = 0.10   # 10% of cells are obstacles
    MEDIUM = 0.25   # 25% of cells are obstacles
    HIGH   = 0.40   # 40% of cells are obstacles


class Cell:
    EMPTY    = 0
    OBSTACLE = 1
    START    = 2
    GOAL     = 3
    PATH     = 4
    EXPLORED = 5


class Grid:
    """70x70 battlefield grid."""
    
    def __init__(self, rows=70, cols=70, density=Density.MEDIUM, seed=None):
        self.rows    = rows
        self.cols    = cols
        self.density = density
        self.seed    = seed
        self.grid    = [[Cell.EMPTY] * cols for _ in range(rows)]
        self._generate_obstacles()
    
    def _generate_obstacles(self):
        rng = random.Random(self.seed)
        for r in range(self.rows):
            for c in range(self.cols):
                if rng.random() < self.density.value:
                    self.grid[r][c] = Cell.OBSTACLE
    
    def is_valid(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols
    
    def is_free(self, r, c):
        return self.is_valid(r, c) and self.grid[r][c] != Cell.OBSTACLE
    
    def set_cell(self, r, c, val):
        self.grid[r][c] = val
    
    def neighbors(self, r, c):
        """8-directional movement (diagonal allowed)."""
        dirs = [(-1,0),(1,0),(0,-1),(0,1),
                (-1,-1),(-1,1),(1,-1),(1,1)]
        result = []
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            if self.is_free(nr, nc):
                # Diagonal cost = sqrt(2) ≈ 1.414
                cost = 1.414 if dr != 0 and dc != 0 else 1.0
                result.append((nr, nc, cost))
        return result
    
    def obstacle_count(self):
        return sum(self.grid[r][c] == Cell.OBSTACLE
                   for r in range(self.rows) for c in range(self.cols))


def heuristic(r1, c1, r2, c2):
    """Octile distance heuristic for 8-directional movement."""
    dx = abs(r1 - r2)
    dy = abs(c1 - c2)
    return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)


def astar(grid, start, goal):
    """
    A* search on the grid.
    Returns (path, cost, nodes_explored, runtime_ms)
    """
    sr, sc = start
    gr, gc = goal
    
    t0 = time.perf_counter()
    
    # (f, g, r, c)
    open_heap = [(0 + heuristic(sr, sc, gr, gc), 0, sr, sc)]
    
    g_cost = {(sr, sc): 0}
    came_from = {(sr, sc): None}
    nodes_explored = 0
    
    while open_heap:
        f, g, r, c = heapq.heappop(open_heap)
        nodes_explored += 1
        
        if (r, c) == (gr, gc):
           
            path = []
            cur = (gr, gc)
            while cur is not None:
                path.append(cur)
                cur = came_from[cur]
            path.reverse()
            runtime_ms = (time.perf_counter() - t0) * 1000
            return path, g, nodes_explored, runtime_ms
        
        if g > g_cost.get((r, c), float('inf')):
            continue
        
        for nr, nc, move_cost in grid.neighbors(r, c):
            ng = g + move_cost
            if ng < g_cost.get((nr, nc), float('inf')):
                g_cost[(nr, nc)] = ng
                came_from[(nr, nc)] = (r, c)
                f_new = ng + heuristic(nr, nc, gr, gc)
                heapq.heappush(open_heap, (f_new, ng, nr, nc))
    
    runtime_ms = (time.perf_counter() - t0) * 1000
    return None, float('inf'), nodes_explored, runtime_ms   # No path


def visualize_grid(grid, path, start, goal, explored_cells=None, max_display=40):
    """ASCII visualization (truncated to max_display x max_display for readability)."""
    SYMBOLS = {
        Cell.EMPTY:    '·',
        Cell.OBSTACLE: '█',
        Cell.START:    'S',
        Cell.GOAL:     'G',
        Cell.PATH:     '●',
        Cell.EXPLORED: '○',
    }
    
    display_grid = [row[:] for row in grid.grid]
    
    if explored_cells:
        for (r, c) in explored_cells:
            if display_grid[r][c] == Cell.EMPTY:
                display_grid[r][c] = Cell.EXPLORED
    
    if path:
        for (r, c) in path:
            if display_grid[r][c] not in (Cell.START, Cell.GOAL, Cell.OBSTACLE):
                display_grid[r][c] = Cell.PATH
    
    sr, sc = start
    gr, gc = goal
    display_grid[sr][sc] = Cell.START
    display_grid[gr][gc] = Cell.GOAL
    
    rows_show = min(grid.rows, max_display)
    cols_show = min(grid.cols, max_display)
    
    print(f"\n  Grid visualization ({rows_show}×{cols_show} shown of {grid.rows}×{grid.cols}):")
    print("  " + "─" * (cols_show * 2 + 2))
    
    for r in range(rows_show):
        row_str = "  │ "
        for c in range(cols_show):
            row_str += SYMBOLS[display_grid[r][c]] + " "
        row_str += "│"
        print(row_str)
    
    print("  " + "─" * (cols_show * 2 + 2))
    print("  Legend: S=Start  G=Goal  ●=Path  ○=Explored  █=Obstacle  ·=Free\n")


def print_moe_report(grid, path, cost, nodes_explored, runtime_ms, start, goal, density):
    """Print Measures of Effectiveness (MOE)."""
    total_cells = grid.rows * grid.cols
    obstacle_cells = grid.obstacle_count()
    free_cells = total_cells - obstacle_cells
    
    print("\n" + "="*60)
    print("  MEASURES OF EFFECTIVENESS (MOE)")
    print("="*60)
    print(f"  Grid Size          : {grid.rows} × {grid.cols} = {total_cells} cells")
    print(f"  Obstacle Density   : {density.name} ({density.value*100:.0f}%)")
    print(f"  Obstacle Cells     : {obstacle_cells} / {total_cells} "
          f"({obstacle_cells/total_cells*100:.1f}%)")
    print(f"  Free Cells         : {free_cells}")
    print(f"  Start              : {start}")
    print(f"  Goal               : {goal}")
    
    sl_dist = math.hypot(goal[0]-start[0], goal[1]-start[1])
    print(f"\n  --- Path Quality ---")
    
    if path:
        path_len_cells = len(path)
        print(f"  Path Found         : YES ✅")
        print(f"  Path Length (cells): {path_len_cells}")
        print(f"  Path Cost (km)     : {cost:.2f}")
        print(f"  Straight-line (km) : {sl_dist:.2f}")
        print(f"  Path Optimality    : {sl_dist/cost*100:.1f}% "
              f"(ratio path/straight-line)")
        detour = (cost - sl_dist) / sl_dist * 100
        print(f"  Detour Factor      : +{detour:.1f}%")
    else:
        print(f"  Path Found         : NO ❌ (Goal unreachable)")
    
    print(f"\n  --- Algorithmic Performance ---")
    print(f"  Nodes Explored     : {nodes_explored}")
    print(f"  Search Efficiency  : {nodes_explored/free_cells*100:.1f}% of free cells")
    print(f"  Runtime            : {runtime_ms:.3f} ms")
    print("="*60 + "\n")

def run_ugv_simulation(density=Density.MEDIUM, seed=42,
                        start=(2, 2), goal=(67, 67)):
    print("\n" + "🤖 " * 20)
    print(f"  UGV NAVIGATION SIMULATION — Static Obstacles")
    print(f"  Density: {density.name} | Seed: {seed}")
    print("🤖 " * 20)
    
    # Build grid
    grid = Grid(rows=70, cols=70, density=density, seed=seed)
    
    # Ensure start and goal are free
    grid.set_cell(*start, Cell.EMPTY)
    grid.set_cell(*goal,  Cell.EMPTY)
    
    print(f"\n  Building 70×70 battlefield grid ...")
    print(f"  Obstacles placed: {grid.obstacle_count()} cells ({density.value*100:.0f}%)")
    print(f"  Running A* search from {start} to {goal} ...")
    
    path, cost, nodes_explored, runtime_ms = astar(grid, start, goal)
    
    # Visualize
    visualize_grid(grid, path, start, goal, max_display=40)
    
    # MOE
    print_moe_report(grid, path, cost, nodes_explored,
                     runtime_ms, start, goal, density)
    
    return path, cost


def compare_densities():
    """Compare all three density levels."""
    print("\n" + "="*70)
    print("  COMPARISON: All Three Obstacle Densities")
    print("="*70)
    
    results = []
    for density in [Density.LOW, Density.MEDIUM, Density.HIGH]:
        grid = Grid(70, 70, density, seed=100)
        start, goal = (2, 2), (67, 67)
        grid.set_cell(*start, Cell.EMPTY)
        grid.set_cell(*goal,  Cell.EMPTY)
        path, cost, nodes, rt = astar(grid, start, goal)
        
        found = "YES ✅" if path else "NO ❌"
        path_cost = f"{cost:.1f}" if path else "N/A"
        results.append((density.name, density.value*100, found, path_cost, nodes, f"{rt:.2f}"))
    
    print(f"\n  {'Density':<8} {'Obs%':>5}  {'Path?':<8} {'Cost(km)':>10}"
          f"  {'Nodes':>8}  {'Time(ms)':>10}")
    print(f"  {'─'*8} {'─'*5}  {'─'*8} {'─'*10}  {'─'*8}  {'─'*10}")
    for row in results:
        print(f"  {row[0]:<8} {row[1]:>4.0f}%  {row[2]:<8} {row[3]:>10}"
              f"  {row[4]:>8}  {row[5]:>10}")
    print()


if __name__ == "__main__":
    # Run with MEDIUM density (default)
    run_ugv_simulation(density=Density.MEDIUM, seed=42)
    
    # Run with HIGH density
    run_ugv_simulation(density=Density.HIGH, seed=42)
    
    # Compare all densities
    compare_densities()
    
    # Interactive: let user choose density
    print("\n  Choose obstacle density for interactive run:")
    print("  1. LOW    (10%)")
    print("  2. MEDIUM (25%)")
    print("  3. HIGH   (40%)")
    choice = input("  Enter 1/2/3 [default=2]: ").strip() or "2"
    density_map = {"1": Density.LOW, "2": Density.MEDIUM, "3": Density.HIGH}
    density = density_map.get(choice, Density.MEDIUM)
    
    try:
        seed = int(input("  Enter random seed [default=42]: ").strip() or "42")
    except ValueError:
        seed = 42
    
    run_ugv_simulation(density=density, seed=seed)

import heapq
import random
import time
import math
from collections import defaultdict
from enum import Enum

class Cell:
    EMPTY    = 0
    OBSTACLE = 1
    START    = 2
    GOAL     = 3
    PATH     = 4
    SENSOR   = 5


class DynamicGrid:
   
    def __init__(self, rows=70, cols=70, sensor_radius=5, seed=None):
        self.rows          = rows
        self.cols          = cols
        self.sensor_radius = sensor_radius
        self.rng           = random.Random(seed)
        
        # True world (unknown to UGV until sensed)
        self.true_grid     = [[Cell.EMPTY]*cols for _ in range(rows)]
        # UGV's known map (starts empty)
        self.known_grid    = [[Cell.EMPTY]*cols for _ in range(rows)]
        
        # Dynamic obstacle probability per step
        self.appear_prob   = 0.02   # chance a free cell becomes obstacle each step
        self.vanish_prob   = 0.30   # chance an obstacle disappears each step
    
    def place_initial_obstacles(self, density=0.15):
        """Scatter some initial (unknown to UGV) static-ish obstacles."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.rng.random() < density:
                    self.true_grid[r][c] = Cell.OBSTACLE
    
    def update_dynamic_obstacles(self):
        changed = set()
        for r in range(self.rows):
            for c in range(self.cols):
                if self.true_grid[r][c] == Cell.OBSTACLE:
                    if self.rng.random() < self.vanish_prob:
                        self.true_grid[r][c] = Cell.EMPTY
                        changed.add((r, c))
                else:
                    if self.rng.random() < self.appear_prob:
                        self.true_grid[r][c] = Cell.OBSTACLE
                        changed.add((r, c))
        return changed
    
    def sense(self, ugv_r, ugv_c):
        newly_discovered = []
        for dr in range(-self.sensor_radius, self.sensor_radius + 1):
            for dc in range(-self.sensor_radius, self.sensor_radius + 1):
                nr, nc = ugv_r + dr, ugv_c + dc
                if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                    continue
                if math.hypot(dr, dc) > self.sensor_radius:
                    continue
                true_val  = self.true_grid[nr][nc]
                known_val = self.known_grid[nr][nc]
                if true_val != known_val:
                    self.known_grid[nr][nc] = true_val
                    newly_discovered.append((nr, nc, known_val, true_val))
        return newly_discovered
    
    def is_free_known(self, r, c):
        return (0 <= r < self.rows and 0 <= c < self.cols and
                self.known_grid[r][c] != Cell.OBSTACLE)
    
    def is_free_true(self, r, c):
        return (0 <= r < self.rows and 0 <= c < self.cols and
                self.true_grid[r][c] != Cell.OBSTACLE)
    
    def neighbors_known(self, r, c):
        dirs = [(-1,0),(1,0),(0,-1),(0,1),
                (-1,-1),(-1,1),(1,-1),(1,1)]
        result = []
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            if self.is_free_known(nr, nc):
                cost = 1.414 if dr!=0 and dc!=0 else 1.0
                result.append((nr, nc, cost))
        return result

class DStarLite:
    INF = float('inf')
    
    def __init__(self, grid: DynamicGrid, start, goal):
        self.grid  = grid
        self.start = start
        self.goal  = goal
        self.s_last = start
        
        # g[s]  = cost-to-go from s to goal (current best known)
        # rhs[s] = one-step-lookahead cost (consistency check)
        self.g   = defaultdict(lambda: self.INF)
        self.rhs = defaultdict(lambda: self.INF)
        
        self.rhs[goal] = 0
        
        self.km = 0   # key modifier (for moved start)
        
        # Priority queue: (key, node)
        self.open_heap = []
        self.open_set  = {}  # node -> key (for lazy deletion)
        
        self._insert(goal, self._calc_key(goal))
    
    def _heuristic(self, s):
        return math.hypot(s[0] - self.start[0], s[1] - self.start[1])
    
    def _calc_key(self, s):
        g_rhs = min(self.g[s], self.rhs[s])
        return (g_rhs + self._heuristic(s) + self.km, g_rhs)
    
    def _insert(self, s, key):
        if s in self.open_set:
            del self.open_set[s]
        self.open_set[s] = key
        heapq.heappush(self.open_heap, (key, s))
    
    def _top_key(self):
        while self.open_heap:
            key, s = self.open_heap[0]
            if self.open_set.get(s) == key:
                return key
            heapq.heappop(self.open_heap)
        return (self.INF, self.INF)
    
    def _pop(self):
        while self.open_heap:
            key, s = heapq.heappop(self.open_heap)
            if self.open_set.get(s) == key:
                del self.open_set[s]
                return s, key
        return None, None
    
    def _neighbors_with_cost(self, s):
        """Backward neighbors (from s's perspective)."""
        r, c = s
        result = []
        dirs = [(-1,0),(1,0),(0,-1),(0,1),
                (-1,-1),(-1,1),(1,-1),(1,1)]
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            if self.grid.is_free_known(nr, nc):
                cost = 1.414 if dr!=0 and dc!=0 else 1.0
                result.append(((nr, nc), cost))
        return result
    
    def _update_vertex(self, s):
        if s != self.goal:
            nbrs = self._neighbors_with_cost(s)
            if nbrs:
                self.rhs[s] = min(c + self.g[n] for n, c in nbrs)
            else:
                self.rhs[s] = self.INF
        
        if s in self.open_set:
            del self.open_set[s]
        
        if self.g[s] != self.rhs[s]:
            self._insert(s, self._calc_key(s))
    
    def compute_shortest_path(self):
        """Run D* Lite until start is consistent."""
        iterations = 0
        while (self._top_key() < self._calc_key(self.start) or
               self.rhs[self.start] != self.g[self.start]):
            
            old_key = self._top_key()
            u, _ = self._pop()
            if u is None:
                break
            iterations += 1
            
            new_key = self._calc_key(u)
            if old_key < new_key:
                self._insert(u, new_key)
            elif self.g[u] > self.rhs[u]:
                self.g[u] = self.rhs[u]
                for s, _ in self._neighbors_with_cost(u):
                    self._update_vertex(s)
            else:
                self.g[u] = self.INF
                self._update_vertex(u)
                for s, _ in self._neighbors_with_cost(u):
                    self._update_vertex(s)
        
        return iterations
    
    def notify_obstacle_change(self, changed_cells):
        self.km += self._heuristic(self.s_last)
        self.s_last = self.start
        
        for (r, c) in changed_cells:
            s = (r, c)
            self._update_vertex(s)
            for nbr, _ in self._neighbors_with_cost(s):
                self._update_vertex(nbr)
    
    def update_start(self, new_start):
        self.km += self._heuristic(self.s_last)
        self.s_last = self.start
        self.start  = new_start
    
    def get_next_step(self):
        if self.rhs[self.start] == self.INF:
            return None
        
        nbrs = self._neighbors_with_cost(self.start)
        if not nbrs:
            return None
        
        best_cost = self.INF
        best_node = None
        for s, c in nbrs:
            val = c + self.g[s]
            if val < best_cost:
                best_cost = val
                best_node = s
        return best_node
    
    def extract_path(self):
        path = [self.start]
        visited = {self.start}
        cur = self.start
        
        for _ in range(10000):
            if cur == self.goal:
                return path
            nbrs = self._neighbors_with_cost(cur)
            if not nbrs:
                return None
            
            best_cost = self.INF
            best_node = None
            for s, c in nbrs:
                val = c + self.g[s]
                if val < best_cost and s not in visited:
                    best_cost = val
                    best_node = s
            
            if best_node is None or best_cost == self.INF:
                return None
            
            cur = best_node
            visited.add(cur)
            path.append(cur)
        
        return None


# ─── Simulation ───────────────────────────────────────────────────────────────

def simulate_ugv_dynamic(start=(2, 2), goal=(67, 67),
                          max_steps=5000, seed=42,
                          sensor_radius=5, dynamic=True):
    
    print("\n" + "🤖 " * 20)
    print("  UGV NAVIGATION — Dynamic Obstacles Environment")
    print("  Algorithm: D* Lite (Incremental Replanning)")
    print("🤖 " * 20)
    
    grid = DynamicGrid(70, 70, sensor_radius=sensor_radius, seed=seed)
    grid.place_initial_obstacles(density=0.15)
    
    # Ensure start and goal are free
    grid.true_grid[start[0]][start[1]] = Cell.EMPTY
    grid.true_grid[goal[0]][goal[1]]   = Cell.EMPTY
    grid.known_grid[start[0]][start[1]] = Cell.EMPTY
    grid.known_grid[goal[0]][goal[1]]   = Cell.EMPTY
    
    # Initialize D* Lite
    planner = DStarLite(grid, start, goal)
    
    # Initial sense + plan
    grid.sense(*start)
    planner.compute_shortest_path()
    
    ugv_pos      = start
    full_path    = [start]
    replans      = 0
    steps_taken  = 0
    total_sense  = 0
    stuck_count  = 0
    
    t_start = time.perf_counter()
    
    print(f"\n  Simulating UGV movement (sensor_radius={sensor_radius})...")
    
    for step in range(max_steps):
        if ugv_pos == goal:
            print(f"  ✅ Goal reached in {step} steps!")
            break
        
        # 1. Update dynamic obstacles in the true world
        if dynamic:
            changed_true = grid.update_dynamic_obstacles()
        else:
            changed_true = set()
        
        # 2. Sense environment (update known_grid)
        newly_discovered = grid.sense(*ugv_pos)
        total_sense += 1
        
        # 3. If new obstacles detected, notify planner
        if newly_discovered:
            changed_positions = {(r, c) for r, c, _, _ in newly_discovered}
            planner.notify_obstacle_change(changed_positions)
            iters = planner.compute_shortest_path()
            replans += 1
        
        # 4. Get next step
        next_pos = planner.get_next_step()
        
        if next_pos is None:
            stuck_count += 1
            if stuck_count > 10:
                print(f"  ❌ UGV stuck at {ugv_pos} — no valid path found.")
                break
            continue
        else:
            stuck_count = 0
        
        # 5. Move UGV (check true grid for actual safety)
        if grid.is_free_true(*next_pos):
            planner.update_start(next_pos)
            ugv_pos = next_pos
            full_path.append(ugv_pos)
            steps_taken += 1
        else:
            # True obstacle hit — update known and replan
            grid.known_grid[next_pos[0]][next_pos[1]] = Cell.OBSTACLE
            planner.notify_obstacle_change({next_pos})
            planner.compute_shortest_path()
            replans += 1
    
    runtime_ms = (time.perf_counter() - t_start) * 1000
    
    # Visualize
    visualize_path_dynamic(grid, full_path, start, goal, sensor_radius)
    
    # MOE report
    reached = (ugv_pos == goal)
    path_cost = sum(
        math.hypot(full_path[i+1][0]-full_path[i][0],
                   full_path[i+1][1]-full_path[i][1])
        for i in range(len(full_path)-1)
    )
    sl_dist = math.hypot(goal[0]-start[0], goal[1]-start[1])
    
    print("\n" + "="*60)
    print("  MEASURES OF EFFECTIVENESS (MOE) — Dynamic UGV")
    print("="*60)
    print(f"  Algorithm          : D* Lite (Incremental Replanning)")
    print(f"  Environment        : {'DYNAMIC' if dynamic else 'STATIC'} Obstacles")
    print(f"  Sensor Radius      : {sensor_radius} cells")
    print(f"  Goal Reached       : {'YES ✅' if reached else 'NO ❌'}")
    print(f"  Steps Taken        : {steps_taken}")
    print(f"  Replanning Events  : {replans}")
    print(f"  Path Length (km)   : {path_cost:.2f}")
    print(f"  Straight-line (km) : {sl_dist:.2f}")
    if path_cost > 0:
        print(f"  Path Optimality    : {sl_dist/path_cost*100:.1f}%")
        print(f"  Detour Factor      : +{(path_cost-sl_dist)/sl_dist*100:.1f}%")
    print(f"  Total Sensor Scans : {total_sense}")
    print(f"  Runtime            : {runtime_ms:.1f} ms")
    print("="*60)
    
    return full_path, reached


def visualize_path_dynamic(grid, path, start, goal,
                            sensor_radius, max_display=40):
    """Visualize the traversed path on the known grid."""
    SYMBOLS = {
        Cell.EMPTY:    '·',
        Cell.OBSTACLE: '█',
        Cell.START:    'S',
        Cell.GOAL:     'G',
        Cell.PATH:     '●',
    }
    
    display = [row[:] for row in grid.known_grid]
    path_set = set(path)
    
    rows_show = min(grid.rows, max_display)
    cols_show = min(grid.cols, max_display)
    
    print(f"\n  Final known map + UGV path "
          f"({rows_show}×{cols_show} of {grid.rows}×{grid.cols}):")
    print("  " + "─" * (cols_show * 2 + 2))
    
    for r in range(rows_show):
        row_str = "  │ "
        for c in range(cols_show):
            if (r, c) == start:
                row_str += "S "
            elif (r, c) == goal:
                row_str += "G "
            elif (r, c) in path_set:
                row_str += "● "
            else:
                row_str += SYMBOLS[display[r][c]] + " "
        row_str += "│"
        print(row_str)
    
    print("  " + "─" * (cols_show * 2 + 2))
    print("  Legend: S=Start  G=Goal  ●=Path  █=Obstacle (known)  ·=Free\n")


def compare_static_vs_dynamic():
    """Side-by-side comparison: static replanning vs dynamic replanning."""
    print("\n" + "="*65)
    print("  COMPARISON: Static Obstacles vs Dynamic Obstacles")
    print("="*65)
    
    print("\n  [A] Static obstacles (D* Lite, no changes after start)...")
    simulate_ugv_dynamic(dynamic=False, seed=10, max_steps=2000)
    
    print("\n  [B] Dynamic obstacles (D* Lite, obstacles change each step)...")
    simulate_ugv_dynamic(dynamic=True,  seed=10, max_steps=2000)


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  ASSIGNMENT 3: UGV with Dynamic Obstacles (D* Lite)")
    print("=" * 60)
    
    # Default simulation
    simulate_ugv_dynamic(
        start=(2, 2), goal=(67, 67),
        max_steps=3000, seed=42,
        sensor_radius=5, dynamic=True
    )
    
    # Comparison
    compare_static_vs_dynamic()
    
    # Interactive
    print("\n  INTERACTIVE MODE")
    print("  ─────────────────")
    try:
        seed = int(input("  Enter random seed [42]: ").strip() or "42")
        radius = int(input("  Sensor radius (3–10) [5]: ").strip() or "5")
    except ValueError:
        seed, radius = 42, 5
    
    simulate_ugv_dynamic(
        start=(2, 2), goal=(67, 67),
        max_steps=3000, seed=seed,
        sensor_radius=radius, dynamic=True
    )

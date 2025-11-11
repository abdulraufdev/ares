"""Core gameplay logic and state management."""
import time
from core.grid import Grid
from core.models import Agent, Stats
from algorithms import bfs, dfs, ucs, greedy, astar

class Game:
    """Manages game state and pathfinding."""
    
    def __init__(self, grid: Grid, player: Agent, enemy: Agent):
        """Initialize game with grid and agents."""
        self.grid = grid
        self.player = player
        self.enemy = enemy
        self.path: list[tuple[int, int]] = []
        self.stats = Stats()
    
    def compute_path(self, algo: str) -> None:
        """Compute path using specified algorithm."""
        start = self.player.pos
        goal = self.enemy.pos
        
        # Time the computation
        start_time = time.perf_counter()
        
        # Select algorithm
        if algo == 'BFS':
            self.path, self.stats = bfs.find_path(self.grid, start, goal)
        elif algo == 'DFS':
            self.path, self.stats = dfs.find_path(self.grid, start, goal)
        elif algo == 'UCS':
            self.path, self.stats = ucs.find_path(self.grid, start, goal)
        elif algo == 'Greedy':
            self.path, self.stats = greedy.find_path(self.grid, start, goal)
        elif algo == 'A*':
            self.path, self.stats = astar.find_path(self.grid, start, goal)
        else:
            self.path = []
            self.stats = Stats()
        
        # Record computation time
        end_time = time.perf_counter()
        self.stats.compute_ms = (end_time - start_time) * 1000
        
        # Update player path
        self.player.path = self.path
        self.player.path_index = 0
    
    def step_along_path(self) -> bool:
        """Move player one step along path. Returns True if moved."""
        if not self.player.path or self.player.path_index >= len(self.player.path):
            return False
        
        self.player.pos = self.player.path[self.player.path_index]
        self.player.path_index += 1
        return True

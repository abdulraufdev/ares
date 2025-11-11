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
        self.path: list[tuple[int, int]] = []  # Enemy path
        self.stats = Stats()
        
        # Player movement tracking
        self.player_target: tuple[int, int] | None = None
        self.player_path: list[tuple[int, int]] = []
        self.player_moving = False
        
        # Enemy movement tracking
        self.enemy_path: list[tuple[int, int]] = []
        self.enemy_path_index = 0
        
        # Live stats tracking
        self.current_algo = 'BFS'
        self.current_path_cost = 0.0
        self.nodes_explored = 0
        self.game_start_time = 0
    
    def compute_path(self, algo: str) -> None:
        """Compute path using specified algorithm."""
        self.current_algo = algo
        start = self.enemy.pos
        goal = self.player.pos
        
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
        
        # Update enemy path (skip first position which is current position)
        if self.path and len(self.path) > 1:
            self.enemy_path = self.path[1:]
        else:
            self.enemy_path = []
        self.enemy_path_index = 0
        
        # Update live stats
        self.nodes_explored = self.stats.nodes_expanded
        self.current_path_cost = self.stats.path_cost
    
    def step_along_path(self) -> bool:
        """Move enemy one step along path. Returns True if moved."""
        if not self.enemy_path or self.enemy_path_index >= len(self.enemy_path):
            return False
        
        self.enemy.pos = self.enemy_path[self.enemy_path_index]
        self.enemy_path_index += 1
        
        # Update current path cost in real-time
        if self.enemy_path_index < len(self.enemy_path):
            self.update_live_path_cost()
        
        return True
    
    def update_live_path_cost(self):
        """Calculate current path cost based on remaining path."""
        if not self.enemy_path or self.enemy_path_index >= len(self.enemy_path):
            self.current_path_cost = 0.0
            return
        
        # Calculate cost of remaining path
        cost = 0.0
        for i in range(self.enemy_path_index, len(self.enemy_path) - 1):
            cost += self.grid.step_cost(self.enemy_path[i], self.enemy_path[i + 1])
        self.current_path_cost = cost
    
    def handle_player_click(self, grid_pos: tuple[int, int]):
        """Handle player clicking a node to move there."""
        # Check if position is valid
        if not self.grid.in_bounds(grid_pos) or not self.grid.passable(grid_pos):
            return
        
        # Set player target
        self.player_target = grid_pos
        
        # Calculate path for player using A* (player uses smart pathfinding)
        from algorithms import astar
        path, _ = astar.find_path(self.grid, self.player.pos, grid_pos)
        
        if path and len(path) > 1:
            # Skip first position (current position)
            self.player_path = path[1:]
            self.player_moving = True
            self.player.path_index = 0
        else:
            # Already at target or no path
            self.player_moving = False
    
    def update_player_movement(self):
        """Move player along their path - ONLY if they clicked."""
        if not self.player_moving or not self.player_path:
            return
        
        if self.player.path_index < len(self.player_path):
            self.player.pos = self.player_path[self.player.path_index]
            self.player.path_index += 1
            
            # Stop when reached target
            if self.player.path_index >= len(self.player_path):
                self.player_moving = False
                self.player_target = None

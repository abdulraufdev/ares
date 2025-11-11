"""Core gameplay logic and state management."""
import time
from core.graph import Graph
from core.models import Agent, Stats
from algorithms import bfs, dfs, ucs, greedy, astar
from config import ANIMATION_SPEEDS


class Game:
    """Manages game state and pathfinding."""
    
    def __init__(self, graph: Graph, player: Agent, enemy: Agent):
        """Initialize game with graph and agents."""
        self.graph = graph
        self.player = player
        self.enemy = enemy
        self.player_path: list[int] = []
        self.enemy_path: list[int] = []
        self.stats = Stats()
        self.visited_nodes: set[int] = set()
        self.current_algo = 'BFS'
    
    def compute_player_path(self, algo: str) -> None:
        """Compute player path to enemy using specified algorithm."""
        self.current_algo = algo
        start = self.player.pos
        goal = self.enemy.pos
        
        # Time the computation
        start_time = time.perf_counter()
        
        # Select algorithm
        if algo == 'BFS':
            self.player_path, self.stats = bfs.find_path(self.graph, start, goal)
        elif algo == 'DFS':
            self.player_path, self.stats = dfs.find_path(self.graph, start, goal)
        elif algo == 'UCS':
            self.player_path, self.stats = ucs.find_path(self.graph, start, goal)
        elif algo == 'Greedy':
            self.player_path, self.stats = greedy.find_path(self.graph, start, goal)
        elif algo == 'A*':
            self.player_path, self.stats = astar.find_path(self.graph, start, goal)
        else:
            self.player_path = []
            self.stats = Stats()
        
        # Record computation time
        end_time = time.perf_counter()
        self.stats.compute_ms = (end_time - start_time) * 1000
        
        # Update player path
        self.player.path = self.player_path
        self.player.path_index = 0
        self.visited_nodes = set()
    
    def compute_enemy_path(self) -> None:
        """Compute enemy path from enemy to player for visualization."""
        start = self.enemy.pos
        goal = self.player.pos
        
        # Use same algorithm as player for consistency
        if self.current_algo == 'BFS':
            self.enemy_path, _ = bfs.find_path(self.graph, start, goal)
        elif self.current_algo == 'DFS':
            self.enemy_path, _ = dfs.find_path(self.graph, start, goal)
        elif self.current_algo == 'UCS':
            self.enemy_path, _ = ucs.find_path(self.graph, start, goal)
        elif self.current_algo == 'Greedy':
            self.enemy_path, _ = greedy.find_path(self.graph, start, goal)
        elif self.current_algo == 'A*':
            self.enemy_path, _ = astar.find_path(self.graph, start, goal)
        else:
            self.enemy_path = []
    
    def step_along_path(self) -> bool:
        """Move player one step along path. Returns True if moved."""
        if not self.player.path or self.player.path_index >= len(self.player.path):
            return False
        
        # Mark current position as visited
        if self.player.path_index > 0:
            self.visited_nodes.add(self.player.path[self.player.path_index - 1])
        
        self.player.pos = self.player.path[self.player.path_index]
        self.player.path_index += 1
        
        # Recompute enemy path when player moves
        self.compute_enemy_path()
        
        return True
    
    def get_animation_speed(self) -> float:
        """Get animation speed in seconds based on current algorithm and edge."""
        if not self.player.path or self.player.path_index < 1:
            return 0.5
        
        # Get current edge info
        from_id = self.player.path[self.player.path_index - 1]
        to_id = self.player.path[self.player.path_index] if self.player.path_index < len(self.player.path) else from_id
        
        # Get edge weight
        weight = self.graph.step_cost(from_id, to_id)
        
        # Get heuristic distance
        goal = self.enemy.pos
        heuristic = self.graph.heuristic(to_id, goal)
        
        # Calculate f-cost for A*
        g_cost = weight
        f_cost = g_cost + heuristic
        
        # Get speed function for current algorithm
        speed_func = ANIMATION_SPEEDS.get(self.current_algo, lambda w, h, f: 0.5)
        return speed_func(weight, heuristic, f_cost)


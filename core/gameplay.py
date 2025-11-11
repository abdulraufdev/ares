"""Core gameplay logic and state management."""
import time
from typing import Optional
from core.grid import Grid
from core.models import Agent, Stats
from core.node import Node
from core.combat import CombatSystem
from core.abilities import AbilityManager
from core.graph import GraphGenerator
from algorithms import bfs, dfs, ucs, greedy, astar
from config import ENEMY_PATHFIND_INTERVAL, MAP_TYPES


class Game:
    """Manages game state and pathfinding."""
    
    def __init__(self, grid: Grid, player: Agent, enemy: Agent):
        """Initialize game with grid and agents."""
        self.grid = grid
        self.player = player
        self.enemy = enemy
        self.path: list[tuple[int, int]] = []
        self.enemy_path: list[tuple[int, int]] = []
        self.stats = Stats()
        
        # Game systems
        self.combat_system = CombatSystem()
        self.ability_manager = AbilityManager()
        
        # Timing
        self.last_enemy_pathfind = 0.0
        self.last_player_move = 0.0
        self.last_enemy_move = 0.0
        
        # Node-based graph
        self.nodes: Optional[list[list[Node]]] = None
        self.graph_generator = GraphGenerator(grid.w, grid.h)
        
        # Track starting positions for reset
        self.player_start = player.pos
        self.enemy_start = enemy.pos
        
        # Game state
        self.game_over = False
        self.winner: Optional[str] = None
    
    def compute_path(self, algo: str, from_pos: Optional[tuple[int, int]] = None, 
                    to_pos: Optional[tuple[int, int]] = None) -> None:
        """Compute path using specified algorithm."""
        start = from_pos if from_pos else self.player.pos
        goal = to_pos if to_pos else self.enemy.pos
        
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
        
        # Update player path if computing for player
        if from_pos is None:
            self.player.path = self.path
            self.player.path_index = 0
    
    def compute_enemy_path(self, algo: str, current_time: float) -> None:
        """
        Compute enemy path to player (FIXES CONTINUOUS PATHFINDING BUG).
        
        Args:
            algo: Algorithm to use
            current_time: Current time in milliseconds
        """
        # Check if enough time has passed since last pathfind
        if current_time - self.last_enemy_pathfind < ENEMY_PATHFIND_INTERVAL:
            return
        
        start = self.enemy.pos
        goal = self.player.pos
        
        # Compute path
        start_time = time.perf_counter()
        
        if algo == 'BFS':
            self.enemy_path, enemy_stats = bfs.find_path(self.grid, start, goal)
        elif algo == 'DFS':
            self.enemy_path, enemy_stats = dfs.find_path(self.grid, start, goal)
        elif algo == 'UCS':
            self.enemy_path, enemy_stats = ucs.find_path(self.grid, start, goal)
        elif algo == 'Greedy':
            self.enemy_path, enemy_stats = greedy.find_path(self.grid, start, goal)
        elif algo == 'A*':
            self.enemy_path, enemy_stats = astar.find_path(self.grid, start, goal)
        else:
            self.enemy_path = []
        
        # Update enemy path
        self.enemy.path = self.enemy_path
        self.enemy.path_index = 0
        
        # Update timing
        self.last_enemy_pathfind = current_time
    
    def step_along_path(self) -> bool:
        """Move player one step along path. Returns True if moved."""
        if not self.player.path or self.player.path_index >= len(self.player.path):
            return False
        
        self.player.pos = self.player.path[self.player.path_index]
        self.player.path_index += 1
        return True
    
    def step_enemy(self, current_time: float) -> bool:
        """
        Move enemy one step along its path.
        
        Args:
            current_time: Current time in milliseconds
            
        Returns:
            True if enemy moved
        """
        if not self.enemy.path or self.enemy.path_index >= len(self.enemy.path):
            return False
        
        self.enemy.pos = self.enemy.path[self.enemy.path_index]
        self.enemy.path_index += 1
        self.last_enemy_move = current_time
        return True
    
    def move_player_to(self, target_pos: tuple[int, int], algo: str) -> bool:
        """
        Move player to target position (click-to-move).
        
        Args:
            target_pos: Target grid position
            algo: Algorithm to use for pathfinding
            
        Returns:
            True if path was computed
        """
        # Check if target is valid
        x, y = target_pos
        if not self.grid.in_bounds(target_pos) or not self.grid.passable(target_pos):
            return False
        
        # Compute path from player to target
        self.compute_path(algo, from_pos=self.player.pos, to_pos=target_pos)
        
        return len(self.path) > 0
    
    def update_combat(self, current_time: float) -> None:
        """
        Update combat system.
        
        Args:
            current_time: Current time in milliseconds
        """
        # Apply contact damage
        self.combat_system.apply_contact_damage(self.player, self.enemy, current_time)
        
        # Check for game over
        if not self.player.is_alive():
            self.game_over = True
            self.winner = "Enemy"
        elif not self.enemy.is_alive():
            self.game_over = True
            self.winner = "Player"
    
    def use_ability(self, ability_name: str, current_time: float, 
                   target_pos: Optional[tuple[int, int]] = None) -> bool:
        """
        Use a player ability.
        
        Args:
            ability_name: Name of ability to use
            current_time: Current time in milliseconds
            target_pos: Target position (for teleport, block, weight)
            
        Returns:
            True if ability was used
        """
        if ability_name == 'shield':
            return self.ability_manager.use_shield(self.player, current_time)
        
        elif ability_name == 'teleport' and target_pos:
            # Update nodes if available
            if self.nodes:
                return self.ability_manager.use_teleport(
                    self.player, target_pos, self.nodes, current_time)
            return False
        
        elif ability_name == 'block' and target_pos:
            if self.nodes:
                success = self.ability_manager.use_block_node(
                    target_pos, self.nodes, self.player, current_time)
                if success:
                    # Update grid to match
                    x, y = target_pos
                    if self.grid.in_bounds(target_pos):
                        self.grid.blocked[y][x] = True
                return success
            return False
        
        elif ability_name == 'weight' and target_pos:
            if self.nodes:
                return self.ability_manager.use_increase_weight(
                    self.player.pos, target_pos, self.nodes, self.player, current_time)
            return False
        
        return False
    
    def generate_map(self, algo: str, seed: int = 42) -> None:
        """
        Generate appropriate map for algorithm.
        
        Args:
            algo: Algorithm name
            seed: Random seed
        """
        # Determine map type based on algorithm
        map_type = 'open'
        for mtype, algos in MAP_TYPES.items():
            if algo in algos:
                map_type = mtype
                break
        
        # Generate node graph
        self.nodes = self.graph_generator.generate(map_type, seed)
        
        # Update grid to match nodes
        for y in range(self.grid.h):
            for x in range(self.grid.w):
                if y < len(self.nodes) and x < len(self.nodes[0]):
                    self.grid.blocked[y][x] = not self.nodes[y][x].walkable
                    self.grid.cost[y][x] = self.nodes[y][x].weight
    
    def reset_agents(self) -> None:
        """Reset agents to starting positions."""
        self.player.pos = self.player_start
        self.enemy.pos = self.enemy_start
        self.player.path = []
        self.player.path_index = 0
        self.enemy.path = []
        self.enemy.path_index = 0

"""Core gameplay logic and state management."""
import time
from typing import Optional
from core.grid import Grid
from core.graph import Graph
from core.models import Agent, Stats
from algorithms import bfs, dfs, ucs, greedy, astar
from algorithms.graph_algorithms import bfs_graph, dfs_graph, ucs_graph, greedy_graph, astar_graph
from config import SPEED_FAST, SPEED_NORMAL, SPEED_SLOW


class Game:
    """Manages game state and pathfinding."""
    
    def __init__(self, grid: Grid = None, player: Agent = None, enemy: Agent = None, 
                 graph: Graph = None, algo: str = 'BFS'):
        """Initialize game with grid/graph and agents."""
        self.grid = grid
        self.graph = graph
        self.player = player
        self.enemy = enemy
        self.path: list[tuple[int, int]] = []
        self.stats = Stats()
        self.current_algo = algo
        
        # Graph mode attributes
        self.enemy_path: list[str] = []
        self.last_player_move_time = 0
        self.enemy_move_delay = SPEED_NORMAL
        self.last_enemy_move_time = 0
        
        # Game state
        self.game_over = False
        self.victory = False
        self.start_time = time.time()
    
    def compute_path(self, algo: str) -> None:
        """Compute path using specified algorithm (legacy grid version)."""
        if not self.grid:
            return
        
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
        """Move player one step along path. Returns True if moved (legacy)."""
        if not self.player.path or self.player.path_index >= len(self.player.path):
            return False
        
        self.player.pos = self.player.path[self.player.path_index]
        self.player.path_index += 1
        return True
    
    def compute_enemy_path(self) -> None:
        """Compute enemy path to player using selected algorithm."""
        if not self.graph or not self.player.node_label or not self.enemy.node_label:
            return
        
        start = self.enemy.node_label
        goal = self.player.node_label
        
        # Select algorithm
        if self.current_algo == 'BFS':
            self.enemy_path, self.stats = bfs_graph(self.graph, start, goal)
        elif self.current_algo == 'DFS':
            self.enemy_path, self.stats = dfs_graph(self.graph, start, goal)
        elif self.current_algo == 'UCS':
            self.enemy_path, self.stats = ucs_graph(self.graph, start, goal)
        elif self.current_algo == 'Greedy':
            self.enemy_path, self.stats = greedy_graph(self.graph, start, goal)
        elif self.current_algo == 'A*':
            self.enemy_path, self.stats = astar_graph(self.graph, start, goal)
        else:
            self.enemy_path = []
            self.stats = Stats()
        
        # Remove first element (enemy's current position)
        if self.enemy_path and len(self.enemy_path) > 1:
            self.enemy_path = self.enemy_path[1:]
    
    def move_player_to_node(self, target_label: str) -> bool:
        """
        Move player to target node.
        
        Returns:
            True if move was successful
        """
        if not self.graph or not self.player.node_label:
            return False
        
        current_node = self.graph.get_node(self.player.node_label)
        target_node = self.graph.get_node(target_label)
        
        if not current_node or not target_node:
            return False
        
        # Check if target is a neighbor
        if not current_node.is_neighbor(target_label):
            return False
        
        # Check if target is walkable
        if not target_node.walkable:
            return False
        
        # Calculate movement cost
        edge_weight = current_node.get_weight(target_label)
        
        # Update player state
        old_label = self.player.node_label
        self.player.node_label = target_label
        self.player.visited_nodes.append(target_label)
        self.player.total_cost += edge_weight
        
        # Calculate distance (visual)
        old_node = self.graph.get_node(old_label)
        if old_node:
            dist = ((target_node.pos[0] - old_node.pos[0])**2 + 
                   (target_node.pos[1] - old_node.pos[1])**2)**0.5
            self.player.total_distance += dist
        
        # Update visualization states
        self.graph.reset_visualization_states()
        target_node.occupied_by_player = True
        
        # Enemy recalculates path
        self.compute_enemy_path()
        
        self.last_player_move_time = time.time()
        
        return True
    
    def update_enemy(self, current_time: float) -> None:
        """Update enemy AI - move along path to player."""
        if not self.graph or not self.enemy.node_label or self.game_over:
            return
        
        # Check if enough time has passed for enemy to move
        if current_time - self.last_enemy_move_time < self.enemy_move_delay / 1000.0:
            return
        
        # Move enemy along path
        if self.enemy_path:
            next_node_label = self.enemy_path[0]
            next_node = self.graph.get_node(next_node_label)
            
            if next_node and next_node.walkable:
                # Calculate movement cost
                current_node = self.graph.get_node(self.enemy.node_label)
                if current_node:
                    edge_weight = current_node.get_weight(next_node_label)
                    self.enemy.total_cost += edge_weight
                    
                    # Calculate distance (visual)
                    dist = ((next_node.pos[0] - current_node.pos[0])**2 + 
                           (next_node.pos[1] - current_node.pos[1])**2)**0.5
                    self.enemy.total_distance += dist
                    
                    # Set movement delay based on edge weight
                    self.enemy_move_delay = self._get_movement_speed(edge_weight)
                
                # Move enemy
                self.enemy.node_label = next_node_label
                self.enemy_path.pop(0)
                
                # Update visualization
                self.graph.reset_visualization_states()
                next_node.occupied_by_enemy = True
                
                # Mark as visited
                if next_node_label not in self.enemy.visited_nodes:
                    self.enemy.visited_nodes.append(next_node_label)
                
                self.last_enemy_move_time = current_time
                
                # Check if enemy caught player
                if self.enemy.node_label == self.player.node_label:
                    self.game_over = True
                    self.victory = False
        else:
            # No path available - player might have trapped enemy
            # Recalculate just in case
            self.compute_enemy_path()
            if not self.enemy_path:
                # Enemy is truly trapped
                self.game_over = True
                self.victory = True
    
    def _get_movement_speed(self, weight: float) -> float:
        """Get movement speed based on edge weight."""
        if weight <= 2:
            return SPEED_FAST
        elif weight <= 5:
            return SPEED_NORMAL
        else:
            return SPEED_SLOW
    
    def update_visualization_states(self) -> None:
        """Update node visualization states based on current game state."""
        if not self.graph:
            return
        
        self.graph.reset_visualization_states()
        
        # Mark player node
        if self.player.node_label:
            player_node = self.graph.get_node(self.player.node_label)
            if player_node:
                player_node.occupied_by_player = True
                player_node.is_target = False
        
        # Mark enemy node
        if self.enemy.node_label:
            enemy_node = self.graph.get_node(self.enemy.node_label)
            if enemy_node:
                enemy_node.occupied_by_enemy = True
        
        # Mark visited nodes
        for label in self.enemy.visited_nodes:
            node = self.graph.get_node(label)
            if node and not node.occupied_by_enemy and not node.occupied_by_player:
                node.visited_by_enemy = True
        
        # Mark nodes in enemy's path (open list)
        for label in self.enemy_path[:3]:  # Only show next few nodes
            node = self.graph.get_node(label)
            if node and not node.occupied_by_player:
                node.in_open_list = True
    
    def get_survival_time(self) -> float:
        """Get the time survived in seconds."""
        return time.time() - self.start_time
    
    def is_node_adjacent_to_player(self, node_label: str) -> bool:
        """Check if a node is adjacent to the player's current node."""
        if not self.graph or not self.player.node_label:
            return False
        
        player_node = self.graph.get_node(self.player.node_label)
        if not player_node:
            return False
        
        return player_node.is_neighbor(node_label)

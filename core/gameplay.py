"""Core gameplay logic and state management."""
import time
from typing import Optional
from core.arena import Arena
from core.models import Agent, Stats, MovementSegment
from algorithms import bfs, dfs, ucs, greedy, astar
from config import get_animation_duration

class Game:
    """Manages game state and pathfinding."""
    
    def __init__(self, arena: Arena, player: Agent, enemy: Agent, goal: int):
        """Initialize game with arena and agents."""
        self.arena = arena
        self.player = player
        self.enemy = enemy
        self.goal = goal
        self.path: list[int] = []
        self.stats = Stats()
        self.current_algo = 'BFS'
        self.game_over = False
        self.victory = False
        self.defeat_reason = ""
    
    def compute_path(self, algo: str) -> None:
        """Compute path using specified algorithm."""
        self.current_algo = algo
        start = self.enemy.pos  # Enemy pathfinding to player
        goal = self.player.pos
        
        # Time the computation
        start_time = time.perf_counter()
        
        # Select algorithm
        if algo == 'BFS':
            self.path, enemy_stats = bfs.find_path(self.arena, start, goal)
        elif algo == 'DFS':
            self.path, enemy_stats = dfs.find_path(self.arena, start, goal)
        elif algo == 'UCS':
            self.path, enemy_stats = ucs.find_path(self.arena, start, goal)
        elif algo == 'Greedy':
            self.path, enemy_stats = greedy.find_path(self.arena, start, goal)
        elif algo == 'A*':
            self.path, enemy_stats = astar.find_path(self.arena, start, goal)
        else:
            self.path = []
            enemy_stats = Stats()
        
        # Record computation time
        end_time = time.perf_counter()
        enemy_stats.compute_ms = (end_time - start_time) * 1000
        
        # Track enemy exploration
        self.stats.enemy_nodes_explored += enemy_stats.nodes_expanded
        self.stats.enemy_path_recalculations += 1
        
        # Update max frontier size if available
        if hasattr(enemy_stats, 'max_frontier_size'):
            self.stats.max_frontier_size = max(self.stats.max_frontier_size, enemy_stats.max_frontier_size)
        
        # Update enemy path
        self.enemy.path = self.path
        self.enemy.path_index = 0
    
    def start_movement(self, agent: Agent, target_node: int, current_time: float) -> None:
        """Start an animated movement for an agent."""
        weight = self.arena.step_cost(agent.pos, target_node)
        duration = get_animation_duration(weight)
        
        agent.movement_segment = MovementSegment(
            origin_node=agent.pos,
            target_node=target_node,
            start_time=current_time,
            duration=duration,
            weight=weight
        )
    
    def update_movement(self, agent: Agent, current_time: float) -> bool:
        """Update agent movement animation. Returns True if movement completed."""
        if agent.movement_segment is None:
            return False
        
        if agent.movement_segment.is_complete(current_time):
            # Movement complete, update logical position
            agent.pos = agent.movement_segment.target_node
            
            # Track distance/cost traveled
            if agent == self.player:
                self.stats.distance_traveled += 1  # Count nodes
                self.stats.cost_traveled += agent.movement_segment.weight
                self.stats.path_len += 1
            
            agent.movement_segment = None
            return True
        
        return False
    
    def try_move_player(self, target_node: int, current_time: float) -> bool:
        """Try to move player to target node. Returns True if successful."""
        # Don't move if already in transit
        if self.player.in_transit:
            return False
        
        # Check if target is a valid neighbor
        neighbors = list(self.arena.neighbors(self.player.pos))
        if target_node not in neighbors:
            return False
        
        # Start movement
        self.start_movement(self.player, target_node, current_time)
        return True
    
    def step_enemy_along_path(self, current_time: float) -> bool:
        """Move enemy one step along path. Returns True if moved."""
        # Don't move if already in transit
        if self.enemy.in_transit:
            return False
        
        if not self.enemy.path or self.enemy.path_index >= len(self.enemy.path):
            return False
        
        target_node = self.enemy.path[self.enemy.path_index]
        self.start_movement(self.enemy, target_node, current_time)
        self.enemy.path_index += 1
        return True
    
    def check_collision(self) -> bool:
        """Check if player and enemy are at the same logical position."""
        return (not self.player.in_transit and 
                not self.enemy.in_transit and 
                self.player.pos == self.enemy.pos)
    
    def check_victory(self) -> bool:
        """Check if player has reached the goal."""
        return not self.player.in_transit and self.player.pos == self.goal
    
    def on_player_arrival(self, current_time: float) -> None:
        """Called when player completes movement to a new node."""
        # Recalculate enemy path to new player position
        self.compute_path(self.current_algo)

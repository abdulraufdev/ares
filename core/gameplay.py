"""Core gameplay logic for Algorithm Arena."""
import pygame
import time as time_module
from core.graph import Graph
from core.node import Node
from core.combat import CombatSystem
from core.models import Stats
from algorithms.graph_algorithms import find_path
from config import *


class PlayerEntity:
    """Player character in the game."""
    
    def __init__(self, start_node: Node):
        """Initialize player.
        
        Args:
            start_node: Starting node
        """
        self.node = start_node
        self.nodes_visited = 0
        self.move_start_time = 0
        self.is_moving = False
        self.move_from = None
        self.move_to = None
        self.move_duration = 0
    
    def can_move_to(self, target_node: Node) -> bool:
        """Check if player can move to target node.
        
        Player can ALWAYS move to adjacent nodes, even when:
        - Enemy is on the same node (allows escape from combat)
        - Taking damage from enemy
        
        Args:
            target_node: Node to move to
            
        Returns:
            True if target is an adjacent neighbor
        """
        if self.is_moving:
            return False
        
        for neighbor, _ in self.node.neighbors:
            if neighbor == target_node:
                return True
        return False
    
    def start_move(self, target_node: Node, algorithm: str, current_time: int):
        """Start moving to a new node.
        
        Args:
            target_node: Destination node
            algorithm: Current algorithm (affects animation speed)
            current_time: Current time in milliseconds
        """
        self.is_moving = True
        self.move_from = self.node
        self.move_to = target_node
        self.move_start_time = current_time
        
        # Calculate animation duration based on algorithm
        if algorithm in ['BFS', 'DFS']:
            self.move_duration = int(ANIMATION_BASE_SPEED * 1000)  # 0.5 seconds
        elif algorithm == 'UCS':
            weight = self.move_from.get_weight_to(target_node)
            duration_seconds = 0.2 + (weight * 0.1)
            self.move_duration = int(duration_seconds * 1000)
        elif algorithm == 'Greedy':
            duration_seconds = 0.3 + (target_node.h_cost * 0.02)
            self.move_duration = int(min(duration_seconds, 1.5) * 1000)
        else:  # A*
            duration_seconds = 0.2 + (target_node.f_cost * 0.015)
            self.move_duration = int(min(duration_seconds, 1.5) * 1000)
    
    def update(self, current_time: int) -> bool:
        """Update player movement.
        
        Args:
            current_time: Current time in milliseconds
            
        Returns:
            True if move completed this frame
        """
        if not self.is_moving:
            return False
        
        elapsed = current_time - self.move_start_time
        if elapsed >= self.move_duration:
            # Move complete
            self.node = self.move_to
            self.nodes_visited += 1
            self.is_moving = False
            self.move_from = None
            self.move_to = None
            return True
        
        return False


class EnemyAI:
    """Enemy AI with pathfinding."""
    
    def __init__(self, start_node: Node, algorithm: str, graph):
        """Initialize enemy AI.
        
        Args:
            start_node: Starting node
            algorithm: Pathfinding algorithm to use
            graph: Game graph
        """
        self.node = start_node
        self.algorithm = algorithm
        self.graph = graph
        self.path = []
        self.path_index = 0
        self.last_move_time = 0
        self.move_delay = ENEMY_SPEEDS.get(algorithm, 500)
        self.target_node = None
        self.stats = Stats()
    
    def recalculate_path(self, target_node: Node):
        """Recalculate path to target.
        
        Args:
            target_node: New target position
        """
        if target_node == self.target_node and self.path:
            return  # Target hasn't changed
        
        self.target_node = target_node
        
        # Find path using algorithm
        self.path, self.stats = find_path(self.algorithm, self.graph, self.node, target_node)
        self.path_index = 0
    
    def update(self, current_time: int, player_node: Node) -> bool:
        """Update enemy AI.
        
        Args:
            current_time: Current time in milliseconds
            player_node: Player's current position
            
        Returns:
            True if enemy moved this frame
        """
        # Recalculate if needed
        if player_node != self.target_node:
            self.recalculate_path(player_node)
        
        # Check if we can move
        if current_time - self.last_move_time < self.move_delay:
            return False
        
        # Move along path
        if self.path and self.path_index < len(self.path) - 1:
            self.path_index += 1
            self.node = self.path[self.path_index]
            self.last_move_time = current_time
            return True
        
        return False


class GameSession:
    """Main game session managing gameplay."""
    
    def __init__(self, algorithm: str):
        """Initialize game session.
        
        Args:
            algorithm: Selected algorithm name
        """
        self.algorithm = algorithm
        self.graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_NODES, GRAPH_SEED)
        
        # Select random start positions (far apart)
        nodes = self.graph.nodes[:]
        import random
        random.shuffle(nodes)
        
        player_start = nodes[0]
        enemy_start = nodes[-1]
        
        # Ensure they're far enough apart
        while player_start.distance_to(enemy_start) < 300 and len(nodes) > 2:
            enemy_start = nodes[-2]
            nodes.pop()
        
        # Initialize entities
        self.player = PlayerEntity(player_start)
        self.enemy = EnemyAI(enemy_start, algorithm, self.graph)
        self.combat = CombatSystem()
        
        # Calculate initial path
        self.enemy.recalculate_path(self.player.node)
        
        # Game state
        self.paused = False
        self.start_time = time_module.time()
        self.game_time = 0
        self.is_victory = False
        self.is_defeat = False
    
    def handle_click(self, pos: tuple[int, int], current_time: int) -> bool:
        """Handle player click for movement.
        
        Args:
            pos: Mouse click position
            current_time: Current time in milliseconds
            
        Returns:
            True if player started moving
        """
        if self.paused or self.player.is_moving:
            return False
        
        # Find clicked node
        clicked_node = self.graph.get_node_at_pos(pos)
        if not clicked_node:
            return False
        
        # Check if it's a valid move
        if self.player.can_move_to(clicked_node):
            self.player.start_move(clicked_node, self.algorithm, current_time)
            return True
        
        return False
    
    def update(self, current_time: int, delta_time: float):
        """Update game state.
        
        Args:
            current_time: Current time in milliseconds
            delta_time: Time since last frame in seconds
        """
        if self.paused:
            return
        
        # Update game time
        self.game_time = int(time_module.time() - self.start_time)
        
        # Update player
        if self.player.update(current_time):
            # Player finished moving, enemy recalculates
            self.enemy.recalculate_path(self.player.node)
        
        # Update enemy
        self.enemy.update(current_time, self.player.node)
        
        # Check combat
        self.combat.check_contact(self.player.node, self.enemy.node, current_time)
        
        # Check game over conditions
        is_over, reason = self.combat.is_game_over()
        if is_over:
            if reason == 'victory':
                self.is_victory = True
            else:
                self.is_defeat = True
        
        # Also check if enemy has no path (victory condition)
        if not self.enemy.path and not self.is_victory:
            self.is_victory = True
    
    def toggle_pause(self):
        """Toggle pause state."""
        self.paused = not self.paused
    
    def get_player_stats(self) -> dict:
        """Get player statistics for end screen."""
        return {
            'position': self.player.node.label,
            'nodes_visited': self.player.nodes_visited,
            'hp': int(self.combat.player.hp)
        }
    
    def get_enemy_stats(self) -> dict:
        """Get enemy statistics for end screen."""
        path_string = ''
        if self.enemy.path and len(self.enemy.path) <= 8:
            path_string = ' → '.join(node.label for node in self.enemy.path)
        
        return {
            'position': self.enemy.node.label,
            'nodes_explored': self.enemy.stats.nodes_expanded,
            'path_cost': self.enemy.stats.path_cost,
            'path_length': len(self.enemy.path) if self.enemy.path else 0,
            'path_status': 'No path found' if not self.enemy.path else 'Path found',
            'path_string': path_string
        }

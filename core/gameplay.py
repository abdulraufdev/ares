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
        
        # Animation properties
        self.visual_pos = start_node.pos  # Rendered position
        self.animating = False
        self.animation_start_time = 0
        self.animation_duration = 400  # milliseconds
        self.animation_from = start_node.pos
        self.animation_to = start_node.pos
        
        # Queue-based pre-move system
        self.move_queue = []  # List of Node objects
        
        # Legacy properties for compatibility
        self.move_start_time = 0
        self.is_moving = False
        self.move_from = None
        self.move_to = None
        self.move_duration = 0
    
    def ease_in_out_cubic(self, t: float) -> float:
        """Smooth easing function for animations.
        
        Args:
            t: Progress from 0.0 to 1.0
            
        Returns:
            Eased progress value
        """
        return t * t * (3 - 2 * t)
    
    def queue_move(self, target_node: Node) -> bool:
        """Add to queue if adjacent to last queued node.
        
        Args:
            target_node: Node to add to queue
            
        Returns:
            True if successfully added to queue
        """
        if not self.move_queue:
            # First node in queue - check adjacency to current position
            if target_node in [n for n, _ in self.node.neighbors]:
                self.move_queue.append(target_node)
                return True
        else:
            # Check adjacency to last node in queue
            last_node = self.move_queue[-1]
            if target_node in [n for n, _ in last_node.neighbors]:
                self.move_queue.append(target_node)
                return True
        return False
    
    def override_queue(self, target_node: Node):
        """Replace queue (keeps current animation target).
        
        Args:
            target_node: New target node
        """
        if self.animating and self.move_queue:
            # Keep current animation target, replace rest
            current_target = self.move_queue[0]
            self.move_queue = [current_target]
            if target_node in [n for n, _ in current_target.neighbors]:
                self.move_queue.append(target_node)
        else:
            # Not animating, start fresh queue
            self.move_queue = []
            if target_node in [n for n, _ in self.node.neighbors]:
                self.move_queue.append(target_node)
    
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
        # Can always click adjacent nodes (for queue system)
        for neighbor, _ in self.node.neighbors:
            if neighbor == target_node:
                return True
        
        # Also check if clicking on queued nodes
        if self.move_queue and target_node in self.move_queue:
            return True
            
        return False
    
    def start_move(self, target_node: Node, algorithm: str, current_time: int):
        """Start moving to a new node.
        
        Args:
            target_node: Destination node
            algorithm: Current algorithm (affects animation speed)
            current_time: Current time in milliseconds
        """
        self.animating = True
        self.animation_start_time = current_time
        self.animation_from = self.visual_pos
        self.animation_to = target_node.pos
        
        # Set move_to for update() to know target node
        self.move_to = target_node
        
        # Calculate animation duration based on algorithm
        if algorithm in ['BFS', 'DFS']:
            self.animation_duration = int(ANIMATION_BASE_SPEED * 1000)  # 0.5 seconds
        elif algorithm == 'UCS':
            weight = self.node.get_weight_to(target_node)
            duration_seconds = 0.2 + (weight * 0.1)
            self.animation_duration = int(duration_seconds * 1000)
        elif 'Greedy' in algorithm:
            duration_seconds = 0.3 + (target_node.h_cost * 0.02)
            self.animation_duration = int(min(duration_seconds, 1.5) * 1000)
        elif 'A*' in algorithm:
            duration_seconds = 0.2 + (target_node.f_cost * 0.015)
            self.animation_duration = int(min(duration_seconds, 1.5) * 1000)
        else:
            self.animation_duration = 400  # Default 400ms
    
    def update(self, current_time: int, dt: float = 0, algorithm: str = 'BFS') -> bool:
        """Update player movement and animation.
        
        Args:
            current_time: Current time in milliseconds
            dt: Delta time in seconds (unused, kept for compatibility)
            algorithm: Algorithm name (for animation speed)
            
        Returns:
            True if move completed this frame
        """
        if self.animating:
            # Update animation
            elapsed = current_time - self.animation_start_time
            progress = min(1.0, elapsed / self.animation_duration)
            eased = self.ease_in_out_cubic(progress)
            
            # Interpolate position
            self.visual_pos = (
                self.animation_from[0] + (self.animation_to[0] - self.animation_from[0]) * eased,
                self.animation_from[1] + (self.animation_to[1] - self.animation_from[1]) * eased
            )
            
            if progress >= 1.0:
                # Move complete
                self.animating = False
                self.visual_pos = self.move_to.pos
                self.node = self.move_to
                self.nodes_visited += 1
                
                # Remove completed move from queue
                if self.move_queue and self.move_queue[0] == self.move_to:
                    self.move_queue.pop(0)
                
                self.move_to = None
                
                # Start next move in queue
                if self.move_queue:
                    self.start_move(self.move_queue[0], algorithm, current_time)
                
                return True
        
        elif self.move_queue:
            # Not animating but have queued moves - start next one
            self.start_move(self.move_queue[0], algorithm, current_time)
        
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
        
        # Animation properties
        self.visual_pos = start_node.pos  # Rendered position
        self.animating = False
        self.animation_start_time = 0
        self.animation_duration = 400  # milliseconds
        self.animation_from = start_node.pos
        self.animation_to = start_node.pos
        
        # Track ALL visited nodes across all path calculations
        # This enforces algorithmic constraints:
        # - For BFS/DFS/UCS: Track visited leaf nodes
        # - For Greedy/A*: Track ALL nodes (no backtracking)
        self.visited_nodes: set[Node] = set()
        
        # Track visited leaf nodes for BFS/DFS/UCS
        # Once a leaf is visited, enemy cannot go there again
        self.visited_leaves: set[Node] = set()
    
    def ease_in_out_cubic(self, t: float) -> float:
        """Smooth easing function for animations.
        
        Args:
            t: Progress from 0.0 to 1.0
            
        Returns:
            Eased progress value
        """
        return t * t * (3 - 2 * t)
    
    def start_animation(self, target_node: Node, current_time: int):
        """Start animation to target node.
        
        Args:
            target_node: Node to animate to
            current_time: Current time in milliseconds
        """
        self.animating = True
        self.animation_start_time = current_time
        self.animation_from = self.visual_pos
        self.animation_to = target_node.pos
        self.node = target_node
    
    def recalculate_path(self, target_node: Node):
        """Recalculate path to target.
        
        Args:
            target_node: New target position
        """
        if target_node == self.target_node and self.path:
            return  # Target hasn't changed
        
        self.target_node = target_node
        
        # Find path using algorithm with persistent visited node tracking
        # BFS/DFS/UCS: Pass both visited_leaves and visited_nodes
        # Greedy/A*: Pass visited_nodes for strict no-backtracking enforcement
        if self.algorithm in ['BFS', 'DFS', 'UCS']:
            self.path, self.stats = find_path(self.algorithm, self.graph, self.node, 
                                             target_node, self.visited_leaves, self.visited_nodes)
        else:
            # Greedy and A* variants use visited_nodes (no backtracking)
            self.path, self.stats = find_path(self.algorithm, self.graph, self.node, 
                                             target_node, None, self.visited_nodes)
        
        self.path_index = 0
    
    def update(self, current_time: int, player_node: Node, dt: float = 0) -> bool:
        """Update enemy AI and animation.
        
        Args:
            current_time: Current time in milliseconds
            player_node: Player's current position
            dt: Delta time in seconds (unused, kept for compatibility)
            
        Returns:
            True if enemy moved this frame
        """
        # Update animation if animating
        if self.animating:
            elapsed = current_time - self.animation_start_time
            progress = min(1.0, elapsed / self.animation_duration)
            eased = self.ease_in_out_cubic(progress)
            
            # Interpolate position
            self.visual_pos = (
                self.animation_from[0] + (self.animation_to[0] - self.animation_from[0]) * eased,
                self.animation_from[1] + (self.animation_to[1] - self.animation_from[1]) * eased
            )
            
            if progress >= 1.0:
                self.animating = False
                self.visual_pos = self.node.pos
        
        # Recalculate if needed
        if player_node != self.target_node:
            self.recalculate_path(player_node)
        
        # Check if we can start a new move (not animating and enough time passed)
        if self.animating or (current_time - self.last_move_time < self.move_delay):
            return False
        
        # Move along path
        if self.path and self.path_index < len(self.path) - 1:
            self.path_index += 1
            next_node = self.path[self.path_index]
            self.start_animation(next_node, current_time)
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
        
        # Random spawn positions using timestamp seed
        import random
        import time as time_module_local
        random.seed(int(time_module_local.time() * 1000))
        
        nodes = list(self.graph.nodes)
        random.shuffle(nodes)
        
        # Find valid spawns with minimum 400px distance
        player_start = None
        enemy_start = None
        
        for player_node in nodes:
            for enemy_node in nodes:
                if player_node != enemy_node:
                    distance = player_node.distance_to(enemy_node)
                    if distance >= 400:
                        player_start = player_node
                        enemy_start = enemy_node
                        break
            if player_start is not None:
                break
        
        # Fallback if no 400px distance pair found (use furthest apart)
        if player_start is None:
            max_distance = 0
            for i, p_node in enumerate(nodes):
                for j, e_node in enumerate(nodes):
                    if i != j:
                        dist = p_node.distance_to(e_node)
                        if dist > max_distance:
                            max_distance = dist
                            player_start = p_node
                            enemy_start = e_node
        
        # Initialize entities
        self.player = PlayerEntity(player_start)
        self.enemy = EnemyAI(enemy_start, algorithm, self.graph)
        self.combat = CombatSystem()
        
        # Graph already has random costs assigned at creation
        # NO initialization or updates needed for tooltips
        
        # Track player's last node to detect movement
        self.player_last_node = player_start
        
        # Calculate initial path
        self.enemy.recalculate_path(self.player.node)
        
        # Game state
        self.paused = False
        self.start_time = time_module.time()
        self.game_time = 0
        self.is_victory = False
        self.is_defeat = False
    
    def handle_click(self, pos: tuple[int, int], current_time: int) -> bool:
        """Handle player click for movement with queue system.
        
        Args:
            pos: Mouse click position
            current_time: Current time in milliseconds
            
        Returns:
            True if click was handled
        """
        if self.paused:
            return False
        
        # Find clicked node
        clicked_node = self.graph.get_node_at_pos(pos)
        if not clicked_node:
            return False
        
        # Check if clicking same node - cancel queue
        if clicked_node == self.player.node:
            self.player.move_queue = []
            return True
        
        # Check if it's a valid adjacent move
        if self.player.can_move_to(clicked_node):
            # Override queue with new move
            self.player.override_queue(clicked_node)
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
        
        # Update player with algorithm parameter for queue system
        if self.player.update(current_time, delta_time, self.algorithm):
            # Player finished moving, enemy recalculates
            self.enemy.recalculate_path(self.player.node)
            
            # Static costs remain unchanged - no need to update
            self.player_last_node = self.player.node
        
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

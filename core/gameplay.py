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
    """Enemy AI with pure greedy movement (no pathfinding/lookahead)."""
    
    def __init__(self, start_node: Node, algorithm: str, graph):
        """Initialize enemy AI.
        
        Args:
            start_node: Starting node
            algorithm: Algorithm to use for movement decisions
            graph: Game graph
        """
        self.node = start_node
        self.algorithm = algorithm
        self.graph = graph
        self.last_move_time = 0
        self.move_delay = ENEMY_SPEEDS.get(algorithm, 500)
        self.stats = Stats()
        
        # Animation properties
        self.visual_pos = start_node.pos  # Rendered position
        self.animating = False
        self.animation_start_time = 0
        self.animation_duration = 400  # milliseconds
        self.animation_from = start_node.pos
        self.animation_to = start_node.pos
        
        # Track visited nodes (for no-backtracking enforcement)
        self.visited_nodes: set[Node] = set()
        
        # Track visited leaves (for BFS/DFS/UCS - cannot revisit)
        self.visited_leaves: set[Node] = set()
        
        # Track nodes that have been backtracked from (to prevent re-backtracking loops)
        self.backtracked_from: set[Node] = set()
        
        # CRITICAL FIX: Mark starting node as visited immediately for BFS/DFS/UCS
        if algorithm in ['BFS', 'DFS', 'UCS']:
            start_node.visited = True
        
        # Track if enemy is stuck (no valid moves)
        self.stuck = False
        
        # CRITICAL FIX: Track reason why enemy got stuck
        # Possible values: "local_min", "local_max", "dead_end", "graph_explored"
        self.stuck_reason = ""
        
        # Track if enemy has caught the player (at same node)
        self.caught_player = False
        
        # Legacy compatibility (for old code that checks these)
        self.path = []
        self.path_index = 0
        self.target_node = None
    
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
    
    def get_next_move(self, player_node: Node) -> Node | None:
        """Get next move based PURELY on algorithm rules - NO pathfinding/lookahead.
        
        BFS/DFS/UCS: Can backtrack (revisit nodes) but CANNOT revisit visited leaves
        Greedy/A*: NO backtracking at all (cannot revisit any visited node)
        
        Player Tracking (Greedy/A* when caught):
        - Local Min: Follow player only if they move to minimum value neighbor
        - Local Max: Follow player only if they move to maximum value neighbor
        - Otherwise: Abandon player, pick correct min/max neighbor instead
        
        Args:
            player_node: Player's current position
            
        Returns:
            Next node to move to, or None if stuck/completed
        """
        if self.stuck:
            return None  # Enemy is stuck, player wins!
        
        # Check if enemy caught the player
        if self.node == player_node:
            self.caught_player = True
            # Stop moving when at goal - only resume if player moves
            return None
        
        # Special logic for Greedy/A* when player was caught and moved
        if self.caught_player and self.algorithm in ['Greedy (Local Min)', 'Greedy (Local Max)',
                                                      'A* (Local Min)', 'A* (Local Max)']:
            # Player moved away - decide whether to follow or abandon
            # Get all valid neighbors (unvisited)
            valid_neighbors = [n for n, _ in self.node.neighbors 
                             if n not in self.visited_nodes]
            
            if not valid_neighbors:
                self.stuck = True
                return None
            
            # Determine the "correct" neighbor based on algorithm
            if self.algorithm == "Greedy (Local Min)":
                correct_neighbor = min(valid_neighbors, key=lambda n: n.heuristic)
            elif self.algorithm == "Greedy (Local Max)":
                correct_neighbor = max(valid_neighbors, key=lambda n: n.heuristic)
            elif self.algorithm == "A* (Local Min)":
                correct_neighbor = min(valid_neighbors, 
                                     key=lambda n: n.heuristic + n.path_cost)
            elif self.algorithm == "A* (Local Max)":
                correct_neighbor = max(valid_neighbors, 
                                     key=lambda n: n.heuristic + n.path_cost)
            else:
                correct_neighbor = valid_neighbors[0]
            
            # Check if player is at the correct neighbor
            if player_node == correct_neighbor:
                # Follow player (they moved to the min/max neighbor)
                self.caught_player = False  # Will catch again next update
                return player_node
            else:
                # Abandon player, choose correct neighbor instead
                self.caught_player = False
                return correct_neighbor
        
        # Get valid neighbors based on algorithm type
        if self.algorithm in ['BFS', 'DFS', 'UCS']:
            # BFS/DFS/UCS: Prioritize unvisited nodes, but allow backtracking when stuck
            # First, try to find truly unvisited neighbors (not visited AND not in visited_leaves)
            unvisited_neighbors = [n for n, _ in self.node.neighbors 
                                 if not n.visited and not (n.is_leaf() and n in self.visited_leaves)]
            
            if unvisited_neighbors:
                # We have unvisited neighbors - use them (prevents infinite loop)
                valid_neighbors = unvisited_neighbors
            else:
                # All neighbors are visited or are visited leaves
                # Mark current node as backtracked from (to prevent returning here in loops)
                self.backtracked_from.add(self.node)
                
                # Check if there are ANY unvisited nodes left in the entire graph
                any_unvisited = any(not node.visited for node in self.graph.nodes)
                
                if not any_unvisited:
                    # Entire graph has been explored - no unvisited nodes left anywhere
                    # Player wins because enemy explored everything but couldn't find player
                    self.stuck = True
                    self.stuck_reason = "graph_explored"
                    return None
                
                # There are still unvisited nodes somewhere, allow backtracking to reach them
                # Allow backtracking to visited non-leaf nodes that haven't been backtracked from
                valid_neighbors = [n for n, _ in self.node.neighbors 
                                 if not (n.is_leaf() and n in self.visited_leaves)
                                 and n not in self.backtracked_from]
            
            # If no valid neighbors, check if entire graph has been explored
            if not valid_neighbors:
                # For BFS/DFS/UCS, being stuck means completing traversal
                # Player wins only if they were never found
                self.stuck = True
                self.stuck_reason = "graph_explored"
                return None
        else:
            # Greedy/A*: NO backtracking - cannot revisit ANY visited node
            valid_neighbors = [n for n, _ in self.node.neighbors 
                             if n not in self.visited_nodes]
            
            # If no valid neighbors, enemy is STUCK (plateau/ridge/dead-end)
            if not valid_neighbors:
                self.stuck = True
                self.stuck_reason = "dead_end"
                return None  # Player wins!
        
        # PLATEAU/RIDGE DETECTION for Greedy/A*: Check if stuck at local min/max
        # before selecting next move
        if self.algorithm == "Greedy (Local Min)":
            # Check if at local minimum: all neighbors have GREATER heuristic values
            min_neighbor_h = min(n.heuristic for n in valid_neighbors)
            if min_neighbor_h > self.node.heuristic:
                # All neighbors have greater values - stuck at local minimum!
                self.stuck = True
                self.stuck_reason = "local_min"
                return None
            # Pick neighbor with LOWEST heuristic (greedy, no planning)
            next_node = min(valid_neighbors, key=lambda n: n.heuristic)
        
        elif self.algorithm == "Greedy (Local Max)":
            # Check if at local maximum: all neighbors have SMALLER heuristic values
            max_neighbor_h = max(n.heuristic for n in valid_neighbors)
            if max_neighbor_h < self.node.heuristic:
                # All neighbors have smaller values - stuck at local maximum!
                self.stuck = True
                self.stuck_reason = "local_max"
                return None
            # Pick neighbor with HIGHEST heuristic (greedy, no planning)
            next_node = max(valid_neighbors, key=lambda n: n.heuristic)
        
        elif self.algorithm == "UCS":
            # Pick neighbor with LOWEST path cost (greedy, no planning)
            next_node = min(valid_neighbors, key=lambda n: n.path_cost)
        
        elif self.algorithm == "A* (Local Min)":
            # Check if at local minimum: all neighbors have GREATER f-cost values
            min_neighbor_f = min(n.heuristic + n.path_cost for n in valid_neighbors)
            current_f = self.node.heuristic + self.node.path_cost
            if min_neighbor_f > current_f:
                # All neighbors have greater f-costs - stuck at local minimum!
                self.stuck = True
                self.stuck_reason = "local_min"
                return None
            # Pick neighbor with LOWEST f-cost (h + g)
            next_node = min(valid_neighbors, 
                           key=lambda n: n.heuristic + n.path_cost)
        
        elif self.algorithm == "A* (Local Max)":
            # Check if at local maximum: all neighbors have SMALLER f-cost values
            max_neighbor_f = max(n.heuristic + n.path_cost for n in valid_neighbors)
            current_f = self.node.heuristic + self.node.path_cost
            if max_neighbor_f < current_f:
                # All neighbors have smaller f-costs - stuck at local maximum!
                self.stuck = True
                self.stuck_reason = "local_max"
                return None
            # Pick neighbor with HIGHEST f-cost (h + g)
            next_node = max(valid_neighbors, 
                           key=lambda n: n.heuristic + n.path_cost)
        
        elif self.algorithm == "BFS":
            # BFS: Pick first unvisited neighbor (queue-like behavior)
            # If all neighbors visited, backtrack to first available
            next_node = valid_neighbors[0]
        
        elif self.algorithm == "DFS":
            # DFS: Pick last unvisited neighbor (stack-like behavior)
            # If all neighbors visited, backtrack to last available
            next_node = valid_neighbors[-1]
        
        else:
            # Default: pick first neighbor
            next_node = valid_neighbors[0]
        
        return next_node
    
    def recalculate_path(self, target_node: Node):
        """Legacy compatibility method - no-op for pure greedy movement.
        
        In the new implementation, enemy doesn't calculate paths ahead of time.
        This method exists for backwards compatibility with tests.
        
        Args:
            target_node: Target node (ignored)
        """
        # No-op: pure greedy movement doesn't pre-calculate paths
        pass
    
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
                
                # Mark current node as visited AFTER animation completes
                # CRITICAL FIX: Update node.visited boolean immediately for BFS/DFS/UCS
                if self.algorithm in ['BFS', 'DFS', 'UCS']:
                    # Set the visited boolean on the node itself (for tooltip display)
                    self.node.visited = True
                    # Track visited leaves (cannot revisit these)
                    if self.node.is_leaf():
                        self.visited_leaves.add(self.node)
                
                # For Greedy/A*: mark all visited nodes
                if self.algorithm in ['Greedy (Local Min)', 'Greedy (Local Max)', 
                                     'A* (Local Min)', 'A* (Local Max)']:
                    self.visited_nodes.add(self.node)
        
        # If caught player and player hasn't moved, stay put
        if self.caught_player and self.node == player_node:
            return False
        
        # If player moved away from caught position, resume pursuit
        if self.caught_player and self.node != player_node:
            self.caught_player = False
        
        # Check if we can start a new move (not animating and enough time passed)
        if self.animating or (current_time - self.last_move_time < self.move_delay):
            return False
        
        # Get next move using pure greedy logic (no pathfinding)
        next_node = self.get_next_move(player_node)
        
        if next_node is None:
            # Enemy is stuck or caught player - no more moves
            return False
        
        # Start animation to next node
        self.start_animation(next_node, current_time)
        self.last_move_time = current_time
        
        # Update legacy path for compatibility (for display purposes)
        self.path = [self.node]
        
        return True


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
        
        # Assign balanced costs based on spawn positions and algorithm
        # This creates ~50% chance of enemy-favorable patterns
        self.graph.assign_balanced_costs(enemy_start, player_start, algorithm)
        
        # Initialize h_cost for all nodes (for tooltip display)
        # Set h_cost based on distance to player's starting position
        self.graph.update_heuristics_to_target(player_start)
        
        # Track player's last node to detect movement
        self.player_last_node = player_start
        
        # Game state
        self.paused = False
        self.start_time = time_module.time()
        self.game_time = 0
        self.is_victory = False
        self.is_defeat = False
        self.victory_reason = ""  # Track reason for victory
    
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
            # Player finished moving
            # Static costs remain unchanged - no need to update
            self.player_last_node = self.player.node
        
        # Update enemy
        self.enemy.update(current_time, self.player.node)
        
        # Check if enemy is stuck (victory condition)
        if self.enemy.stuck and not self.is_victory:
            self.is_victory = True
            # CRITICAL FIX: Use enemy's stuck_reason for accurate victory message
            self.victory_reason = self.enemy.stuck_reason if self.enemy.stuck_reason else "enemy_stuck"
        
        # Check combat
        self.combat.check_contact(self.player.node, self.enemy.node, current_time)
        
        # Check game over conditions
        is_over, reason = self.combat.is_game_over()
        if is_over:
            if reason == 'victory':
                self.is_victory = True
                if not self.victory_reason:
                    self.victory_reason = "combat"
            else:
                self.is_defeat = True
    
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

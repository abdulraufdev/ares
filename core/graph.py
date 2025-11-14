"""Graph generation for Algorithm Arena."""
import random
import math
from core.node import Node


class Graph:
    """Manages the game's node network."""
    
    def __init__(self, width: int, height: int, num_nodes: int = 28, seed: int = 42):
        """Generate a beautiful interconnected graph.
        
        Args:
            width: Display area width
            height: Display area height
            num_nodes: Number of nodes to generate (25-30 recommended)
            seed: Random seed for reproducible layouts
        """
        self.width = width
        self.height = height
        self.nodes: list[Node] = []
        
        random.seed(seed)
        self._generate_nodes(num_nodes)
        self._connect_nodes()
        
        # Assign RANDOM STATIC values to all nodes
        self._assign_random_costs()
    
    def _generate_nodes(self, num_nodes: int):
        """Generate nodes with organic layout."""
        # Create margin to keep nodes away from edges
        margin = 80
        usable_width = self.width - 2 * margin
        usable_height = self.height - 2 * margin
        
        # Try to place nodes with minimum distance between them
        min_distance = 100
        attempts = 0
        max_attempts = num_nodes * 50
        
        while len(self.nodes) < num_nodes and attempts < max_attempts:
            x = margin + random.random() * usable_width
            y = margin + random.random() * usable_height
            
            # Check if position is valid (not too close to existing nodes)
            valid = True
            for node in self.nodes:
                dist = math.sqrt((x - node.pos[0])**2 + (y - node.pos[1])**2)
                if dist < min_distance:
                    valid = False
                    break
            
            if valid:
                label = f"N{len(self.nodes) + 1}"
                self.nodes.append(Node(label, (x, y)))
            
            attempts += 1
        
        # If we couldn't place all nodes, reduce min_distance and try again
        while len(self.nodes) < num_nodes:
            min_distance *= 0.9
            x = margin + random.random() * usable_width
            y = margin + random.random() * usable_height
            
            valid = True
            for node in self.nodes:
                dist = math.sqrt((x - node.pos[0])**2 + (y - node.pos[1])**2)
                if dist < min_distance:
                    valid = False
                    break
            
            if valid:
                label = f"N{len(self.nodes) + 1}"
                self.nodes.append(Node(label, (x, y)))
    
    def _connect_nodes(self):
        """Create edges between nodes for fully connected graph with strategic positions.
        
        Enforces:
        - Minimum neighbors per node: 1 (dead-ends for trapping enemy)
        - Maximum neighbors per node: 3
        - 8-12 leaf nodes (nodes with exactly 1 neighbor) when possible
        - Most nodes should have 2-3 neighbors
        """
        # Designate leaf nodes based on graph size
        # For full game (28 nodes): 8-12 leaf nodes
        # For smaller graphs: scale proportionally (min 3, max half the nodes)
        if len(self.nodes) >= 25:
            num_dead_ends = random.randint(8, 12)
        else:
            # Scale proportionally but ensure reasonable bounds
            min_leaves = max(3, len(self.nodes) // 5)
            max_leaves = min(len(self.nodes) // 2, len(self.nodes) - 2)
            num_dead_ends = random.randint(min_leaves, max_leaves)
        
        dead_end_indices = random.sample(range(len(self.nodes)), num_dead_ends)
        
        for idx, node in enumerate(self.nodes):
            # Find closest nodes that aren't already neighbors
            distances = []
            for other_idx, other in enumerate(self.nodes):
                if other == node:
                    continue
                if any(n == other for n, _ in node.neighbors):
                    continue
                
                # Skip if the other node already has 3 neighbors (maximum)
                if len(other.neighbors) >= 3:
                    continue
                
                # Skip if the other node is a dead-end and already has 1 neighbor
                if other_idx in dead_end_indices and len(other.neighbors) >= 1:
                    continue
                    
                dist = node.distance_to(other)
                distances.append((dist, other, other_idx))
            
            # Sort by distance and connect to closest
            distances.sort(key=lambda x: x[0])
            
            # Determine target neighbors based on node type
            if idx in dead_end_indices:
                # Dead-end nodes: only 1 neighbor
                target_neighbors = 1
            else:
                # Regular nodes: 2-3 neighbors
                target_neighbors = random.randint(2, 3)
            
            # Connect to ensure target neighbors (but respect maximum of 3)
            current_neighbors = len(node.neighbors)
            # Don't exceed 3 neighbors (or 1 for dead-ends)
            max_allowed = min(3, target_neighbors)
            to_add = max(0, max_allowed - current_neighbors)
            
            for i in range(min(to_add, len(distances))):
                dist, neighbor, neighbor_idx = distances[i]
                
                # Skip if this would give the neighbor more than 3 connections
                if len(neighbor.neighbors) >= 3:
                    continue
                
                # Skip if this would give a dead-end neighbor more than 1 connection
                if neighbor_idx in dead_end_indices and len(neighbor.neighbors) >= 1:
                    continue
                
                # Strategic weight assignment
                if idx in dead_end_indices or neighbor_idx in dead_end_indices:
                    # High-cost paths to/from dead-ends (for UCS/A* strategy)
                    weight = random.randint(7, 10)
                else:
                    # Regular weights - mix of low and high
                    weight = random.randint(1, 10)
                
                node.add_neighbor(neighbor, weight)
        
        # Ensure graph is fully connected (no isolated components)
        self._ensure_connected()
        
        # Pre-calculate all heuristics for A* and Greedy
        self._precalculate_heuristics()
        
        # Count actual leaf nodes for validation
        actual_leaf_count = sum(1 for node in self.nodes if len(node.neighbors) == 1)
        self.leaf_node_count = actual_leaf_count
        
        # Store dead-end info for debugging/verification
        self.dead_end_count = num_dead_ends
    
    def _ensure_connected(self):
        """Ensure all nodes are reachable from any node."""
        if not self.nodes:
            return
        
        # BFS to find connected component
        visited = set()
        queue = [self.nodes[0]]
        visited.add(self.nodes[0])
        
        while queue:
            current = queue.pop(0)
            for neighbor, _ in current.neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        # If not all nodes are visited, connect isolated nodes
        unvisited = [n for n in self.nodes if n not in visited]
        
        for node in unvisited:
            # Connect to closest visited node
            closest = None
            min_dist = float('inf')
            
            for visited_node in visited:
                dist = node.distance_to(visited_node)
                if dist < min_dist:
                    min_dist = dist
                    closest = visited_node
            
            if closest:
                weight = random.randint(1, 10)
                node.add_neighbor(closest, weight)
                visited.add(node)
    
    def _precalculate_heuristics(self):
        """Pre-calculate heuristics between all node pairs for A* and Greedy.
        
        This prevents "Calculating heuristic..." messages during gameplay.
        """
        for node in self.nodes:
            for other_node in self.nodes:
                if node != other_node:
                    # Store Euclidean distance as heuristic
                    node.heuristics[other_node] = node.distance_to(other_node)
    
    def _assign_random_costs(self):
        """Assign random heuristic and path cost to each node (ONCE, NEVER changes).
        
        These static values are used for tooltip display and remain constant
        throughout the game session. They are NOT used for pathfinding calculations.
        
        Note: These are initial random values. They will be reassigned in GameSession
        to create balanced gameplay based on spawn positions.
        """
        for node in self.nodes:
            # Random heuristic between 10 and 300
            node.heuristic = random.uniform(10.0, 300.0)
            
            # Random path cost between 10 and 300
            node.path_cost = random.uniform(10.0, 300.0)
        
        # Round to 1 decimal place for cleaner display
        for node in self.nodes:
            node.heuristic = round(node.heuristic, 1)
            node.path_cost = round(node.path_cost, 1)
    
    def assign_balanced_costs(self, enemy_node: Node, player_node: Node, 
                             algorithm: str, favor_enemy_chance: float = 0.5):
        """Assign costs that create balanced gameplay based on spawn positions.
        
        CRITICAL FIX: For Greedy/A* algorithms, ALWAYS create a valid initial path 
        from enemy to player with NO plateau conditions at game start.
        This ensures player cannot win by standing still.
        
        For Local Min algorithms: create descending path enemy→player
        For Local Max algorithms: create ascending path enemy→player  
        For UCS: create low-cost path enemy→player
        
        Args:
            enemy_node: Enemy starting position
            player_node: Player starting position
            algorithm: Algorithm name
            favor_enemy_chance: Probability of creating enemy-favorable pattern (default 0.5)
        """
        import random as rand_module
        
        # CRITICAL: For Greedy/A*, ALWAYS create valid initial path (not random)
        # Find shortest path from enemy to player using BFS
        visited = set()
        parent_map = {enemy_node: None}
        queue = [enemy_node]
        visited.add(enemy_node)
        
        while queue:
            current = queue.pop(0)
            if current == player_node:
                break
            for neighbor, _ in current.neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent_map[neighbor] = current
                    queue.append(neighbor)
        
        # Reconstruct path from enemy to player
        path_to_player = []
        if player_node in parent_map:
            node = player_node
            while node is not None:
                path_to_player.append(node)
                node = parent_map.get(node)
            path_to_player.reverse()
        
        # Assign values based on algorithm type
        if 'Local Min' in algorithm:
            # For Local Min: create descending path (high→low toward player)
            # CRITICAL: Ensure STRICT descending values with NO plateau
            if path_to_player and len(path_to_player) > 1:
                # Assign decreasing values along path with guaranteed gaps
                for i, node in enumerate(path_to_player):
                    # Strict descending: each node is at least 30 units lower than previous
                    # Start at 300, each step decreases by 30-50 units
                    gap = rand_module.uniform(30.0, 50.0)
                    node.heuristic = 300.0 - (i * gap)
                
                # Other nodes get random values but ensure they don't break the path
                for node in self.nodes:
                    if node not in path_to_player:
                        node.heuristic = rand_module.uniform(50.0, 350.0)
            else:
                # Fallback to random
                for node in self.nodes:
                    node.heuristic = rand_module.uniform(10.0, 300.0)
        
        elif 'Local Max' in algorithm:
            # For Local Max: create ascending path (low→high toward player)
            # CRITICAL: Ensure STRICT ascending values with NO plateau
            if path_to_player and len(path_to_player) > 1:
                # Assign increasing values along path with guaranteed gaps
                for i, node in enumerate(path_to_player):
                    # Strict ascending: each node is at least 30 units higher than previous
                    # Start at 50, each step increases by 30-50 units
                    gap = rand_module.uniform(30.0, 50.0)
                    node.heuristic = 50.0 + (i * gap)
                
                # Other nodes get random values but ensure they don't break the path
                for node in self.nodes:
                    if node not in path_to_player:
                        node.heuristic = rand_module.uniform(10.0, 300.0)
            else:
                # Fallback to random
                for node in self.nodes:
                    node.heuristic = rand_module.uniform(10.0, 300.0)
        
        elif algorithm == 'UCS':
            # For UCS: create low path_cost along path
            if path_to_player:
                for node in path_to_player:
                    node.path_cost = rand_module.uniform(10.0, 80.0)
                # Other nodes get higher costs
                for node in self.nodes:
                    if node not in path_to_player:
                        node.path_cost = rand_module.uniform(100.0, 300.0)
            else:
                # Fallback to random
                for node in self.nodes:
                    node.path_cost = rand_module.uniform(10.0, 300.0)
        
        # For A* algorithms, also ensure valid gradient in path_cost
        if 'A*' in algorithm:
            if 'Local Min' in algorithm and path_to_player and len(path_to_player) > 1:
                # A* Local Min: decreasing f-cost along path
                for i, node in enumerate(path_to_player):
                    # Assign path costs that contribute to decreasing f-cost
                    gap = rand_module.uniform(20.0, 30.0)
                    node.path_cost = 200.0 - (i * gap)
            elif 'Local Max' in algorithm and path_to_player and len(path_to_player) > 1:
                # A* Local Max: increasing f-cost along path
                for i, node in enumerate(path_to_player):
                    # Assign path costs that contribute to increasing f-cost
                    gap = rand_module.uniform(20.0, 30.0)
                    node.path_cost = 50.0 + (i * gap)
        
        # For all algorithms, assign path_cost to nodes not in path
        for node in self.nodes:
            if not hasattr(node, 'path_cost') or node.path_cost == 0.0:
                node.path_cost = rand_module.uniform(10.0, 300.0)
        
        # Round to 1 decimal place for cleaner display
        for node in self.nodes:
            node.heuristic = round(node.heuristic, 1)
            node.path_cost = round(node.path_cost, 1)
    
    def update_heuristics_to_target(self, target_node: Node):
        """Update all nodes' h_cost to reflect distance to target.
        
        This is called when the player moves to update tooltip displays.
        
        Args:
            target_node: The target node (usually player's current position)
        """
        for node in self.nodes:
            if node == target_node:
                node.h_cost = 0.0
            else:
                node.h_cost = node.distance_to(target_node)
    
    def get_node_by_label(self, label: str) -> Node | None:
        """Find node by its label."""
        for node in self.nodes:
            if node.label == label:
                return node
        return None
    
    def get_node_at_pos(self, pos: tuple[float, float], radius: float = 30) -> Node | None:
        """Find node at given position (within radius)."""
        x, y = pos
        for node in self.nodes:
            dx = node.pos[0] - x
            dy = node.pos[1] - y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= radius:
                return node
        return None
    
    def reset_all_nodes(self):
        """Reset pathfinding metadata for all nodes."""
        for node in self.nodes:
            node.reset_pathfinding()
    
    def get_random_node(self) -> Node:
        """Get a random node from the graph."""
        return random.choice(self.nodes)

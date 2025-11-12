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
        """Create edges between nodes for fully connected graph with strategic positions."""
        # Create strategic variety in node connectivity
        # Some nodes will be dead-ends (1-2 neighbors) - safe zones for BFS/DFS
        # Some will have many neighbors (4-6) - junction points
        
        # Designate 3-5 nodes as "safe zone" candidates (dead-ends)
        num_safe_zones = random.randint(3, 5)
        safe_zone_indices = random.sample(range(len(self.nodes)), num_safe_zones)
        
        for idx, node in enumerate(self.nodes):
            # Find closest nodes that aren't already neighbors
            distances = []
            for other in self.nodes:
                if other == node:
                    continue
                if any(n == other for n, _ in node.neighbors):
                    continue
                dist = node.distance_to(other)
                distances.append((dist, other))
            
            # Sort by distance and connect to closest
            distances.sort(key=lambda x: x[0])
            
            # Determine target neighbors based on node type
            if idx in safe_zone_indices:
                # Safe zone nodes: only 1-2 neighbors (dead-ends)
                target_neighbors = random.randint(1, 2)
            else:
                # Regular nodes: 3-6 neighbors
                target_neighbors = random.randint(3, 6)
            
            # Connect to ensure target neighbors (but at least 1)
            current_neighbors = len(node.neighbors)
            to_add = max(1, target_neighbors - current_neighbors)
            
            for i in range(min(to_add, len(distances))):
                dist, neighbor = distances[i]
                
                # Strategic weight assignment for safe zones
                if idx in safe_zone_indices:
                    # High-cost paths to safe zones (for UCS/A* strategy)
                    weight = random.randint(7, 10)
                else:
                    # Regular weights - mix of low and high
                    weight = random.randint(1, 10)
                
                node.add_neighbor(neighbor, weight)
        
        # Ensure graph is fully connected (no isolated components)
        self._ensure_connected()
        
        # Store safe zone info for debugging/verification
        self.safe_zone_count = num_safe_zones
    
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

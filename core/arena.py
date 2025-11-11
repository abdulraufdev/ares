"""Arena representation with node-based graph visualization."""
import random
import math
from typing import Iterator, Optional

class Arena:
    """Represents the game arena as a graph with nodes and edges."""
    
    def __init__(self, node_count: int = 25, obstacle_ratio: float = 0.15, 
                 seed: int = 42, window_width: int = 1280, window_height: int = 800):
        """Initialize arena with nodes positioned in space."""
        random.seed(seed)
        
        self.node_count = node_count
        self.window_width = window_width
        self.window_height = window_height
        
        # Generate node positions
        self.nodes: dict[int, tuple[float, float]] = {}
        self.blocked: set[int] = set()
        self.edges: dict[int, list[tuple[int, float]]] = {}  # node_id -> [(neighbor_id, weight), ...]
        self.cost: dict[int, float] = {}
        
        self._generate_nodes()
        self._generate_edges()
        self._mark_obstacles(obstacle_ratio)
    
    def _generate_nodes(self) -> None:
        """Generate node positions in a visually pleasing layout."""
        # Create a margin around the edges
        margin_x = 100
        margin_y = 100
        usable_width = self.window_width - 2 * margin_x
        usable_height = self.window_height - 2 * margin_y
        
        # Use a grid-based layout with some randomness for organic feel
        cols = int(math.sqrt(self.node_count * usable_width / usable_height))
        rows = (self.node_count + cols - 1) // cols
        
        cell_width = usable_width / cols
        cell_height = usable_height / rows
        
        node_id = 0
        for row in range(rows):
            for col in range(cols):
                if node_id >= self.node_count:
                    break
                
                # Base position in grid
                base_x = margin_x + col * cell_width + cell_width / 2
                base_y = margin_y + row * cell_height + cell_height / 2
                
                # Add some randomness for organic feel
                offset_x = random.uniform(-cell_width * 0.2, cell_width * 0.2)
                offset_y = random.uniform(-cell_height * 0.2, cell_height * 0.2)
                
                x = base_x + offset_x
                y = base_y + offset_y
                
                self.nodes[node_id] = (x, y)
                self.cost[node_id] = 1.0
                node_id += 1
    
    def _generate_edges(self) -> None:
        """Generate edges between nearby nodes."""
        # Calculate average node spacing
        positions = list(self.nodes.values())
        if len(positions) < 2:
            return
        
        # Find average distance to nearest neighbor
        total_min_dist = 0
        for i, pos1 in enumerate(positions):
            min_dist = float('inf')
            for j, pos2 in enumerate(positions):
                if i != j:
                    dist = self._distance(pos1, pos2)
                    min_dist = min(min_dist, dist)
            total_min_dist += min_dist
        avg_spacing = total_min_dist / len(positions)
        
        # Connect nodes within a threshold distance
        connection_threshold = avg_spacing * 1.8
        
        for node_id, pos1 in self.nodes.items():
            self.edges[node_id] = []
            
            for other_id, pos2 in self.nodes.items():
                if node_id != other_id:
                    dist = self._distance(pos1, pos2)
                    
                    if dist < connection_threshold:
                        # Weight based on distance
                        weight = max(1.0, dist / avg_spacing)
                        self.edges[node_id].append((other_id, weight))
    
    def _mark_obstacles(self, obstacle_ratio: float) -> None:
        """Mark some nodes as blocked (obstacles)."""
        node_ids = list(self.nodes.keys())
        obstacle_count = int(len(node_ids) * obstacle_ratio)
        
        # Don't block corner nodes (they might be spawn points)
        corners = self._get_corner_nodes()
        available_nodes = [nid for nid in node_ids if nid not in corners]
        
        if available_nodes:
            obstacles = random.sample(available_nodes, min(obstacle_count, len(available_nodes)))
            self.blocked = set(obstacles)
    
    def _distance(self, pos1: tuple[float, float], pos2: tuple[float, float]) -> float:
        """Calculate Euclidean distance between two positions."""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def _get_corner_nodes(self) -> list[int]:
        """Get nodes at the corners (extremes)."""
        if not self.nodes:
            return []
        
        # Find nodes at extremes
        min_sum_id = min(self.nodes.keys(), key=lambda nid: sum(self.nodes[nid]))
        max_sum_id = max(self.nodes.keys(), key=lambda nid: sum(self.nodes[nid]))
        
        return [min_sum_id, max_sum_id]
    
    def get_node_position(self, node_id: int) -> tuple[float, float]:
        """Get the screen position of a node."""
        return self.nodes.get(node_id, (0, 0))
    
    def passable(self, node_id: int) -> bool:
        """Check if node is passable (not blocked)."""
        return node_id not in self.blocked
    
    def neighbors(self, node_id: int) -> Iterator[int]:
        """Yield valid neighboring node IDs."""
        if node_id in self.edges:
            for neighbor_id, _ in self.edges[node_id]:
                if self.passable(neighbor_id):
                    yield neighbor_id
    
    def step_cost(self, from_node: int, to_node: int) -> float:
        """Get the cost of moving from one node to another."""
        if from_node in self.edges:
            for neighbor_id, weight in self.edges[from_node]:
                if neighbor_id == to_node:
                    return weight
        return 1.0
    
    def get_opposite_corners(self) -> tuple[int, int]:
        """Get two opposite corner nodes for spawn positions."""
        if len(self.nodes) < 2:
            return (0, 1)
        
        # Find passable nodes at extremes
        passable_nodes = [nid for nid in self.nodes.keys() if self.passable(nid)]
        
        if not passable_nodes:
            return (0, 1)
        
        # Sort by sum of coordinates (approximates diagonal corners)
        passable_nodes.sort(key=lambda nid: sum(self.nodes[nid]))
        
        player_node = passable_nodes[0]  # Top-left-ish
        enemy_node = passable_nodes[-1]  # Bottom-right-ish
        
        return player_node, enemy_node

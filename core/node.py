"""Node class for graph-based navigation."""
from typing import Optional
import math


class Node:
    """Represents a node in the graph network."""
    
    def __init__(self, label: str, pos: tuple[float, float]):
        """Initialize a node with label and position.
        
        Args:
            label: Node identifier (e.g., "N1", "N2")
            pos: (x, y) position in pixel coordinates
        """
        self.label = label
        self.pos = pos
        self.neighbors: list[tuple['Node', float]] = []  # (neighbor_node, edge_weight)
        
        # Pathfinding metadata
        self.visited = False
        self.distance = float('inf')
        self.g_cost = 0.0  # Cost from start (for UCS, A*)
        self.h_cost = 0.0  # Heuristic to goal (for Greedy, A*)
        self.f_cost = 0.0  # g + h (for A*)
        self.parent: Optional['Node'] = None
    
    def add_neighbor(self, neighbor: 'Node', weight: float):
        """Add a bidirectional connection to another node."""
        # Add to this node's neighbors
        if not any(n == neighbor for n, _ in self.neighbors):
            self.neighbors.append((neighbor, weight))
        
        # Add reverse connection
        if not any(n == self for n, _ in neighbor.neighbors):
            neighbor.neighbors.append((self, weight))
    
    def get_weight_to(self, neighbor: 'Node') -> float:
        """Get edge weight to a specific neighbor."""
        for node, weight in self.neighbors:
            if node == neighbor:
                return weight
        return float('inf')
    
    def distance_to(self, other: 'Node') -> float:
        """Calculate Euclidean distance to another node."""
        dx = self.pos[0] - other.pos[0]
        dy = self.pos[1] - other.pos[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def reset_pathfinding(self):
        """Reset pathfinding metadata for new search."""
        self.visited = False
        self.distance = float('inf')
        self.g_cost = 0.0
        self.h_cost = 0.0
        self.f_cost = 0.0
        self.parent = None

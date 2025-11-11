"""Node representation for graph-based pathfinding."""
from typing import Optional


class Node:
    """Represents a single node in the pathfinding graph."""
    
    def __init__(self, x: int, y: int, walkable: bool = True, weight: float = 1.0):
        """
        Initialize a node.
        
        Args:
            x: X coordinate
            y: Y coordinate
            walkable: Whether the node can be traversed
            weight: Movement cost multiplier for this node
        """
        self.x = x
        self.y = y
        self.walkable = walkable
        self.weight = weight
        self.neighbors: list['Node'] = []
        
        # Pathfinding attributes
        self.g = float('inf')  # Cost from start
        self.h = 0.0  # Heuristic to goal
        self.f = float('inf')  # Total cost (g + h)
        self.parent: Optional['Node'] = None
        self.visited = False
        self.in_open_list = False
        self.in_closed_list = False
    
    @property
    def pos(self) -> tuple[int, int]:
        """Get position as tuple."""
        return (self.x, self.y)
    
    def reset_pathfinding(self) -> None:
        """Reset pathfinding attributes for new search."""
        self.g = float('inf')
        self.h = 0.0
        self.f = float('inf')
        self.parent = None
        self.visited = False
        self.in_open_list = False
        self.in_closed_list = False
    
    def add_neighbor(self, node: 'Node') -> None:
        """Add a neighboring node."""
        if node not in self.neighbors:
            self.neighbors.append(node)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Node({self.x}, {self.y}, walkable={self.walkable}, weight={self.weight})"
    
    def __eq__(self, other) -> bool:
        """Check equality based on position."""
        if not isinstance(other, Node):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        """Hash based on position."""
        return hash((self.x, self.y))
    
    def __lt__(self, other) -> bool:
        """Less than comparison for priority queue (based on f value)."""
        return self.f < other.f

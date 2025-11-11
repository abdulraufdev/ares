"""Node representation for graph-based navigation."""
from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class Node:
    """Represents a node in the graph with label, position, and edges."""
    label: str  # Node label (A, B, C, ...)
    pos: Tuple[float, float]  # Visual position (x, y) for rendering
    walkable: bool = True  # Can be blocked by player ability
    edges: Dict[str, float] = field(default_factory=dict)  # neighbor_label -> weight
    
    # Visualization states
    occupied_by_player: bool = False
    occupied_by_enemy: bool = False
    visited_by_enemy: bool = False
    in_open_list: bool = False
    is_target: bool = False
    
    def add_edge(self, neighbor_label: str, weight: float) -> None:
        """Add an edge to a neighbor node."""
        self.edges[neighbor_label] = weight
    
    def get_weight(self, neighbor_label: str) -> float:
        """Get the weight of an edge to a neighbor."""
        return self.edges.get(neighbor_label, float('inf'))
    
    def is_neighbor(self, other_label: str) -> bool:
        """Check if another node is a neighbor."""
        return other_label in self.edges
    
    def reset_state(self) -> None:
        """Reset visualization states."""
        self.occupied_by_player = False
        self.occupied_by_enemy = False
        self.visited_by_enemy = False
        self.in_open_list = False
        self.is_target = False

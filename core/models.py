"""Data models for Project ARES."""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class MovementSegment:
    """Represents an active movement animation between two nodes."""
    origin_node: int  # Node ID
    target_node: int  # Node ID
    start_time: float  # milliseconds
    duration: float  # milliseconds
    weight: float
    
    def get_progress(self, current_time: float) -> float:
        """Calculate progress (0.0 to 1.0) through this segment."""
        elapsed = current_time - self.start_time
        return min(1.0, elapsed / self.duration)
    
    def get_interpolated_pos(self, current_time: float, arena) -> tuple[float, float]:
        """Get interpolated position at current time."""
        t = self.get_progress(current_time)
        pos0 = arena.get_node_position(self.origin_node)
        pos1 = arena.get_node_position(self.target_node)
        x = pos0[0] + (pos1[0] - pos0[0]) * t
        y = pos0[1] + (pos1[1] - pos0[1]) * t
        return (x, y)
    
    def is_complete(self, current_time: float) -> bool:
        """Check if movement segment is complete."""
        return current_time >= self.start_time + self.duration

@dataclass
class Agent:
    """Represents a player or enemy agent."""
    name: str
    pos: int  # Node ID in arena
    stamina: float
    hp: float
    path: list[int] = field(default_factory=list)  # List of node IDs
    path_index: int = 0
    movement_segment: Optional[MovementSegment] = None
    
    @property
    def in_transit(self) -> bool:
        """Check if agent is currently moving between nodes."""
        return self.movement_segment is not None

@dataclass
class Stats:
    """Statistics for pathfinding algorithm execution."""
    nodes_expanded: int = 0
    compute_ms: float = 0.0
    path_len: int = 0
    path_cost: float = 0.0
    notes: str = ""
    
    # Additional tracking for enhanced stats
    distance_traveled: float = 0.0
    cost_traveled: float = 0.0
    enemy_nodes_explored: int = 0
    enemy_path_recalculations: int = 0
    max_frontier_size: int = 0
    abilities_used: dict[str, int] = field(default_factory=dict)
    edges_reweighted: int = 0
    nodes_blocked: int = 0

@dataclass
class Plan:
    """Represents a tactical plan for combat."""
    actions: list[str] = field(default_factory=list)
    score: float = 0.0

"""Data models for Project ARES."""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class MovementSegment:
    """Represents an active movement animation between two nodes."""
    origin_node: tuple[int, int]
    target_node: tuple[int, int]
    start_time: float  # milliseconds
    duration: float  # milliseconds
    weight: float
    
    def get_progress(self, current_time: float) -> float:
        """Calculate progress (0.0 to 1.0) through this segment."""
        elapsed = current_time - self.start_time
        return min(1.0, elapsed / self.duration)
    
    def get_interpolated_pos(self, current_time: float) -> tuple[float, float]:
        """Get interpolated position at current time."""
        t = self.get_progress(current_time)
        x0, y0 = self.origin_node
        x1, y1 = self.target_node
        return (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)
    
    def is_complete(self, current_time: float) -> bool:
        """Check if movement segment is complete."""
        return current_time >= self.start_time + self.duration

@dataclass
class Agent:
    """Represents a player or enemy agent."""
    name: str
    pos: tuple[int, int]
    stamina: float
    hp: float
    path: list[tuple[int, int]] = field(default_factory=list)
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

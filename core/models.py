"""Data models for Project ARES."""
from dataclasses import dataclass, field

@dataclass
class Agent:
    """Represents a player or enemy agent."""
    name: str
    pos: tuple[int, int]
    stamina: float
    hp: float
    path: list[tuple[int, int]] = field(default_factory=list)
    path_index: int = 0

@dataclass
class Stats:
    """Statistics for pathfinding algorithm execution."""
    nodes_expanded: int = 0
    compute_ms: float = 0.0
    path_len: int = 0
    path_cost: float = 0.0
    notes: str = ""

@dataclass
class Plan:
    """Represents a tactical plan for combat."""
    actions: list[str] = field(default_factory=list)
    score: float = 0.0

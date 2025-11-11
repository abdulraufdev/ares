"""Data models for Project ARES."""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Agent:
    """Represents a player or enemy agent."""
    name: str
    pos: tuple[int, int]  # Grid position (legacy)
    stamina: float
    hp: float
    path: list[tuple[int, int]] = field(default_factory=list)
    path_index: int = 0
    
    # Graph-based attributes
    node_label: Optional[str] = None  # Current node label (A, B, C...)
    node_path: List[str] = field(default_factory=list)  # Path as node labels
    node_path_index: int = 0
    total_distance: float = 0.0
    total_cost: float = 0.0
    visited_nodes: List[str] = field(default_factory=list)
    abilities_used: dict = field(default_factory=dict)

@dataclass
class Stats:
    """Statistics for pathfinding algorithm execution."""
    nodes_expanded: int = 0
    compute_ms: float = 0.0
    path_len: int = 0
    path_cost: float = 0.0
    notes: str = ""
    
    # Additional stats for graph algorithms
    frontier_size: int = 0
    heuristic_value: float = 0.0
    g_cost: float = 0.0  # Path cost for A*
    h_cost: float = 0.0  # Heuristic for A*
    f_cost: float = 0.0  # Total cost for A*

@dataclass
class Plan:
    """Represents a tactical plan for combat."""
    actions: list[str] = field(default_factory=list)
    score: float = 0.0

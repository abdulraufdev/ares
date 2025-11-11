"""Data models for Project ARES."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Agent:
    """Represents a player or enemy agent."""
    name: str
    pos: tuple[int, int]
    stamina: float
    hp: float
    max_hp: float = 100.0
    path: list[tuple[int, int]] = field(default_factory=list)
    path_index: int = 0
    
    # Combat attributes
    damage_cooldown_end: float = 0.0
    
    # Shield ability
    shield_active: bool = False
    shield_end_time: float = 0.0
    
    # Abilities (stores cooldown end times)
    abilities: dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize after dataclass init."""
        if not self.abilities:
            self.abilities = {
                'shield': 0.0,
                'teleport': 0.0,
                'block': 0.0,
                'weight': 0.0
            }
    
    def take_damage(self, amount: float, current_time: float) -> bool:
        """
        Take damage if not shielded.
        
        Args:
            amount: Damage amount
            current_time: Current game time in milliseconds
            
        Returns:
            True if damage was taken, False if blocked
        """
        if self.shield_active and current_time < self.shield_end_time:
            return False
        
        self.hp = max(0, self.hp - amount)
        return True
    
    def heal(self, amount: float) -> None:
        """Heal the agent."""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def is_alive(self) -> bool:
        """Check if agent is alive."""
        return self.hp > 0

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

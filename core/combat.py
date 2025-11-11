"""Combat system for Project ARES."""
import pygame
from core.models import Agent
from config import CONTACT_DAMAGE, MELEE_DAMAGE, DAMAGE_COOLDOWN_MS


class CombatSystem:
    """Manages combat interactions between agents."""
    
    def __init__(self):
        """Initialize combat system."""
        self.last_collision_time = 0.0
    
    def check_collision(self, agent1: Agent, agent2: Agent) -> bool:
        """
        Check if two agents are on the same cell.
        
        Args:
            agent1: First agent
            agent2: Second agent
            
        Returns:
            True if agents are colliding
        """
        return agent1.pos == agent2.pos
    
    def apply_contact_damage(self, player: Agent, enemy: Agent, current_time: float) -> None:
        """
        Apply contact damage when agents collide.
        
        Args:
            player: Player agent
            enemy: Enemy agent
            current_time: Current time in milliseconds
        """
        if not self.check_collision(player, enemy):
            return
        
        # Check if enough time has passed since last damage
        if current_time - self.last_collision_time < DAMAGE_COOLDOWN_MS:
            return
        
        # Both agents take damage on collision
        player.take_damage(CONTACT_DAMAGE, current_time)
        enemy.take_damage(CONTACT_DAMAGE, current_time)
        
        self.last_collision_time = current_time
    
    def apply_melee_damage(self, attacker: Agent, target: Agent, current_time: float) -> bool:
        """
        Apply melee damage to target.
        
        Args:
            attacker: Attacking agent
            target: Target agent
            current_time: Current time in milliseconds
            
        Returns:
            True if damage was applied
        """
        # Check cooldown
        if current_time < attacker.damage_cooldown_end:
            return False
        
        # Apply damage
        if target.take_damage(MELEE_DAMAGE, current_time):
            attacker.damage_cooldown_end = current_time + DAMAGE_COOLDOWN_MS
            return True
        
        return False
    
    def is_in_melee_range(self, agent1: Agent, agent2: Agent, range_cells: int = 1) -> bool:
        """
        Check if two agents are within melee range.
        
        Args:
            agent1: First agent
            agent2: Second agent
            range_cells: Range in cells
            
        Returns:
            True if in range
        """
        x1, y1 = agent1.pos
        x2, y2 = agent2.pos
        distance = max(abs(x1 - x2), abs(y1 - y2))  # Chebyshev distance
        return distance <= range_cells
    
    def get_health_percentage(self, agent: Agent) -> float:
        """
        Get agent's health as percentage.
        
        Args:
            agent: Agent to check
            
        Returns:
            Health percentage (0.0 to 1.0)
        """
        return agent.hp / agent.max_hp if agent.max_hp > 0 else 0.0

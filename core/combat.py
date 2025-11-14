"""Combat system for Algorithm Arena."""
import pygame


class CombatEntity:
    """Entity with health and combat capabilities."""
    
    def __init__(self, max_hp: int = 100):
        """Initialize combat entity.
        
        Args:
            max_hp: Maximum health points
        """
        self.max_hp = max_hp
        self.hp = max_hp
        self.last_damage_time = 0
        self.damage_cooldown = 1000  # milliseconds
    
    def take_damage(self, amount: int, current_time: int) -> bool:
        """Apply damage to entity.
        
        Args:
            amount: Damage amount
            current_time: Current time in milliseconds
            
        Returns:
            True if damage was applied, False if on cooldown
        """
        if current_time - self.last_damage_time < self.damage_cooldown:
            return False
        
        self.hp = max(0, self.hp - amount)
        self.last_damage_time = current_time
        return True
    
    def is_alive(self) -> bool:
        """Check if entity is still alive."""
        return self.hp > 0
    
    def get_health_percentage(self) -> float:
        """Get health as percentage (0.0 to 1.0)."""
        return self.hp / self.max_hp


class CombatSystem:
    """Manages combat between player and enemy."""
    
    def __init__(self):
        """Initialize combat system."""
        self.player = CombatEntity(max_hp=100)
        self.enemy = CombatEntity(max_hp=150)
        self.contact_damage = 10
    
    def check_contact(self, player_node, enemy_node, current_time: int) -> tuple[bool, bool]:
        """Check if player and enemy are in contact and apply damage.
        
        Args:
            player_node: Current player node
            enemy_node: Current enemy node
            current_time: Current time in milliseconds
            
        Returns:
            Tuple of (player_damaged, enemy_damaged)
        """
        if player_node == enemy_node:
            # Only player takes damage (enemy is invincible)
            player_damaged = self.player.take_damage(self.contact_damage, current_time)
            return (player_damaged, False)
        
        return (False, False)
    
    def is_game_over(self) -> tuple[bool, str]:
        """Check if game is over and return reason.
        
        Returns:
            Tuple of (is_over, reason) where reason is 'victory', 'defeat', or ''
        """
        if not self.player.is_alive():
            return (True, 'defeat')
        
        # Enemy cannot die (invincible)
        
        return (False, '')
    
    def reset(self):
        """Reset combat state."""
        self.player = CombatEntity(max_hp=100)
        self.enemy = CombatEntity(max_hp=150)

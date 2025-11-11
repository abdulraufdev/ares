"""Ability system for Project ARES."""
import pygame
from typing import Optional
from core.models import Agent
from core.node import Node
from config import ABILITIES


class AbilityManager:
    """Manages player abilities."""
    
    def __init__(self):
        """Initialize ability manager."""
        self.ability_uses = {
            'block': ABILITIES['block']['uses'],
            'weight': ABILITIES['weight']['uses']
        }
        self.blocked_nodes: list[tuple[int, int]] = []
        self.weighted_edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
    
    def can_use_ability(self, ability_name: str, agent: Agent, current_time: float) -> bool:
        """
        Check if an ability can be used.
        
        Args:
            ability_name: Name of the ability
            agent: Agent trying to use ability
            current_time: Current time in milliseconds
            
        Returns:
            True if ability can be used
        """
        if ability_name not in ABILITIES:
            return False
        
        ability_config = ABILITIES[ability_name]
        
        # Check cooldown
        if current_time < agent.abilities.get(ability_name, 0.0):
            return False
        
        # Check uses (for limited abilities)
        if ability_name in self.ability_uses:
            if self.ability_uses[ability_name] <= 0:
                return False
        
        return True
    
    def use_shield(self, agent: Agent, current_time: float) -> bool:
        """
        Activate shield ability.
        
        Args:
            agent: Agent using shield
            current_time: Current time in milliseconds
            
        Returns:
            True if shield was activated
        """
        if not self.can_use_ability('shield', agent, current_time):
            return False
        
        ability = ABILITIES['shield']
        agent.shield_active = True
        agent.shield_end_time = current_time + ability['duration_ms']
        agent.abilities['shield'] = current_time + ability['cooldown_ms']
        
        return True
    
    def use_teleport(self, agent: Agent, target_pos: tuple[int, int], 
                     nodes: list[list[Node]], current_time: float) -> bool:
        """
        Teleport agent to target position.
        
        Args:
            agent: Agent teleporting
            target_pos: Target position
            nodes: Node graph
            current_time: Current time in milliseconds
            
        Returns:
            True if teleport was successful
        """
        if not self.can_use_ability('teleport', agent, current_time):
            return False
        
        ability = ABILITIES['teleport']
        x, y = agent.pos
        tx, ty = target_pos
        
        # Check distance
        distance = max(abs(tx - x), abs(ty - y))
        if distance > ability['distance']:
            return False
        
        # Check if target is valid
        if ty >= len(nodes) or tx >= len(nodes[0]):
            return False
        
        target_node = nodes[ty][tx]
        if not target_node.walkable:
            return False
        
        # Teleport
        agent.pos = target_pos
        agent.abilities['teleport'] = current_time + ability['cooldown_ms']
        
        return True
    
    def use_block_node(self, target_pos: tuple[int, int], nodes: list[list[Node]], 
                       agent: Agent, current_time: float) -> bool:
        """
        Block a node to prevent movement.
        
        Args:
            target_pos: Position to block
            nodes: Node graph
            agent: Agent using ability
            current_time: Current time in milliseconds
            
        Returns:
            True if node was blocked
        """
        if not self.can_use_ability('block', agent, current_time):
            return False
        
        tx, ty = target_pos
        
        # Check if position is valid
        if ty >= len(nodes) or tx >= len(nodes[0]):
            return False
        
        target_node = nodes[ty][tx]
        
        # Can't block already blocked nodes or agent positions
        if not target_node.walkable:
            return False
        
        # Block the node
        target_node.walkable = False
        # Remove from neighbors
        for neighbor in target_node.neighbors[:]:
            if target_node in neighbor.neighbors:
                neighbor.neighbors.remove(target_node)
        target_node.neighbors.clear()
        
        self.blocked_nodes.append(target_pos)
        self.ability_uses['block'] -= 1
        
        return True
    
    def use_increase_weight(self, from_pos: tuple[int, int], to_pos: tuple[int, int],
                           nodes: list[list[Node]], agent: Agent, current_time: float) -> bool:
        """
        Increase weight of an edge.
        
        Args:
            from_pos: Starting position
            to_pos: Target position
            nodes: Node graph
            agent: Agent using ability
            current_time: Current time in milliseconds
            
        Returns:
            True if weight was increased
        """
        if not self.can_use_ability('weight', agent, current_time):
            return False
        
        fx, fy = from_pos
        tx, ty = to_pos
        
        # Check if positions are valid
        if (fy >= len(nodes) or fx >= len(nodes[0]) or 
            ty >= len(nodes) or tx >= len(nodes[0])):
            return False
        
        target_node = nodes[ty][tx]
        
        # Increase weight
        multiplier = ABILITIES['weight']['multiplier']
        target_node.weight *= multiplier
        
        self.weighted_edges.append((from_pos, to_pos))
        self.ability_uses['weight'] -= 1
        
        return True
    
    def update_shield(self, agent: Agent, current_time: float) -> None:
        """
        Update shield status.
        
        Args:
            agent: Agent with shield
            current_time: Current time in milliseconds
        """
        if agent.shield_active and current_time >= agent.shield_end_time:
            agent.shield_active = False
    
    def get_cooldown_remaining(self, ability_name: str, agent: Agent, current_time: float) -> float:
        """
        Get remaining cooldown time for an ability.
        
        Args:
            ability_name: Name of the ability
            agent: Agent to check
            current_time: Current time in milliseconds
            
        Returns:
            Remaining cooldown in milliseconds
        """
        if ability_name not in agent.abilities:
            return 0.0
        
        remaining = agent.abilities[ability_name] - current_time
        return max(0.0, remaining)
    
    def get_remaining_uses(self, ability_name: str) -> int:
        """
        Get remaining uses for an ability.
        
        Args:
            ability_name: Name of the ability
            
        Returns:
            Remaining uses or -1 for unlimited
        """
        if ability_name in self.ability_uses:
            return int(self.ability_uses[ability_name])
        return -1  # Unlimited

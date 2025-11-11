"""User input handling."""
import pygame
import math
from dataclasses import dataclass
from typing import Optional
from core.arena import Arena
from core.models import Agent
from config import NODE_RADIUS

@dataclass
class UIState:
    """Represents UI state changes from input."""
    paused: Optional[bool] = None
    map_switch: bool = False
    clicked_node: Optional[int] = None

class UIHandler:
    """Handles keyboard and mouse input and UI state."""
    
    def __init__(self):
        """Initialize UI handler."""
        self.is_paused = False
    
    def handle_keypress(self, key: int) -> UIState:
        """Process keypress and return state changes."""
        state = UIState()
        
        # Pause toggle
        if key == pygame.K_SPACE:
            self.is_paused = not self.is_paused
            state.paused = self.is_paused
        
        # Map switch (future feature)
        elif key == pygame.K_m:
            state.map_switch = True
        
        return state
    
    def handle_mouse_click(self, mouse_pos: tuple[int, int], arena: Arena) -> Optional[int]:
        """Get the node clicked at mouse position."""
        mx, my = mouse_pos
        
        # Find the closest node within click radius
        closest_node = None
        closest_dist = float('inf')
        
        for node_id, pos in arena.nodes.items():
            if node_id in arena.blocked:
                continue
            
            dist = math.sqrt((pos[0] - mx)**2 + (pos[1] - my)**2)
            if dist < NODE_RADIUS + 5 and dist < closest_dist:
                closest_node = node_id
                closest_dist = dist
        
        return closest_node
    
    def get_hovered_node(self, mouse_pos: tuple[int, int], arena: Arena) -> Optional[int]:
        """Get the node currently under the mouse."""
        return self.handle_mouse_click(mouse_pos, arena)
    
    def generate_tooltip_content(
        self, 
        hovered_node: int, 
        player: Agent, 
        arena: Arena, 
        algo: str
    ) -> list[str]:
        """Generate tooltip content for a hovered node."""
        if hovered_node in arena.blocked:
            return []
        
        # Check if node is adjacent to player
        player_neighbors = list(arena.neighbors(player.pos))
        is_adjacent = hovered_node in player_neighbors
        
        if not is_adjacent and hovered_node != player.pos:
            return []
        
        if hovered_node == player.pos:
            return [f"Current Position (Node {hovered_node})"]
        
        lines = [f"Node {hovered_node}"]
        
        # Edge weight from player to hovered node
        if algo in ['UCS', 'A*']:
            weight = arena.step_cost(player.pos, hovered_node)
            lines.append(f"Edge Weight: {weight:.2f}")
        
        # Get neighbors of hovered node (excluding player position)
        lines.append("")
        lines.append("Next Options:")
        neighbors = list(arena.neighbors(hovered_node))
        
        # Filter out the player's current position
        future_neighbors = [n for n in neighbors if n != player.pos]
        
        if not future_neighbors:
            lines.append("  (none)")
        else:
            for neighbor in future_neighbors[:5]:  # Limit to 5 for space
                weight = arena.step_cost(hovered_node, neighbor)
                if algo in ['UCS', 'A*']:
                    lines.append(f"  Node {neighbor}: w={weight:.1f}")
                else:
                    lines.append(f"  Node {neighbor}")
        
        return lines

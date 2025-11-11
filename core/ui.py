"""User input handling."""
import pygame
from dataclasses import dataclass
from typing import Optional
from core.grid import Grid
from core.models import Agent
from algorithms.common import manhattan, euclidean

@dataclass
class UIState:
    """Represents UI state changes from input."""
    paused: Optional[bool] = None
    map_switch: bool = False

class UIHandler:
    """Handles keyboard input and UI state."""
    
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
    
    def get_hovered_node(self, mouse_pos: tuple[int, int], cell_size: int) -> Optional[tuple[int, int]]:
        """Get the grid node at mouse position."""
        x, y = mouse_pos
        grid_x = x // cell_size
        grid_y = y // cell_size
        return (grid_x, grid_y)
    
    def generate_tooltip_content(
        self, 
        hovered_node: tuple[int, int], 
        player: Agent, 
        grid: Grid, 
        algo: str
    ) -> list[str]:
        """Generate tooltip content for a hovered node.
        
        Shows information about the hovered node and its neighbors (future options),
        but NOT information about the current player node.
        """
        hx, hy = hovered_node
        px, py = player.pos
        
        # Check if node is valid and passable
        if not grid.in_bounds(hovered_node) or not grid.passable(hovered_node):
            return []
        
        # Check if node is adjacent to player
        is_adjacent = abs(hx - px) <= 1 and abs(hy - py) <= 1 and (hx, hy) != (px, py)
        
        if not is_adjacent:
            # Only show tooltip for adjacent nodes
            return []
        
        lines = [f"Node ({hx}, {hy})"]
        
        # Distance from player to hovered node
        if algo not in ['BFS', 'DFS']:  # Show distance for algorithms that care
            dist = euclidean((px, py), (hx, hy))
            lines.append(f"Distance: {dist:.2f}")
        
        # Edge weight from player to hovered node
        if algo in ['UCS', 'A*']:
            weight = grid.step_cost((px, py), (hx, hy))
            lines.append(f"Edge Weight: {weight:.2f}")
        
        # Heuristic for hovered node (if applicable)
        # Note: We'd need the goal position to calculate this properly
        # For now, we'll skip this or use a placeholder
        
        # Get neighbors of hovered node (excluding player position)
        lines.append("")
        lines.append("Next Options:")
        neighbors = list(grid.neighbors(hovered_node))
        
        # Filter out the player's current position
        future_neighbors = [n for n in neighbors if n != (px, py)]
        
        if not future_neighbors:
            lines.append("  (none)")
        else:
            for neighbor in future_neighbors[:5]:  # Limit to 5 for space
                nx, ny = neighbor
                weight = grid.step_cost(hovered_node, neighbor)
                if algo in ['UCS', 'A*']:
                    lines.append(f"  ({nx},{ny}): w={weight:.1f}")
                else:
                    lines.append(f"  ({nx},{ny})")
        
        return lines

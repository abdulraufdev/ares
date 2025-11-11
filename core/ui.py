"""User input handling."""
import pygame
from dataclasses import dataclass
from typing import Optional

@dataclass
class UIState:
    """Represents UI state changes from input."""
    algo_key: Optional[str] = None
    paused: Optional[bool] = None
    map_switch: bool = False
    ability_key: Optional[str] = None
    mouse_click: Optional[tuple[int, int]] = None  # Grid coordinates

class UIHandler:
    """Handles keyboard and mouse input and UI state."""
    
    def __init__(self):
        """Initialize UI handler."""
        self.is_paused = False
    
    def handle_keypress(self, key: int) -> UIState:
        """Process keypress and return state changes."""
        state = UIState()
        
        # Algorithm selection
        if key == pygame.K_1:
            state.algo_key = '1'
        elif key == pygame.K_2:
            state.algo_key = '2'
        elif key == pygame.K_3:
            state.algo_key = '3'
        elif key == pygame.K_4:
            state.algo_key = '4'
        elif key == pygame.K_5:
            state.algo_key = '5'
        
        # Pause toggle
        elif key == pygame.K_SPACE:
            self.is_paused = not self.is_paused
            state.paused = self.is_paused
        
        # Map switch
        elif key == pygame.K_m:
            state.map_switch = True
        
        # Ability keys
        elif key == pygame.K_q:
            state.ability_key = 'shield'
        elif key == pygame.K_w:
            state.ability_key = 'teleport'
        elif key == pygame.K_e:
            state.ability_key = 'block'
        elif key == pygame.K_r:
            state.ability_key = 'weight'
        
        return state
    
    def handle_mouse_click(self, pos: tuple[int, int], cell_size: int) -> UIState:
        """
        Process mouse click and return state changes.
        
        Args:
            pos: Mouse position in pixels
            cell_size: Size of grid cells
            
        Returns:
            UIState with mouse click in grid coordinates
        """
        state = UIState()
        
        # Convert pixel position to grid coordinates
        x, y = pos
        grid_x = x // cell_size
        grid_y = y // cell_size
        
        state.mouse_click = (grid_x, grid_y)
        
        return state

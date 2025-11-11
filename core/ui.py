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

class UIHandler:
    """Handles keyboard input and UI state."""
    
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
        
        return state

"""Theme management for algorithm-specific visuals."""
from typing import Optional
from config import ALGORITHM_THEMES


class ThemeManager:
    """Manages visual themes for different algorithms."""
    
    def __init__(self):
        """Initialize theme manager."""
        self.current_theme = 'BFS'
    
    def set_theme(self, algorithm: str) -> None:
        """
        Set the current theme based on algorithm.
        
        Args:
            algorithm: Algorithm name
        """
        if algorithm in ALGORITHM_THEMES:
            self.current_theme = algorithm
    
    def get_theme(self, algorithm: Optional[str] = None) -> dict:
        """
        Get theme configuration.
        
        Args:
            algorithm: Algorithm name (uses current if None)
            
        Returns:
            Theme configuration dictionary
        """
        algo = algorithm if algorithm else self.current_theme
        return ALGORITHM_THEMES.get(algo, ALGORITHM_THEMES['BFS'])
    
    def get_color(self, color_type: str, algorithm: Optional[str] = None) -> tuple[int, int, int]:
        """
        Get a specific color from theme.
        
        Args:
            color_type: Type of color (primary, secondary, background, path, visited, open, closed)
            algorithm: Algorithm name (uses current if None)
            
        Returns:
            RGB color tuple
        """
        theme = self.get_theme(algorithm)
        return theme.get(color_type, (255, 255, 255))
    
    def get_name(self, algorithm: Optional[str] = None) -> str:
        """
        Get theme name.
        
        Args:
            algorithm: Algorithm name (uses current if None)
            
        Returns:
            Theme name
        """
        theme = self.get_theme(algorithm)
        return theme.get('name', 'Default')

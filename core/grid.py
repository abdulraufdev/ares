"""Grid representation and navigation."""
import random
from typing import Iterator

class Grid:
    """Represents the game grid with obstacles and navigation."""
    
    def __init__(self, width: int, height: int, obstacle_ratio: float = 0.25, 
                 seed: int = 42, eight_connected: bool = True):
        """Initialize grid with random obstacles."""
        self.w = width
        self.h = height
        self.eight_connected = eight_connected
        
        # Initialize grids
        self.blocked = [[False] * width for _ in range(height)]
        self.cost = [[1.0] * width for _ in range(height)]
        
        # Generate random obstacles
        random.seed(seed)
        for y in range(height):
            for x in range(width):
                # Less likely to block borders
                if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                    if random.random() < obstacle_ratio * 0.3:
                        self.blocked[y][x] = True
                else:
                    if random.random() < obstacle_ratio:
                        self.blocked[y][x] = True
    
    def in_bounds(self, pos: tuple[int, int]) -> bool:
        """Check if position is within grid bounds."""
        x, y = pos
        return 0 <= x < self.w and 0 <= y < self.h
    
    def passable(self, pos: tuple[int, int]) -> bool:
        """Check if position is passable (not blocked)."""
        x, y = pos
        return not self.blocked[y][x]
    
    def neighbors(self, pos: tuple[int, int]) -> Iterator[tuple[int, int]]:
        """Yield valid neighboring positions."""
        x, y = pos
        
        # 4-way movement
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        # Add diagonals for 8-way
        if self.eight_connected:
            directions.extend([(-1, -1), (1, -1), (1, 1), (-1, 1)])
        
        for dx, dy in directions:
            next_pos = (x + dx, y + dy)
            if self.in_bounds(next_pos) and self.passable(next_pos):
                yield next_pos
    
    def step_cost(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> float:
        """Get the cost of moving from one position to another."""
        x, y = to_pos
        base_cost = self.cost[y][x]
        
        # Diagonal moves cost more (sqrt(2) ≈ 1.414)
        fx, fy = from_pos
        if abs(x - fx) + abs(y - fy) == 2:  # Diagonal
            return base_cost * 1.414
        
        return base_cost

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
    
    def get_opposite_corners(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """Get two opposite corner positions that are passable and not adjacent.
        Returns (player_start, enemy_start) where player is at min(x+y) corner
        and enemy is at max(x+y) corner."""
        
        # Collect all passable cells
        passable_cells = []
        for y in range(self.h):
            for x in range(self.w):
                if not self.blocked[y][x]:
                    passable_cells.append((x, y))
        
        if not passable_cells:
            # Fallback to (0, 0) and (w-1, h-1) if no passable cells
            return (0, 0), (self.w - 1, self.h - 1)
        
        # Sort by sum of coordinates
        passable_cells.sort(key=lambda p: p[0] + p[1])
        
        # Player starts at minimum sum (top-left-ish corner)
        player_pos = passable_cells[0]
        
        # Enemy starts at maximum sum (bottom-right-ish corner)
        enemy_pos = passable_cells[-1]
        
        # Ensure they're not adjacent
        px, py = player_pos
        ex, ey = enemy_pos
        distance = max(abs(ex - px), abs(ey - py))  # Chebyshev distance
        
        if distance <= 1:
            # If they would be adjacent, find a different enemy position
            # Use the cell with second-highest sum
            if len(passable_cells) > 1:
                enemy_pos = passable_cells[-2]
        
        return player_pos, enemy_pos

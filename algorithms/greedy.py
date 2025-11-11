"""Greedy Best-First Search pathfinding."""
import heapq
from core.grid import Grid
from core.models import Stats
from algorithms.common import manhattan

def find_path(grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> tuple[list[tuple[int, int]], Stats]:
    """Find path using Greedy Best-First Search."""
    stats = Stats()
    
    if start == goal:
        stats.path_len = 1
        return [start], stats
    
    frontier = [(manhattan(start, goal), start)]
    came_from = {start: None}
    
    while frontier:
        _, current = heapq.heappop(frontier)
        stats.nodes_expanded += 1
        
        if current == goal:
            # Reconstruct path
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            path.reverse()
            stats.path_len = len(path)
            return path, stats
        
        for next_pos in grid.neighbors(current):
            if next_pos not in came_from:
                priority = manhattan(next_pos, goal)
                heapq.heappush(frontier, (priority, next_pos))
                came_from[next_pos] = current
    
    return [], stats

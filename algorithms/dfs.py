"""Depth-First Search pathfinding."""
from typing import Union
from core.grid import Grid
from core.graph import Graph
from core.models import Stats


def find_path(grid: Union[Grid, Graph], start, goal) -> tuple[list, Stats]:
    """Find path using DFS."""
    stats = Stats()
    
    if start == goal:
        stats.path_len = 1
        return [start], stats
    
    frontier = [start]
    came_from = {start: None}
    
    while frontier:
        current = frontier.pop()  # Stack: pop from end
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
                frontier.append(next_pos)
                came_from[next_pos] = current
    
    return [], stats


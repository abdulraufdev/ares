"""Uniform Cost Search pathfinding."""
import heapq
from typing import Union
from core.grid import Grid
from core.graph import Graph
from core.models import Stats


def find_path(grid: Union[Grid, Graph], start, goal) -> tuple[list, Stats]:
    """Find path using Uniform Cost Search."""
    stats = Stats()
    
    if start == goal:
        stats.path_len = 1
        return [start], stats
    
    frontier = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while frontier:
        current_cost, current = heapq.heappop(frontier)
        stats.nodes_expanded += 1
        
        if current == goal:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            stats.path_len = len(path)
            stats.path_cost = cost_so_far[current]
            return path, stats
        
        for next_pos in grid.neighbors(current):
            new_cost = cost_so_far[current] + grid.step_cost(current, next_pos)
            
            if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                cost_so_far[next_pos] = new_cost
                priority = new_cost
                heapq.heappush(frontier, (priority, next_pos))
                came_from[next_pos] = current
    
    return [], stats


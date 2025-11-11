"""A* pathfinding algorithm."""
import heapq
from core.grid import Grid
from core.models import Stats
from algorithms.common import manhattan

def find_path(grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> tuple[list[tuple[int, int]], Stats]:
    """Find path using A* algorithm."""
    stats = Stats()
    
    if start == goal:
        stats.path_len = 1
        return [start], stats
    
    frontier = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while frontier:
        _, current = heapq.heappop(frontier)
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
                priority = new_cost + manhattan(next_pos, goal)
                heapq.heappush(frontier, (priority, next_pos))
                came_from[next_pos] = current
    
    return [], stats

"""Depth-First Search pathfinding."""
from core.models import Stats

def find_path(arena, start: int, goal: int) -> tuple[list[int], Stats]:
    """Find path using DFS on arena graph."""
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
        
        for next_node in arena.neighbors(current):
            if next_node not in came_from:
                frontier.append(next_node)
                came_from[next_node] = current
    
    return [], stats

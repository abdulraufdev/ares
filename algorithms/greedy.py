"""Greedy Best-First Search pathfinding."""
import heapq
from core.models import Stats
from algorithms.common import euclidean_nodes

def find_path(arena, start: int, goal: int) -> tuple[list[int], Stats]:
    """Find path using Greedy Best-First Search on arena graph."""
    stats = Stats()
    
    if start == goal:
        stats.path_len = 1
        return [start], stats
    
    goal_pos = arena.get_node_position(goal)
    start_pos = arena.get_node_position(start)
    h = euclidean_nodes(start_pos, goal_pos)
    
    frontier = [(h, start)]
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
        
        for next_node in arena.neighbors(current):
            if next_node not in came_from:
                next_pos = arena.get_node_position(next_node)
                priority = euclidean_nodes(next_pos, goal_pos)
                heapq.heappush(frontier, (priority, next_node))
                came_from[next_node] = current
    
    return [], stats

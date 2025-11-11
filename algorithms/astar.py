"""A* pathfinding algorithm."""
import heapq
from core.models import Stats
from algorithms.common import euclidean_nodes

def find_path(arena, start: int, goal: int) -> tuple[list[int], Stats]:
    """Find path using A* algorithm on arena graph."""
    stats = Stats()
    
    if start == goal:
        stats.path_len = 1
        return [start], stats
    
    # Get positions for heuristic
    goal_pos = arena.get_node_position(goal)
    
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
        
        for next_node in arena.neighbors(current):
            new_cost = cost_so_far[current] + arena.step_cost(current, next_node)
            
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                
                # Use Euclidean distance as heuristic
                next_pos = arena.get_node_position(next_node)
                h = euclidean_nodes(next_pos, goal_pos)
                priority = new_cost + h
                
                heapq.heappush(frontier, (priority, next_node))
                came_from[next_node] = current
    
    return [], stats

"""Graph-based pathfinding algorithms for Algorithm Arena."""
from collections import deque
import heapq
from core.node import Node
from core.models import Stats


def bfs_find_path(graph, start_node: Node, goal_node: Node, visited_leaves: set[Node] = None) -> tuple[list[Node], Stats]:
    """Find path using Breadth-First Search on graph.
    
    BFS can revisit regular nodes but cannot revisit leaf nodes that were
    already explored.
    
    Args:
        graph: Graph object containing nodes
        start_node: Starting node
        goal_node: Target node
        visited_leaves: Set of leaf nodes already visited (cannot revisit)
        
    Returns:
        Tuple of (path, stats) where path is list of nodes
    """
    stats = Stats()
    
    if visited_leaves is None:
        visited_leaves = set()
    
    # If goal is a visited leaf, no path possible
    if goal_node.is_leaf() and goal_node in visited_leaves:
        return [], stats
    
    if start_node == goal_node:
        stats.path_len = 1
        stats.path_cost = 0.0
        return [start_node], stats
    
    # Reset all nodes
    graph.reset_all_nodes()
    
    frontier = deque([start_node])
    start_node.visited = True
    start_node.parent = None
    
    while frontier:
        current = frontier.popleft()
        stats.nodes_expanded += 1
        
        # Track visited leaves
        if current.is_leaf() and current != start_node:
            visited_leaves.add(current)
        
        if current == goal_node:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = node.parent
            path.reverse()
            stats.path_len = len(path)
            
            # Calculate path cost (sum of edge weights)
            path_cost = 0.0
            for i in range(len(path) - 1):
                weight = path[i].get_weight_to(path[i + 1])
                path_cost += weight
            stats.path_cost = path_cost
            
            return path, stats
        
        for neighbor, weight in current.neighbors:
            # Skip if neighbor is a visited leaf
            if neighbor.is_leaf() and neighbor in visited_leaves:
                continue
            
            if not neighbor.visited:
                neighbor.visited = True
                neighbor.parent = current
                frontier.append(neighbor)
    
    return [], stats


def dfs_find_path(graph, start_node: Node, goal_node: Node, visited_leaves: set[Node] = None) -> tuple[list[Node], Stats]:
    """Find path using Depth-First Search on graph.
    
    DFS can revisit regular nodes but cannot revisit leaf nodes that were
    already explored.
    
    Args:
        graph: Graph object containing nodes
        start_node: Starting node
        goal_node: Target node
        visited_leaves: Set of leaf nodes already visited (cannot revisit)
        
    Returns:
        Tuple of (path, stats) where path is list of nodes
    """
    stats = Stats()
    
    if visited_leaves is None:
        visited_leaves = set()
    
    # If goal is a visited leaf, no path possible
    if goal_node.is_leaf() and goal_node in visited_leaves:
        return [], stats
    
    if start_node == goal_node:
        stats.path_len = 1
        stats.path_cost = 0.0
        return [start_node], stats
    
    # Reset all nodes
    graph.reset_all_nodes()
    
    stack = [start_node]
    start_node.visited = True
    start_node.parent = None
    
    while stack:
        current = stack.pop()
        stats.nodes_expanded += 1
        
        # Track visited leaves
        if current.is_leaf() and current != start_node:
            visited_leaves.add(current)
        
        if current == goal_node:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = node.parent
            path.reverse()
            stats.path_len = len(path)
            
            # Calculate path cost (sum of edge weights)
            path_cost = 0.0
            for i in range(len(path) - 1):
                weight = path[i].get_weight_to(path[i + 1])
                path_cost += weight
            stats.path_cost = path_cost
            
            return path, stats
        
        for neighbor, weight in current.neighbors:
            # Skip if neighbor is a visited leaf
            if neighbor.is_leaf() and neighbor in visited_leaves:
                continue
            
            if not neighbor.visited:
                neighbor.visited = True
                neighbor.parent = current
                stack.append(neighbor)
    
    return [], stats


def ucs_find_path(graph, start_node: Node, goal_node: Node, visited_leaves: set[Node] = None) -> tuple[list[Node], Stats]:
    """Find path using Uniform Cost Search on graph.
    
    UCS can revisit regular nodes but cannot revisit leaf nodes that were
    already explored.
    
    Args:
        graph: Graph object containing nodes
        start_node: Starting node
        goal_node: Target node
        visited_leaves: Set of leaf nodes already visited (cannot revisit)
        
    Returns:
        Tuple of (path, stats) where path is list of nodes
    """
    stats = Stats()
    
    if visited_leaves is None:
        visited_leaves = set()
    
    # If goal is a visited leaf, no path possible
    if goal_node.is_leaf() and goal_node in visited_leaves:
        return [], stats
    
    if start_node == goal_node:
        stats.path_len = 1
        stats.path_cost = 0.0
        return [start_node], stats
    
    # Reset all nodes
    graph.reset_all_nodes()
    
    frontier = [(0, id(start_node), start_node)]
    start_node.g_cost = 0
    start_node.parent = None
    start_node.visited = True
    
    while frontier:
        cost, _, current = heapq.heappop(frontier)
        stats.nodes_expanded += 1
        
        # Track visited leaves
        if current.is_leaf() and current != start_node:
            visited_leaves.add(current)
        
        if current == goal_node:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = node.parent
            path.reverse()
            stats.path_len = len(path)
            stats.path_cost = current.g_cost
            return path, stats
        
        for neighbor, weight in current.neighbors:
            # Skip if neighbor is a visited leaf
            if neighbor.is_leaf() and neighbor in visited_leaves:
                continue
            
            new_cost = current.g_cost + weight
            
            if not neighbor.visited or new_cost < neighbor.g_cost:
                neighbor.visited = True
                neighbor.g_cost = new_cost
                neighbor.parent = current
                heapq.heappush(frontier, (new_cost, id(neighbor), neighbor))
    
    return [], stats


def greedy_find_path(graph, start_node: Node, goal_node: Node) -> tuple[list[Node], Stats]:
    """Find path using Greedy Best-First Search on graph.
    
    Args:
        graph: Graph object containing nodes
        start_node: Starting node
        goal_node: Target node
        
    Returns:
        Tuple of (path, stats) where path is list of nodes
    """
    stats = Stats()
    
    if start_node == goal_node:
        stats.path_len = 1
        stats.path_cost = 0.0
        return [start_node], stats
    
    # Reset all nodes
    graph.reset_all_nodes()
    
    # Calculate heuristic for start (use pre-calculated)
    start_node.h_cost = start_node.get_heuristic_to(goal_node)
    
    frontier = [(start_node.h_cost, id(start_node), start_node)]
    start_node.visited = True
    start_node.parent = None
    
    while frontier:
        _, _, current = heapq.heappop(frontier)
        stats.nodes_expanded += 1
        
        if current == goal_node:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = node.parent
            path.reverse()
            stats.path_len = len(path)
            
            # Calculate path cost (sum of edge weights)
            path_cost = 0.0
            for i in range(len(path) - 1):
                weight = path[i].get_weight_to(path[i + 1])
                path_cost += weight
            stats.path_cost = path_cost
            
            return path, stats
        
        for neighbor, weight in current.neighbors:
            if not neighbor.visited:
                neighbor.visited = True
                neighbor.parent = current
                neighbor.h_cost = neighbor.get_heuristic_to(goal_node)
                heapq.heappush(frontier, (neighbor.h_cost, id(neighbor), neighbor))
    
    return [], stats


def astar_find_path(graph, start_node: Node, goal_node: Node) -> tuple[list[Node], Stats]:
    """Find path using A* Search on graph.
    
    Args:
        graph: Graph object containing nodes
        start_node: Starting node
        goal_node: Target node
        
    Returns:
        Tuple of (path, stats) where path is list of nodes
    """
    stats = Stats()
    
    if start_node == goal_node:
        stats.path_len = 1
        stats.path_cost = 0.0
        return [start_node], stats
    
    # Reset all nodes
    graph.reset_all_nodes()
    
    # Initialize start node
    start_node.g_cost = 0
    start_node.h_cost = start_node.get_heuristic_to(goal_node)
    start_node.f_cost = start_node.g_cost + start_node.h_cost
    start_node.parent = None
    start_node.visited = True
    
    frontier = [(start_node.f_cost, id(start_node), start_node)]
    
    while frontier:
        _, _, current = heapq.heappop(frontier)
        stats.nodes_expanded += 1
        
        if current == goal_node:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = node.parent
            path.reverse()
            stats.path_len = len(path)
            stats.path_cost = current.g_cost
            return path, stats
        
        for neighbor, weight in current.neighbors:
            new_g = current.g_cost + weight
            
            if not neighbor.visited or new_g < neighbor.g_cost:
                neighbor.visited = True
                neighbor.g_cost = new_g
                neighbor.h_cost = neighbor.get_heuristic_to(goal_node)
                neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                neighbor.parent = current
                heapq.heappush(frontier, (neighbor.f_cost, id(neighbor), neighbor))
    
    return [], stats


def greedy_local_min_find_path(graph, start_node: Node, goal_node: Node) -> tuple[list[Node], Stats]:
    """Find path using Greedy Best-First Search (Local Minima variant).
    
    This variant seeks nodes with LOWER heuristic values (closer to goal).
    Can get stuck in local minima. No backtracking allowed.
    
    Args:
        graph: Graph object containing nodes
        start_node: Starting node
        goal_node: Target node
        
    Returns:
        Tuple of (path, stats) where path is list of nodes
    """
    stats = Stats()
    
    if start_node == goal_node:
        stats.path_len = 1
        stats.path_cost = 0.0
        return [start_node], stats
    
    # Reset all nodes
    graph.reset_all_nodes()
    
    # Calculate heuristic for start (use pre-calculated)
    start_node.h_cost = start_node.get_heuristic_to(goal_node)
    
    frontier = [(start_node.h_cost, id(start_node), start_node)]
    start_node.visited = True
    start_node.parent = None
    
    while frontier:
        _, _, current = heapq.heappop(frontier)
        stats.nodes_expanded += 1
        
        if current == goal_node:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = node.parent
            path.reverse()
            stats.path_len = len(path)
            
            # Calculate path cost (sum of edge weights)
            path_cost = 0.0
            for i in range(len(path) - 1):
                weight = path[i].get_weight_to(path[i + 1])
                path_cost += weight
            stats.path_cost = path_cost
            
            return path, stats
        
        for neighbor, weight in current.neighbors:
            if not neighbor.visited:
                neighbor.visited = True
                neighbor.parent = current
                neighbor.h_cost = neighbor.get_heuristic_to(goal_node)
                heapq.heappush(frontier, (neighbor.h_cost, id(neighbor), neighbor))
    
    return [], stats


def greedy_local_max_find_path(graph, start_node: Node, goal_node: Node) -> tuple[list[Node], Stats]:
    """Find path using Greedy Best-First Search (Local Maxima variant).
    
    This variant seeks nodes with HIGHER heuristic values (farther from goal).
    Can get stuck in local maxima. No backtracking allowed.
    
    Args:
        graph: Graph object containing nodes
        start_node: Starting node
        goal_node: Target node
        
    Returns:
        Tuple of (path, stats) where path is list of nodes
    """
    stats = Stats()
    
    if start_node == goal_node:
        stats.path_len = 1
        stats.path_cost = 0.0
        return [start_node], stats
    
    # Reset all nodes
    graph.reset_all_nodes()
    
    # Calculate heuristic for start (use pre-calculated)
    start_node.h_cost = start_node.get_heuristic_to(goal_node)
    
    # Use NEGATIVE heuristic to prefer higher values (max-heap behavior)
    frontier = [(-start_node.h_cost, id(start_node), start_node)]
    start_node.visited = True
    start_node.parent = None
    
    while frontier:
        _, _, current = heapq.heappop(frontier)
        stats.nodes_expanded += 1
        
        if current == goal_node:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = node.parent
            path.reverse()
            stats.path_len = len(path)
            
            # Calculate path cost (sum of edge weights)
            path_cost = 0.0
            for i in range(len(path) - 1):
                weight = path[i].get_weight_to(path[i + 1])
                path_cost += weight
            stats.path_cost = path_cost
            
            return path, stats
        
        for neighbor, weight in current.neighbors:
            if not neighbor.visited:
                neighbor.visited = True
                neighbor.parent = current
                neighbor.h_cost = neighbor.get_heuristic_to(goal_node)
                # Use negative heuristic to prefer higher values
                heapq.heappush(frontier, (-neighbor.h_cost, id(neighbor), neighbor))
    
    return [], stats


def astar_local_min_find_path(graph, start_node: Node, goal_node: Node) -> tuple[list[Node], Stats]:
    """Find path using A* Search (Local Minima variant).
    
    Uses f(n) = g(n) + h(n), seeking lower f-values.
    Can get stuck in local minima. No backtracking allowed.
    
    Args:
        graph: Graph object containing nodes
        start_node: Starting node
        goal_node: Target node
        
    Returns:
        Tuple of (path, stats) where path is list of nodes
    """
    stats = Stats()
    
    if start_node == goal_node:
        stats.path_len = 1
        stats.path_cost = 0.0
        return [start_node], stats
    
    # Reset all nodes
    graph.reset_all_nodes()
    
    # Initialize start node
    start_node.g_cost = 0
    start_node.h_cost = start_node.get_heuristic_to(goal_node)
    start_node.f_cost = start_node.g_cost + start_node.h_cost
    start_node.parent = None
    start_node.visited = True
    
    frontier = [(start_node.f_cost, id(start_node), start_node)]
    
    while frontier:
        _, _, current = heapq.heappop(frontier)
        stats.nodes_expanded += 1
        
        if current == goal_node:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = node.parent
            path.reverse()
            stats.path_len = len(path)
            stats.path_cost = current.g_cost
            return path, stats
        
        for neighbor, weight in current.neighbors:
            new_g = current.g_cost + weight
            
            # No backtracking - only visit unvisited nodes
            if not neighbor.visited:
                neighbor.visited = True
                neighbor.g_cost = new_g
                neighbor.h_cost = neighbor.get_heuristic_to(goal_node)
                neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                neighbor.parent = current
                heapq.heappush(frontier, (neighbor.f_cost, id(neighbor), neighbor))
    
    return [], stats


def astar_local_max_find_path(graph, start_node: Node, goal_node: Node) -> tuple[list[Node], Stats]:
    """Find path using A* Search (Local Maxima variant).
    
    Uses f(n) = g(n) + h(n), but inverts heuristic to seek higher h-values.
    Can get stuck in local maxima. No backtracking allowed.
    
    Args:
        graph: Graph object containing nodes
        start_node: Starting node
        goal_node: Target node
        
    Returns:
        Tuple of (path, stats) where path is list of nodes
    """
    stats = Stats()
    
    if start_node == goal_node:
        stats.path_len = 1
        stats.path_cost = 0.0
        return [start_node], stats
    
    # Reset all nodes
    graph.reset_all_nodes()
    
    # Initialize start node
    # Find max heuristic to invert properly
    max_h = max(start_node.get_heuristic_to(n) for n in graph.nodes if n != start_node)
    
    start_node.g_cost = 0
    start_node.h_cost = start_node.get_heuristic_to(goal_node)
    # Invert heuristic: prefer higher h values by using (max_h - h)
    inverted_h = max_h - start_node.h_cost
    start_node.f_cost = start_node.g_cost + inverted_h
    start_node.parent = None
    start_node.visited = True
    
    frontier = [(start_node.f_cost, id(start_node), start_node)]
    
    while frontier:
        _, _, current = heapq.heappop(frontier)
        stats.nodes_expanded += 1
        
        if current == goal_node:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = node.parent
            path.reverse()
            stats.path_len = len(path)
            stats.path_cost = current.g_cost
            return path, stats
        
        for neighbor, weight in current.neighbors:
            new_g = current.g_cost + weight
            
            # No backtracking - only visit unvisited nodes
            if not neighbor.visited:
                neighbor.visited = True
                neighbor.g_cost = new_g
                neighbor.h_cost = neighbor.get_heuristic_to(goal_node)
                # Invert heuristic to prefer higher values
                inverted_h = max_h - neighbor.h_cost
                neighbor.f_cost = neighbor.g_cost + inverted_h
                neighbor.parent = current
                heapq.heappush(frontier, (neighbor.f_cost, id(neighbor), neighbor))
    
    return [], stats


# Algorithm dispatcher
def find_path(algorithm: str, graph, start_node: Node, goal_node: Node, visited_leaves: set[Node] = None) -> tuple[list[Node], Stats]:
    """Find path using specified algorithm.
    
    Args:
        algorithm: Algorithm name
        graph: Graph object
        start_node: Starting node
        goal_node: Target node
        visited_leaves: Set of already-visited leaf nodes (for BFS/DFS/UCS)
        
    Returns:
        Tuple of (path, stats)
    """
    if algorithm == 'BFS':
        return bfs_find_path(graph, start_node, goal_node, visited_leaves)
    elif algorithm == 'DFS':
        return dfs_find_path(graph, start_node, goal_node, visited_leaves)
    elif algorithm == 'UCS':
        return ucs_find_path(graph, start_node, goal_node, visited_leaves)
    elif algorithm == 'Greedy (Local Min)':
        return greedy_local_min_find_path(graph, start_node, goal_node)
    elif algorithm == 'Greedy (Local Max)':
        return greedy_local_max_find_path(graph, start_node, goal_node)
    elif algorithm == 'A* (Local Min)':
        return astar_local_min_find_path(graph, start_node, goal_node)
    elif algorithm == 'A* (Local Max)':
        return astar_local_max_find_path(graph, start_node, goal_node)
    # Legacy support for old names
    elif algorithm == 'Greedy':
        return greedy_local_min_find_path(graph, start_node, goal_node)
    elif algorithm == 'A*':
        return astar_local_min_find_path(graph, start_node, goal_node)
    else:
        return [], Stats()

"""Graph-based pathfinding algorithms for Algorithm Arena."""
from collections import deque
import heapq
from core.node import Node
from core.models import Stats


def bfs_find_path(graph, start_node: Node, goal_node: Node) -> tuple[list[Node], Stats]:
    """Find path using Breadth-First Search on graph.
    
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
    
    frontier = deque([start_node])
    start_node.visited = True
    start_node.parent = None
    
    while frontier:
        current = frontier.popleft()
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
                frontier.append(neighbor)
    
    return [], stats


def dfs_find_path(graph, start_node: Node, goal_node: Node) -> tuple[list[Node], Stats]:
    """Find path using Depth-First Search on graph.
    
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
    
    stack = [start_node]
    start_node.visited = True
    start_node.parent = None
    
    while stack:
        current = stack.pop()
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
                stack.append(neighbor)
    
    return [], stats


def ucs_find_path(graph, start_node: Node, goal_node: Node) -> tuple[list[Node], Stats]:
    """Find path using Uniform Cost Search on graph.
    
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
    
    frontier = [(0, id(start_node), start_node)]
    start_node.g_cost = 0
    start_node.parent = None
    start_node.visited = True
    
    while frontier:
        cost, _, current = heapq.heappop(frontier)
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
    
    # Calculate heuristic for start
    start_node.h_cost = start_node.distance_to(goal_node)
    
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
                neighbor.h_cost = neighbor.distance_to(goal_node)
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
    start_node.h_cost = start_node.distance_to(goal_node)
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
                neighbor.h_cost = neighbor.distance_to(goal_node)
                neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                neighbor.parent = current
                heapq.heappush(frontier, (neighbor.f_cost, id(neighbor), neighbor))
    
    return [], stats


# Algorithm dispatcher
def find_path(algorithm: str, graph, start_node: Node, goal_node: Node) -> tuple[list[Node], Stats]:
    """Find path using specified algorithm.
    
    Args:
        algorithm: Algorithm name ('BFS', 'DFS', 'UCS', 'Greedy', 'A*')
        graph: Graph object
        start_node: Starting node
        goal_node: Target node
        
    Returns:
        Tuple of (path, stats)
    """
    if algorithm == 'BFS':
        return bfs_find_path(graph, start_node, goal_node)
    elif algorithm == 'DFS':
        return dfs_find_path(graph, start_node, goal_node)
    elif algorithm == 'UCS':
        return ucs_find_path(graph, start_node, goal_node)
    elif algorithm == 'Greedy':
        return greedy_find_path(graph, start_node, goal_node)
    elif algorithm == 'A*':
        return astar_find_path(graph, start_node, goal_node)
    else:
        return [], Stats()

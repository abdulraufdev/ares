"""Graph-based pathfinding algorithms."""
import time
from typing import Dict, List, Tuple, Optional, Set
from collections import deque
import heapq
from core.graph import Graph
from core.models import Stats


def manhattan_heuristic(graph: Graph, from_label: str, to_label: str) -> float:
    """Manhattan distance heuristic based on node positions."""
    node1 = graph.get_node(from_label)
    node2 = graph.get_node(to_label)
    if node1 and node2:
        return abs(node1.pos[0] - node2.pos[0]) + abs(node1.pos[1] - node2.pos[1])
    return 0.0


def euclidean_heuristic(graph: Graph, from_label: str, to_label: str) -> float:
    """Euclidean distance heuristic based on node positions."""
    node1 = graph.get_node(from_label)
    node2 = graph.get_node(to_label)
    if node1 and node2:
        dx = node1.pos[0] - node2.pos[0]
        dy = node1.pos[1] - node2.pos[1]
        return (dx * dx + dy * dy) ** 0.5
    return 0.0


def bfs_graph(graph: Graph, start: str, goal: str) -> Tuple[List[str], Stats]:
    """
    Breadth-First Search on graph.
    
    Returns:
        Tuple of (path as list of node labels, statistics)
    """
    stats = Stats()
    start_time = time.perf_counter()
    
    if start == goal:
        stats.path_len = 1
        stats.compute_ms = (time.perf_counter() - start_time) * 1000
        return [start], stats
    
    start_node = graph.get_node(start)
    goal_node = graph.get_node(goal)
    
    if not start_node or not goal_node or not start_node.walkable or not goal_node.walkable:
        stats.compute_ms = (time.perf_counter() - start_time) * 1000
        return [], stats
    
    frontier = deque([start])
    came_from: Dict[str, Optional[str]] = {start: None}
    
    while frontier:
        current = frontier.popleft()
        stats.nodes_expanded += 1
        stats.frontier_size = max(stats.frontier_size, len(frontier))
        
        if current == goal:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            stats.path_len = len(path)
            stats.compute_ms = (time.perf_counter() - start_time) * 1000
            return path, stats
        
        current_node = graph.get_node(current)
        if current_node:
            for neighbor_label in graph.get_neighbors(current):
                neighbor_node = graph.get_node(neighbor_label)
                if neighbor_node and neighbor_node.walkable and neighbor_label not in came_from:
                    frontier.append(neighbor_label)
                    came_from[neighbor_label] = current
    
    stats.compute_ms = (time.perf_counter() - start_time) * 1000
    return [], stats


def dfs_graph(graph: Graph, start: str, goal: str) -> Tuple[List[str], Stats]:
    """
    Depth-First Search on graph.
    
    Returns:
        Tuple of (path as list of node labels, statistics)
    """
    stats = Stats()
    start_time = time.perf_counter()
    
    if start == goal:
        stats.path_len = 1
        stats.compute_ms = (time.perf_counter() - start_time) * 1000
        return [start], stats
    
    start_node = graph.get_node(start)
    goal_node = graph.get_node(goal)
    
    if not start_node or not goal_node or not start_node.walkable or not goal_node.walkable:
        stats.compute_ms = (time.perf_counter() - start_time) * 1000
        return [], stats
    
    frontier = [start]  # Use as stack
    came_from: Dict[str, Optional[str]] = {start: None}
    
    while frontier:
        current = frontier.pop()  # Pop from end (stack behavior)
        stats.nodes_expanded += 1
        stats.frontier_size = max(stats.frontier_size, len(frontier))
        
        if current == goal:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            stats.path_len = len(path)
            stats.compute_ms = (time.perf_counter() - start_time) * 1000
            return path, stats
        
        current_node = graph.get_node(current)
        if current_node:
            for neighbor_label in graph.get_neighbors(current):
                neighbor_node = graph.get_node(neighbor_label)
                if neighbor_node and neighbor_node.walkable and neighbor_label not in came_from:
                    frontier.append(neighbor_label)
                    came_from[neighbor_label] = current
    
    stats.compute_ms = (time.perf_counter() - start_time) * 1000
    return [], stats


def ucs_graph(graph: Graph, start: str, goal: str) -> Tuple[List[str], Stats]:
    """
    Uniform Cost Search on graph.
    
    Returns:
        Tuple of (path as list of node labels, statistics)
    """
    stats = Stats()
    start_time = time.perf_counter()
    
    if start == goal:
        stats.path_len = 1
        stats.path_cost = 0.0
        stats.compute_ms = (time.perf_counter() - start_time) * 1000
        return [start], stats
    
    start_node = graph.get_node(start)
    goal_node = graph.get_node(goal)
    
    if not start_node or not goal_node or not start_node.walkable or not goal_node.walkable:
        stats.compute_ms = (time.perf_counter() - start_time) * 1000
        return [], stats
    
    frontier: List[Tuple[float, str]] = [(0.0, start)]
    came_from: Dict[str, Optional[str]] = {start: None}
    cost_so_far: Dict[str, float] = {start: 0.0}
    
    while frontier:
        current_cost, current = heapq.heappop(frontier)
        stats.nodes_expanded += 1
        stats.frontier_size = max(stats.frontier_size, len(frontier))
        
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
            stats.compute_ms = (time.perf_counter() - start_time) * 1000
            return path, stats
        
        # Skip if we've found a better path already
        if current_cost > cost_so_far.get(current, float('inf')):
            continue
        
        current_node = graph.get_node(current)
        if current_node:
            for neighbor_label in graph.get_neighbors(current):
                neighbor_node = graph.get_node(neighbor_label)
                if neighbor_node and neighbor_node.walkable:
                    new_cost = cost_so_far[current] + graph.get_edge_weight(current, neighbor_label)
                    
                    if neighbor_label not in cost_so_far or new_cost < cost_so_far[neighbor_label]:
                        cost_so_far[neighbor_label] = new_cost
                        heapq.heappush(frontier, (new_cost, neighbor_label))
                        came_from[neighbor_label] = current
    
    stats.compute_ms = (time.perf_counter() - start_time) * 1000
    return [], stats


def greedy_graph(graph: Graph, start: str, goal: str) -> Tuple[List[str], Stats]:
    """
    Greedy Best-First Search on graph.
    
    Returns:
        Tuple of (path as list of node labels, statistics)
    """
    stats = Stats()
    start_time = time.perf_counter()
    
    if start == goal:
        stats.path_len = 1
        stats.heuristic_value = 0.0
        stats.compute_ms = (time.perf_counter() - start_time) * 1000
        return [start], stats
    
    start_node = graph.get_node(start)
    goal_node = graph.get_node(goal)
    
    if not start_node or not goal_node or not start_node.walkable or not goal_node.walkable:
        stats.compute_ms = (time.perf_counter() - start_time) * 1000
        return [], stats
    
    h_start = euclidean_heuristic(graph, start, goal)
    frontier: List[Tuple[float, str]] = [(h_start, start)]
    came_from: Dict[str, Optional[str]] = {start: None}
    visited: Set[str] = set()
    
    while frontier:
        _, current = heapq.heappop(frontier)
        
        if current in visited:
            continue
        
        visited.add(current)
        stats.nodes_expanded += 1
        stats.frontier_size = max(stats.frontier_size, len(frontier))
        
        if current == goal:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            stats.path_len = len(path)
            stats.heuristic_value = 0.0  # At goal
            stats.compute_ms = (time.perf_counter() - start_time) * 1000
            return path, stats
        
        current_node = graph.get_node(current)
        if current_node:
            for neighbor_label in graph.get_neighbors(current):
                neighbor_node = graph.get_node(neighbor_label)
                if neighbor_node and neighbor_node.walkable and neighbor_label not in visited:
                    if neighbor_label not in came_from:
                        h = euclidean_heuristic(graph, neighbor_label, goal)
                        heapq.heappush(frontier, (h, neighbor_label))
                        came_from[neighbor_label] = current
    
    stats.compute_ms = (time.perf_counter() - start_time) * 1000
    return [], stats


def astar_graph(graph: Graph, start: str, goal: str) -> Tuple[List[str], Stats]:
    """
    A* Search on graph.
    
    Returns:
        Tuple of (path as list of node labels, statistics)
    """
    stats = Stats()
    start_time = time.perf_counter()
    
    if start == goal:
        stats.path_len = 1
        stats.path_cost = 0.0
        stats.g_cost = 0.0
        stats.h_cost = 0.0
        stats.f_cost = 0.0
        stats.compute_ms = (time.perf_counter() - start_time) * 1000
        return [start], stats
    
    start_node = graph.get_node(start)
    goal_node = graph.get_node(goal)
    
    if not start_node or not goal_node or not start_node.walkable or not goal_node.walkable:
        stats.compute_ms = (time.perf_counter() - start_time) * 1000
        return [], stats
    
    h_start = euclidean_heuristic(graph, start, goal)
    frontier: List[Tuple[float, str]] = [(h_start, start)]
    came_from: Dict[str, Optional[str]] = {start: None}
    cost_so_far: Dict[str, float] = {start: 0.0}
    
    while frontier:
        _, current = heapq.heappop(frontier)
        stats.nodes_expanded += 1
        stats.frontier_size = max(stats.frontier_size, len(frontier))
        
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
            stats.g_cost = cost_so_far[current]
            stats.h_cost = 0.0  # At goal
            stats.f_cost = stats.g_cost + stats.h_cost
            stats.compute_ms = (time.perf_counter() - start_time) * 1000
            return path, stats
        
        current_node = graph.get_node(current)
        if current_node:
            for neighbor_label in graph.get_neighbors(current):
                neighbor_node = graph.get_node(neighbor_label)
                if neighbor_node and neighbor_node.walkable:
                    new_cost = cost_so_far[current] + graph.get_edge_weight(current, neighbor_label)
                    
                    if neighbor_label not in cost_so_far or new_cost < cost_so_far[neighbor_label]:
                        cost_so_far[neighbor_label] = new_cost
                        h = euclidean_heuristic(graph, neighbor_label, goal)
                        f = new_cost + h
                        heapq.heappush(frontier, (f, neighbor_label))
                        came_from[neighbor_label] = current
    
    stats.compute_ms = (time.perf_counter() - start_time) * 1000
    return [], stats

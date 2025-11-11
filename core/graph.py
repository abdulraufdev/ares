"""Graph representation for interconnected node visualization."""
import random
import math
from typing import Iterator
from dataclasses import dataclass


@dataclass
class Node:
    """Represents a node in the graph."""
    id: int
    x: float  # Visual position
    y: float  # Visual position
    label: str


@dataclass
class Edge:
    """Represents an edge between two nodes."""
    from_id: int
    to_id: int
    weight: float


class Graph:
    """Represents an interconnected graph with weighted edges."""
    
    def __init__(self, num_nodes: int = 28, seed: int = 42, 
                 layout_type: str = 'organic'):
        """Initialize graph with interconnected nodes.
        
        Args:
            num_nodes: Number of nodes (25-30 recommended)
            seed: Random seed for reproducibility
            layout_type: 'organic', 'maze', or 'open'
        """
        self.num_nodes = num_nodes
        self.seed = seed
        self.layout_type = layout_type
        self.nodes: dict[int, Node] = {}
        self.edges: dict[tuple[int, int], Edge] = {}
        self.adjacency: dict[int, list[int]] = {}
        
        random.seed(seed)
        self._generate_graph()
    
    def _generate_graph(self) -> None:
        """Generate interconnected graph with appropriate layout."""
        # Generate node positions based on layout type
        if self.layout_type == 'maze':
            self._generate_maze_layout()
        elif self.layout_type == 'open':
            self._generate_open_layout()
        else:
            self._generate_organic_layout()
        
        # Create edges (each node connects to 3-6 neighbors)
        self._generate_edges()
    
    def _generate_organic_layout(self) -> None:
        """Generate organic, visually appealing node layout."""
        width, height = 960, 720
        margin = 80
        
        # Use a relaxed grid with some randomness
        cols = int(math.sqrt(self.num_nodes * 1.5))
        rows = math.ceil(self.num_nodes / cols)
        
        cell_w = (width - 2 * margin) / cols
        cell_h = (height - 2 * margin) / rows
        
        node_id = 0
        for row in range(rows):
            for col in range(cols):
                if node_id >= self.num_nodes:
                    break
                
                # Base position with some randomness
                base_x = margin + col * cell_w + cell_w / 2
                base_y = margin + row * cell_h + cell_h / 2
                
                # Add randomness for organic feel
                offset_x = random.uniform(-cell_w * 0.3, cell_w * 0.3)
                offset_y = random.uniform(-cell_h * 0.3, cell_h * 0.3)
                
                x = base_x + offset_x
                y = base_y + offset_y
                
                # Keep within bounds
                x = max(margin, min(width - margin, x))
                y = max(margin, min(height - margin, y))
                
                self.nodes[node_id] = Node(
                    id=node_id,
                    x=x,
                    y=y,
                    label=f"N{node_id + 1}"
                )
                node_id += 1
    
    def _generate_maze_layout(self) -> None:
        """Generate maze-like grid layout with corridors."""
        width, height = 960, 720
        margin = 60
        
        cols = 7
        rows = 5
        
        cell_w = (width - 2 * margin) / cols
        cell_h = (height - 2 * margin) / rows
        
        node_id = 0
        for row in range(rows):
            for col in range(cols):
                if node_id >= self.num_nodes:
                    break
                
                x = margin + col * cell_w + cell_w / 2
                y = margin + row * cell_h + cell_h / 2
                
                # Small randomness for visual variety
                x += random.uniform(-10, 10)
                y += random.uniform(-10, 10)
                
                self.nodes[node_id] = Node(
                    id=node_id,
                    x=x,
                    y=y,
                    label=f"N{node_id + 1}"
                )
                node_id += 1
    
    def _generate_open_layout(self) -> None:
        """Generate open layout with diagonal connections."""
        width, height = 960, 720
        margin = 80
        
        # Scatter nodes more randomly
        for node_id in range(self.num_nodes):
            # Use rejection sampling to avoid clustering
            attempts = 0
            while attempts < 50:
                x = random.uniform(margin, width - margin)
                y = random.uniform(margin, height - margin)
                
                # Check distance from existing nodes
                too_close = False
                for existing in self.nodes.values():
                    dist = math.sqrt((x - existing.x) ** 2 + (y - existing.y) ** 2)
                    if dist < 60:  # Minimum distance
                        too_close = True
                        break
                
                if not too_close or attempts >= 40:
                    break
                attempts += 1
            
            self.nodes[node_id] = Node(
                id=node_id,
                x=x,
                y=y,
                label=f"N{node_id + 1}"
            )
    
    def _generate_edges(self) -> None:
        """Generate edges with weights, each node connects to 3-6 neighbors."""
        # Initialize adjacency list
        for node_id in self.nodes:
            self.adjacency[node_id] = []
        
        # Calculate distances between all nodes
        distances = []
        for i in self.nodes:
            for j in self.nodes:
                if i < j:
                    node_i = self.nodes[i]
                    node_j = self.nodes[j]
                    dist = math.sqrt((node_i.x - node_j.x) ** 2 + 
                                   (node_i.y - node_j.y) ** 2)
                    distances.append((dist, i, j))
        
        # Sort by distance
        distances.sort()
        
        # Connect nodes starting with closest pairs
        for dist, i, j in distances:
            # Check if we should add this edge
            conn_i = len(self.adjacency[i])
            conn_j = len(self.adjacency[j])
            
            # Each node should have 3-6 connections
            if conn_i >= 6 and conn_j >= 6:
                continue
            
            # Add edge if at least one node needs more connections
            if conn_i < 3 or conn_j < 3 or (conn_i < 6 and conn_j < 6 and random.random() < 0.3):
                # Normalize weight based on distance
                # Map distance to weight range 1-10
                max_dist = 400  # Approximate max distance in layout
                weight = 1 + (dist / max_dist) * 9
                weight = round(weight, 1)
                
                self.adjacency[i].append(j)
                self.adjacency[j].append(i)
                self.edges[(i, j)] = Edge(i, j, weight)
                self.edges[(j, i)] = Edge(j, i, weight)
        
        # Ensure all nodes have at least 3 connections
        for node_id in self.nodes:
            while len(self.adjacency[node_id]) < 3:
                # Find closest unconnected node
                min_dist = float('inf')
                closest = None
                node = self.nodes[node_id]
                
                for other_id, other in self.nodes.items():
                    if other_id != node_id and other_id not in self.adjacency[node_id]:
                        dist = math.sqrt((node.x - other.x) ** 2 + 
                                       (node.y - other.y) ** 2)
                        if dist < min_dist:
                            min_dist = dist
                            closest = other_id
                
                if closest is not None:
                    weight = 1 + (min_dist / 400) * 9
                    weight = round(weight, 1)
                    
                    self.adjacency[node_id].append(closest)
                    self.adjacency[closest].append(node_id)
                    self.edges[(node_id, closest)] = Edge(node_id, closest, weight)
                    self.edges[(closest, node_id)] = Edge(closest, node_id, weight)
                else:
                    break
    
    def in_bounds(self, node_id: int) -> bool:
        """Check if node ID is valid."""
        return node_id in self.nodes
    
    def passable(self, node_id: int) -> bool:
        """Check if node is passable (always True for graph)."""
        return node_id in self.nodes
    
    def neighbors(self, node_id: int) -> Iterator[int]:
        """Yield valid neighboring node IDs."""
        if node_id in self.adjacency:
            yield from self.adjacency[node_id]
    
    def step_cost(self, from_id: int, to_id: int) -> float:
        """Get the cost of moving from one node to another."""
        edge = self.edges.get((from_id, to_id))
        if edge:
            return edge.weight
        return 1.0
    
    def heuristic(self, node_id: int, goal_id: int) -> float:
        """Calculate heuristic (Euclidean distance) between nodes."""
        if node_id not in self.nodes or goal_id not in self.nodes:
            return 0.0
        
        node = self.nodes[node_id]
        goal = self.nodes[goal_id]
        
        # Euclidean distance divided by average edge weight for consistency
        dist = math.sqrt((node.x - goal.x) ** 2 + (node.y - goal.y) ** 2)
        return dist / 40  # Normalize to be comparable with edge weights

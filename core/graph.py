"""Graph representation for node-based navigation."""
import random
import math
from typing import List, Dict, Tuple, Optional
from core.node import Node


class Graph:
    """Represents the game graph with named nodes and weighted edges."""
    
    def __init__(self, num_nodes: int = 15, width: int = 800, height: int = 600, 
                 seed: int = 42, topology: str = 'mesh'):
        """
        Initialize graph with named nodes.
        
        Args:
            num_nodes: Number of nodes (up to 26 for A-Z)
            width: Width of the drawable area
            height: Height of the drawable area
            seed: Random seed for reproducibility
            topology: Graph topology ('mesh', 'grid', 'ring')
        """
        random.seed(seed)
        self.num_nodes = min(num_nodes, 26)  # Max 26 for A-Z
        self.width = width
        self.height = height
        self.topology = topology
        self.nodes: Dict[str, Node] = {}
        
        # Generate nodes
        self._generate_nodes()
        
        # Create edges based on topology
        self._create_edges()
    
    def _generate_nodes(self) -> None:
        """Generate nodes with labels A-Z and positions."""
        # Position nodes in a visually pleasing layout
        positions = self._calculate_node_positions()
        
        for i in range(self.num_nodes):
            label = chr(65 + i)  # A=65 in ASCII
            pos = positions[i]
            self.nodes[label] = Node(label=label, pos=pos)
    
    def _calculate_node_positions(self) -> List[Tuple[float, float]]:
        """Calculate visually pleasing positions for nodes."""
        positions = []
        
        if self.topology == 'grid':
            # Grid layout
            cols = int(math.ceil(math.sqrt(self.num_nodes)))
            rows = int(math.ceil(self.num_nodes / cols))
            
            spacing_x = self.width / (cols + 1)
            spacing_y = self.height / (rows + 1)
            
            for i in range(self.num_nodes):
                row = i // cols
                col = i % cols
                x = spacing_x * (col + 1)
                y = spacing_y * (row + 1)
                positions.append((x, y))
        
        elif self.topology == 'ring':
            # Circular layout
            center_x = self.width / 2
            center_y = self.height / 2
            radius = min(self.width, self.height) * 0.35
            
            for i in range(self.num_nodes):
                angle = (2 * math.pi * i) / self.num_nodes - math.pi / 2
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions.append((x, y))
        
        else:  # mesh - semi-random with spacing
            # Use a grid with random offset for natural look
            cols = int(math.ceil(math.sqrt(self.num_nodes)))
            rows = int(math.ceil(self.num_nodes / cols))
            
            spacing_x = self.width / (cols + 1)
            spacing_y = self.height / (rows + 1)
            
            for i in range(self.num_nodes):
                row = i // cols
                col = i % cols
                base_x = spacing_x * (col + 1)
                base_y = spacing_y * (row + 1)
                
                # Add random offset (30% of spacing)
                offset_x = random.uniform(-spacing_x * 0.3, spacing_x * 0.3)
                offset_y = random.uniform(-spacing_y * 0.3, spacing_y * 0.3)
                
                x = max(50, min(self.width - 50, base_x + offset_x))
                y = max(50, min(self.height - 50, base_y + offset_y))
                positions.append((x, y))
        
        return positions
    
    def _create_edges(self) -> None:
        """Create edges between nodes based on topology."""
        node_list = list(self.nodes.keys())
        
        if self.topology == 'grid':
            # Grid connections (4-way)
            cols = int(math.ceil(math.sqrt(self.num_nodes)))
            
            for i, label in enumerate(node_list):
                row = i // cols
                col = i % cols
                
                # Right neighbor
                if col < cols - 1 and i + 1 < self.num_nodes:
                    neighbor = node_list[i + 1]
                    weight = random.randint(1, 10)
                    self.add_edge(label, neighbor, weight)
                
                # Down neighbor
                if i + cols < self.num_nodes:
                    neighbor = node_list[i + cols]
                    weight = random.randint(1, 10)
                    self.add_edge(label, neighbor, weight)
        
        elif self.topology == 'ring':
            # Ring connections
            for i, label in enumerate(node_list):
                # Connect to next node in ring
                next_label = node_list[(i + 1) % self.num_nodes]
                weight = random.randint(1, 10)
                self.add_edge(label, next_label, weight)
                
                # Also connect to node 2 steps away for shortcuts
                if self.num_nodes > 4:
                    shortcut_label = node_list[(i + 2) % self.num_nodes]
                    weight = random.randint(3, 8)
                    self.add_edge(label, shortcut_label, weight)
        
        else:  # mesh - connect to nearby nodes
            # Connect each node to its N closest neighbors
            neighbors_per_node = min(4, self.num_nodes - 1)
            
            for label in node_list:
                node = self.nodes[label]
                
                # Calculate distances to all other nodes
                distances = []
                for other_label in node_list:
                    if other_label == label:
                        continue
                    other_node = self.nodes[other_label]
                    dist = self._distance(node.pos, other_node.pos)
                    distances.append((dist, other_label))
                
                # Sort by distance and connect to closest neighbors
                distances.sort()
                for _, neighbor_label in distances[:neighbors_per_node]:
                    if not node.is_neighbor(neighbor_label):
                        # Weight proportional to distance
                        dist = self._distance(node.pos, self.nodes[neighbor_label].pos)
                        weight = max(1, min(10, int(dist / 50)))
                        self.add_edge(label, neighbor_label, weight)
    
    def _distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two positions."""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def add_edge(self, from_label: str, to_label: str, weight: float) -> None:
        """Add a bidirectional edge between two nodes."""
        if from_label in self.nodes and to_label in self.nodes:
            self.nodes[from_label].add_edge(to_label, weight)
            self.nodes[to_label].add_edge(from_label, weight)
    
    def get_node(self, label: str) -> Optional[Node]:
        """Get a node by its label."""
        return self.nodes.get(label)
    
    def get_neighbors(self, label: str) -> List[str]:
        """Get list of neighbor labels for a node."""
        node = self.nodes.get(label)
        if node:
            return list(node.edges.keys())
        return []
    
    def get_edge_weight(self, from_label: str, to_label: str) -> float:
        """Get the weight of an edge between two nodes."""
        node = self.nodes.get(from_label)
        if node:
            return node.get_weight(to_label)
        return float('inf')
    
    def increase_edge_weight(self, from_label: str, to_label: str, multiplier: float = 5.0) -> None:
        """Increase the weight of an edge (player ability)."""
        if from_label in self.nodes and to_label in self.nodes:
            current_weight = self.nodes[from_label].get_weight(to_label)
            if current_weight != float('inf'):
                new_weight = current_weight * multiplier
                self.nodes[from_label].edges[to_label] = new_weight
                self.nodes[to_label].edges[from_label] = new_weight
    
    def block_node(self, label: str) -> None:
        """Block a node (player ability)."""
        node = self.nodes.get(label)
        if node:
            node.walkable = False
    
    def unblock_node(self, label: str) -> None:
        """Unblock a node."""
        node = self.nodes.get(label)
        if node:
            node.walkable = True
    
    def reset_visualization_states(self) -> None:
        """Reset all visualization states on nodes."""
        for node in self.nodes.values():
            node.reset_state()
    
    def get_all_labels(self) -> List[str]:
        """Get all node labels."""
        return list(self.nodes.keys())

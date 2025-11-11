"""Graph generation for different map types."""
import random
from typing import Literal
from core.node import Node


MapType = Literal['maze', 'weighted', 'open']


class GraphGenerator:
    """Generates different types of node graphs for pathfinding."""
    
    def __init__(self, width: int, height: int, eight_connected: bool = True):
        """
        Initialize graph generator.
        
        Args:
            width: Grid width
            height: Grid height
            eight_connected: Whether to use 8-way movement
        """
        self.width = width
        self.height = height
        self.eight_connected = eight_connected
        self.nodes: list[list[Node]] = []
    
    def generate(self, map_type: MapType, seed: int = 42) -> list[list[Node]]:
        """
        Generate a graph based on map type.
        
        Args:
            map_type: Type of map to generate
            seed: Random seed for reproducibility
            
        Returns:
            2D list of nodes
        """
        random.seed(seed)
        
        if map_type == 'maze':
            return self._generate_maze()
        elif map_type == 'weighted':
            return self._generate_weighted()
        elif map_type == 'open':
            return self._generate_open()
        else:
            raise ValueError(f"Unknown map type: {map_type}")
    
    def _generate_maze(self) -> list[list[Node]]:
        """Generate maze using recursive backtracking."""
        # Initialize all cells as walls
        self.nodes = [[Node(x, y, walkable=False) for x in range(self.width)] 
                      for y in range(self.height)]
        
        # Start from top-left corner
        start_x, start_y = 1, 1
        self.nodes[start_y][start_x].walkable = True
        
        # Stack for backtracking
        stack = [(start_x, start_y)]
        visited = {(start_x, start_y)}
        
        # Directions: N, E, S, W
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        
        while stack:
            x, y = stack[-1]
            
            # Get unvisited neighbors (2 cells away)
            neighbors = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (0 < nx < self.width - 1 and 0 < ny < self.height - 1 and 
                    (nx, ny) not in visited):
                    neighbors.append((nx, ny, dx // 2, dy // 2))
            
            if neighbors:
                # Choose random unvisited neighbor
                nx, ny, wall_dx, wall_dy = random.choice(neighbors)
                
                # Carve path to neighbor
                self.nodes[y + wall_dy][x + wall_dx].walkable = True
                self.nodes[ny][nx].walkable = True
                
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
        
        # Ensure start and goal areas are clear
        for dy in range(3):
            for dx in range(3):
                if 0 <= dy < self.height and 0 <= dx < self.width:
                    self.nodes[dy][dx].walkable = True
                if 0 <= self.height - 1 - dy < self.height and 0 <= self.width - 1 - dx < self.width:
                    self.nodes[self.height - 1 - dy][self.width - 1 - dx].walkable = True
        
        self._connect_neighbors()
        return self.nodes
    
    def _generate_weighted(self) -> list[list[Node]]:
        """Generate weighted terrain with varied costs."""
        self.nodes = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Most cells are walkable
                walkable = random.random() > 0.15
                
                # Varied weights (1-10)
                if walkable:
                    weight = random.choice([1, 1, 1, 2, 2, 3, 3, 5, 8, 10])
                else:
                    weight = 1.0
                
                row.append(Node(x, y, walkable=walkable, weight=weight))
            self.nodes.append(row)
        
        # Ensure start and goal are clear with low cost
        for dy in range(3):
            for dx in range(3):
                if 0 <= dy < self.height and 0 <= dx < self.width:
                    self.nodes[dy][dx].walkable = True
                    self.nodes[dy][dx].weight = 1.0
                if 0 <= self.height - 1 - dy < self.height and 0 <= self.width - 1 - dx < self.width:
                    self.nodes[self.height - 1 - dy][self.width - 1 - dx].walkable = True
                    self.nodes[self.height - 1 - dy][self.width - 1 - dx].weight = 1.0
        
        self._connect_neighbors()
        return self.nodes
    
    def _generate_open(self) -> list[list[Node]]:
        """Generate open field with scattered obstacles."""
        self.nodes = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Fewer obstacles
                walkable = random.random() > 0.10
                row.append(Node(x, y, walkable=walkable, weight=1.0))
            self.nodes.append(row)
        
        # Ensure start and goal are clear
        for dy in range(3):
            for dx in range(3):
                if 0 <= dy < self.height and 0 <= dx < self.width:
                    self.nodes[dy][dx].walkable = True
                if 0 <= self.height - 1 - dy < self.height and 0 <= self.width - 1 - dx < self.width:
                    self.nodes[self.height - 1 - dy][self.width - 1 - dx].walkable = True
        
        self._connect_neighbors()
        return self.nodes
    
    def _connect_neighbors(self) -> None:
        """Connect all nodes to their neighbors."""
        # 4-way directions
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        # Add diagonals for 8-way
        if self.eight_connected:
            directions.extend([(-1, -1), (1, -1), (1, 1), (-1, 1)])
        
        for y in range(self.height):
            for x in range(self.width):
                node = self.nodes[y][x]
                
                if not node.walkable:
                    continue
                
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    
                    if (0 <= nx < self.width and 0 <= ny < self.height):
                        neighbor = self.nodes[ny][nx]
                        if neighbor.walkable:
                            node.add_neighbor(neighbor)

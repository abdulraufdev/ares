"""Rendering and visualization."""
import pygame
import math
from config import *
from core.grid import Grid
from core.models import Agent, Stats

class Renderer:
    """Handles all drawing operations."""
    
    def __init__(self, screen: pygame.Surface, grid: Grid):
        """Initialize renderer."""
        self.screen = screen
        self.grid = grid
        self.font = pygame.font.SysFont('Consolas', 14)
        self.font_large = pygame.font.SysFont('Consolas', 16)
        self.font_small = pygame.font.SysFont('Consolas', 10)
        
        # Node colors
        self.COLOR_NODE_DEFAULT = (180, 180, 180)
        self.COLOR_NODE_PLAYER = (100, 150, 255)
        self.COLOR_NODE_ENEMY = (255, 100, 100)
        self.COLOR_NODE_TARGET = (100, 255, 150)
        self.COLOR_NODE_BLOCKED = (60, 60, 70)
        self.COLOR_EDGE_DEFAULT = (80, 80, 90)
        self.COLOR_EDGE_HEAVY = (120, 120, 140)
    
    def draw_grid(self) -> None:
        """Draw the grid and obstacles."""
        self.screen.fill(COLOR_BACKGROUND)
        
        # Draw cells (lighter background for walkable areas)
        for y in range(self.grid.h):
            for x in range(self.grid.w):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                if self.grid.blocked[y][x]:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)
                
                # Draw grid lines (very subtle)
                pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect, 1)
    
    def draw_graph_nodes(self, player_pos: tuple[int, int], enemy_pos: tuple[int, int], 
                        player_target: tuple[int, int] | None = None):
        """Draw visible nodes as circles (metro map style)."""
        node_radius = 8
        
        # First pass: draw edges between nodes
        for y in range(self.grid.h):
            for x in range(self.grid.w):
                if self.grid.blocked[y][x]:
                    continue
                
                current_pos = (x, y)
                center = self.grid_to_screen(current_pos)
                
                # Draw edges to neighbors
                for neighbor_pos in self.grid.neighbors(current_pos):
                    neighbor_center = self.grid_to_screen(neighbor_pos)
                    
                    # Calculate edge weight/cost
                    cost = self.grid.step_cost(current_pos, neighbor_pos)
                    edge_color = self.get_edge_color(cost)
                    edge_width = 1 if cost < 1.2 else 2
                    
                    pygame.draw.line(self.screen, edge_color, center, neighbor_center, edge_width)
        
        # Second pass: draw nodes on top of edges
        for y in range(self.grid.h):
            for x in range(self.grid.w):
                if self.grid.blocked[y][x]:
                    continue
                
                pos = (x, y)
                center = self.grid_to_screen(pos)
                color = self.get_node_color(pos, player_pos, enemy_pos, player_target)
                
                # Draw node circle
                pygame.draw.circle(self.screen, color, center, node_radius)
                
                # Add glow effect for player and enemy
                if pos == player_pos:
                    pygame.draw.circle(self.screen, (150, 200, 255), center, node_radius + 3, 2)
                elif pos == enemy_pos:
                    pygame.draw.circle(self.screen, (255, 150, 150), center, node_radius + 3, 2)
                
                # Add outline for target node
                if player_target and pos == player_target:
                    pygame.draw.circle(self.screen, (100, 255, 150), center, node_radius + 2, 3)
    
    def grid_to_screen(self, pos: tuple[int, int]) -> tuple[int, int]:
        """Convert grid position to screen coordinates (center of cell)."""
        x, y = pos
        return (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2)
    
    def get_node_color(self, pos: tuple[int, int], player_pos: tuple[int, int], 
                      enemy_pos: tuple[int, int], player_target: tuple[int, int] | None) -> tuple[int, int, int]:
        """Determine node color based on state."""
        if pos == player_pos:
            return self.COLOR_NODE_PLAYER
        elif pos == enemy_pos:
            return self.COLOR_NODE_ENEMY
        elif player_target and pos == player_target:
            return self.COLOR_NODE_TARGET
        else:
            return self.COLOR_NODE_DEFAULT
    
    def get_edge_color(self, cost: float) -> tuple[int, int, int]:
        """Determine edge color based on weight/cost."""
        if cost > 1.2:  # Diagonal or weighted
            return self.COLOR_EDGE_HEAVY
        return self.COLOR_EDGE_DEFAULT
    
    def draw_path(self, path: list[tuple[int, int]]) -> None:
        """Draw the computed path."""
        if len(path) < 2:
            return
        
        points = [(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2) 
                  for x, y in path]
        pygame.draw.lines(self.screen, COLOR_PATH, False, points, 3)
    
    def draw_agents(self, player: Agent, enemy: Agent) -> None:
        """Draw player and enemy agents."""
        # Draw player
        px, py = player.pos
        player_rect = pygame.Rect(px * CELL_SIZE + 4, py * CELL_SIZE + 4, 
                                   CELL_SIZE - 8, CELL_SIZE - 8)
        pygame.draw.rect(self.screen, COLOR_PLAYER, player_rect)
        
        # Draw enemy
        ex, ey = enemy.pos
        enemy_rect = pygame.Rect(ex * CELL_SIZE + 4, ey * CELL_SIZE + 4, 
                                  CELL_SIZE - 8, CELL_SIZE - 8)
        pygame.draw.rect(self.screen, COLOR_ENEMY, enemy_rect)
    
    def draw_labels(self, algo: str, stats: Stats, paused: bool, 
                   game_time_ms: int = 0, current_path_cost: float = 0.0, 
                   path_length: int = 0) -> None:
        """Draw HUD with controls and metrics."""
        # Background box
        hud_rect = pygame.Rect(10, 10, 550, 140)
        pygame.draw.rect(self.screen, COLOR_HUD_BG, hud_rect)
        pygame.draw.rect(self.screen, COLOR_TEXT, hud_rect, 1)
        
        y_offset = 20
        
        # Title
        title_text = self.font_large.render(f"Algorithm Arena - {algo}", True, COLOR_TEXT)
        self.screen.blit(title_text, (20, y_offset))
        y_offset += 22
        
        # Algorithm description
        algo_desc = self.get_algo_description(algo)
        desc_text = self.font.render(algo_desc, True, (180, 180, 200))
        self.screen.blit(desc_text, (20, y_offset))
        y_offset += 20
        
        # Controls
        controls = "1=BFS 2=DFS 3=UCS 4=Greedy 5=A* | SPACE=Pause | Click=Move"
        controls_text = self.font.render(controls, True, COLOR_TEXT)
        self.screen.blit(controls_text, (20, y_offset))
        y_offset += 20
        
        # Live metrics
        time_sec = game_time_ms // 1000
        time_str = f"{time_sec // 60:02d}:{time_sec % 60:02d}"
        
        metrics = f"Time: {time_str} | Path Cost: {current_path_cost:.1f} | Path Length: {path_length} nodes"
        metrics_text = self.font.render(metrics, True, (100, 255, 150))
        self.screen.blit(metrics_text, (20, y_offset))
        y_offset += 20
        
        # Algorithm stats
        algo_stats = f"Nodes Explored: {stats.nodes_expanded} | Compute Time: {stats.compute_ms:.2f}ms"
        stats_text = self.font.render(algo_stats, True, (150, 200, 255))
        self.screen.blit(stats_text, (20, y_offset))
        
        # Pause indicator
        if paused:
            pause_text = self.font_large.render("PAUSED", True, (255, 255, 0))
            self.screen.blit(pause_text, (WINDOW_WIDTH - 100, 20))
    
    def get_algo_description(self, algo: str) -> str:
        """Get description for algorithm."""
        descriptions = {
            'BFS': 'Breadth-First Search - explores all neighbors equally',
            'DFS': 'Depth-First Search - explores one path deeply first',
            'UCS': 'Uniform Cost Search - finds lowest cost path',
            'Greedy': 'Greedy Best-First - rushes toward target',
            'A*': 'A* Algorithm - optimal with heuristic guidance'
        }
        return descriptions.get(algo, '')

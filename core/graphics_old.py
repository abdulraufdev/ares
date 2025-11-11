"""Rendering and visualization."""
import pygame
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
    
    def draw_grid(self) -> None:
        """Draw the grid and obstacles."""
        self.screen.fill(COLOR_BACKGROUND)
        
        # Draw cells
        for y in range(self.grid.h):
            for x in range(self.grid.w):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                if self.grid.blocked[y][x]:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)
                
                # Draw grid lines
                pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect, 1)
    
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
    
    def draw_labels(self, algo: str, stats: Stats, paused: bool) -> None:
        """Draw HUD with controls and metrics."""
        # Background box
        hud_rect = pygame.Rect(10, 10, 450, 80)
        pygame.draw.rect(self.screen, COLOR_HUD_BG, hud_rect)
        pygame.draw.rect(self.screen, COLOR_TEXT, hud_rect, 1)
        
        # Title
        title_text = self.font_large.render(f"Project ARES - Algorithm: {algo}", True, COLOR_TEXT)
        self.screen.blit(title_text, (20, 20))
        
        # Controls
        controls = "1=BFS  2=DFS  3=UCS  4=Greedy  5=A*  |  SPACE=Pause  M=Map"
        controls_text = self.font.render(controls, True, COLOR_TEXT)
        self.screen.blit(controls_text, (20, 42))
        
        # Metrics
        metrics = f"Nodes: {stats.nodes_expanded}  Time: {stats.compute_ms:.2f}ms  Path Len: {stats.path_len}"
        metrics_text = self.font.render(metrics, True, COLOR_TEXT)
        self.screen.blit(metrics_text, (20, 62))
        
        # Pause indicator
        if paused:
            pause_text = self.font_large.render("PAUSED", True, (255, 255, 0))
            self.screen.blit(pause_text, (WINDOW_WIDTH - 100, 20))

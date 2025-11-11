"""Rendering and visualization."""
import pygame
from typing import Optional
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
        self.font_small = pygame.font.SysFont('Consolas', 12)
        
        # Tooltip state
        self.tooltip_visible = False
        self.tooltip_content: list[str] = []
        self.tooltip_pos = (0, 0)
    
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
    
    def draw_agents(self, player: Agent, enemy: Agent, current_time: float) -> None:
        """Draw player and enemy agents with animation support."""
        # Draw player
        if player.in_transit:
            px, py = player.movement_segment.get_interpolated_pos(current_time)
        else:
            px, py = player.pos
        
        player_rect = pygame.Rect(
            int(px * CELL_SIZE + 4), 
            int(py * CELL_SIZE + 4), 
            CELL_SIZE - 8, 
            CELL_SIZE - 8
        )
        pygame.draw.rect(self.screen, COLOR_PLAYER, player_rect)
        
        # Draw enemy
        if enemy.in_transit:
            ex, ey = enemy.movement_segment.get_interpolated_pos(current_time)
        else:
            ex, ey = enemy.pos
        
        enemy_rect = pygame.Rect(
            int(ex * CELL_SIZE + 4), 
            int(ey * CELL_SIZE + 4), 
            CELL_SIZE - 8, 
            CELL_SIZE - 8
        )
        pygame.draw.rect(self.screen, COLOR_ENEMY, enemy_rect)
    
    def draw_pause_indicator(self, paused: bool) -> None:
        """Draw pause indicator if paused."""
        if paused:
            pause_text = self.font_large.render("PAUSED", True, (255, 255, 0))
            self.screen.blit(pause_text, (WINDOW_WIDTH - 100, 20))
    
    def set_tooltip(self, content: list[str], mouse_pos: tuple[int, int]) -> None:
        """Set tooltip content and position."""
        self.tooltip_visible = True
        self.tooltip_content = content
        # Offset tooltip from mouse
        self.tooltip_pos = (mouse_pos[0] + 15, mouse_pos[1] + 15)
    
    def hide_tooltip(self) -> None:
        """Hide the tooltip."""
        self.tooltip_visible = False
    
    def draw_tooltip(self) -> None:
        """Draw the tooltip if visible."""
        if not self.tooltip_visible or not self.tooltip_content:
            return
        
        # Calculate tooltip size
        padding = 8
        line_height = 16
        max_width = max(self.font_small.size(line)[0] for line in self.tooltip_content) if self.tooltip_content else 100
        tooltip_width = max_width + padding * 2
        tooltip_height = len(self.tooltip_content) * line_height + padding * 2
        
        # Ensure tooltip stays on screen
        x, y = self.tooltip_pos
        if x + tooltip_width > WINDOW_WIDTH:
            x = WINDOW_WIDTH - tooltip_width - 5
        if y + tooltip_height > WINDOW_HEIGHT:
            y = WINDOW_HEIGHT - tooltip_height - 5
        
        # Draw background
        tooltip_rect = pygame.Rect(x, y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, (40, 40, 50), tooltip_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), tooltip_rect, 1)
        
        # Draw text lines
        for i, line in enumerate(self.tooltip_content):
            text_surface = self.font_small.render(line, True, COLOR_TEXT)
            self.screen.blit(text_surface, (x + padding, y + padding + i * line_height))
    
    def draw_victory_screen(self, stats: Stats, algo: str) -> None:
        """Draw victory screen with comprehensive stats."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 30))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_large.render("VICTORY!", True, (100, 255, 100))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Stats
        y_offset = 150
        stats_lines = self._format_stats_for_screen(stats, algo, victory=True)
        for line in stats_lines:
            text = self.font.render(line, True, COLOR_TEXT)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 25
    
    def draw_defeat_screen(self, stats: Stats, algo: str, reason: str) -> None:
        """Draw defeat screen with comprehensive stats."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 30))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_large.render("DEFEAT!", True, (255, 100, 100))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Reason
        reason_text = self.font.render(f"Reason: {reason}", True, (255, 255, 100))
        reason_rect = reason_text.get_rect(center=(WINDOW_WIDTH // 2, 130))
        self.screen.blit(reason_text, reason_rect)
        
        # Stats
        y_offset = 170
        stats_lines = self._format_stats_for_screen(stats, algo, victory=False)
        for line in stats_lines:
            text = self.font.render(line, True, COLOR_TEXT)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 25
    
    def _format_stats_for_screen(self, stats: Stats, algo: str, victory: bool) -> list[str]:
        """Format stats based on algorithm type."""
        lines = [f"Algorithm: {algo}"]
        
        # Common stats
        lines.append(f"Path Length: {stats.path_len}")
        lines.append(f"Distance Traveled: {stats.distance_traveled:.1f}")
        
        # Algorithm-specific stats
        if algo in ['UCS', 'A*']:
            lines.append(f"Path Cost: {stats.path_cost:.2f}")
            lines.append(f"Cost Traveled: {stats.cost_traveled:.2f}")
        
        if algo == 'A*':
            lines.append(f"Nodes Explored (Player): {stats.nodes_expanded}")
        
        lines.append(f"Enemy Nodes Explored: {stats.enemy_nodes_explored}")
        lines.append(f"Enemy Recalculations: {stats.enemy_path_recalculations}")
        
        if stats.max_frontier_size > 0:
            lines.append(f"Max Frontier Size: {stats.max_frontier_size}")
        
        # Abilities used
        if stats.abilities_used:
            lines.append("Abilities Used:")
            for ability, count in stats.abilities_used.items():
                lines.append(f"  {ability}: {count}")
        
        return lines

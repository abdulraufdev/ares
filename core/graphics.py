"""Rendering and visualization with modern UI."""
import pygame
import math
from typing import Optional
from config import *
from core.arena import Arena
from core.models import Agent, Stats

class Renderer:
    """Handles all drawing operations with modern visual style."""
    
    def __init__(self, screen: pygame.Surface, arena: Arena):
        """Initialize renderer."""
        self.screen = screen
        self.arena = arena
        self.font = pygame.font.SysFont('Segoe UI', 14)
        self.font_medium = pygame.font.SysFont('Segoe UI', 16)
        self.font_large = pygame.font.SysFont('Segoe UI', 24, bold=True)
        self.font_title = pygame.font.SysFont('Segoe UI', 32, bold=True)
        
        # Tooltip state
        self.tooltip_visible = False
        self.tooltip_content: list[str] = []
        self.tooltip_pos = (0, 0)
        
        # Animation state
        self.pulse_offset = 0
    
    def draw_arena(self, current_time: float) -> None:
        """Draw the arena background and edges."""
        self.screen.fill(COLOR_BACKGROUND)
        
        # Draw edges first (so they appear behind nodes)
        for node_id, edges in self.arena.edges.items():
            if node_id in self.arena.blocked:
                continue
            
            pos1 = self.arena.get_node_position(node_id)
            for neighbor_id, weight in edges:
                if neighbor_id in self.arena.blocked:
                    continue
                
                pos2 = self.arena.get_node_position(neighbor_id)
                
                # Draw edge with anti-aliasing
                color = COLOR_EDGE
                pygame.draw.line(self.screen, color, pos1, pos2, 2)
    
    def draw_nodes(self) -> None:
        """Draw all nodes in the arena."""
        for node_id, pos in self.arena.nodes.items():
            if node_id in self.arena.blocked:
                # Draw blocked nodes differently
                pygame.draw.circle(self.screen, COLOR_WALL, (int(pos[0]), int(pos[1])), NODE_RADIUS)
                pygame.draw.circle(self.screen, COLOR_NODE_BORDER, (int(pos[0]), int(pos[1])), NODE_RADIUS, 2)
            else:
                # Draw regular nodes
                pygame.draw.circle(self.screen, COLOR_NODE, (int(pos[0]), int(pos[1])), NODE_RADIUS)
                pygame.draw.circle(self.screen, COLOR_NODE_BORDER, (int(pos[0]), int(pos[1])), NODE_RADIUS, 2)
    
    def draw_goal(self, goal_node: int, current_time: float) -> None:
        """Draw the goal node with pulsing effect."""
        pos = self.arena.get_node_position(goal_node)
        
        # Pulsing effect
        pulse = math.sin(current_time * 0.003) * 3 + 3
        inner_radius = NODE_RADIUS + int(pulse)
        outer_radius = inner_radius + 6
        
        # Outer glow
        pygame.draw.circle(self.screen, COLOR_GOAL_GLOW, (int(pos[0]), int(pos[1])), outer_radius)
        # Inner circle
        pygame.draw.circle(self.screen, COLOR_GOAL, (int(pos[0]), int(pos[1])), inner_radius)
        # Star effect - draw a small star in center
        center_x, center_y = int(pos[0]), int(pos[1])
        star_size = 6
        points = []
        for i in range(8):
            angle = i * math.pi / 4
            r = star_size if i % 2 == 0 else star_size / 2
            px = center_x + int(r * math.cos(angle))
            py = center_y + int(r * math.sin(angle))
            points.append((px, py))
        pygame.draw.polygon(self.screen, (255, 255, 220), points)
    
    def draw_path(self, path: list[int]) -> None:
        """Draw the computed path."""
        if len(path) < 2:
            return
        
        for i in range(len(path) - 1):
            pos1 = self.arena.get_node_position(path[i])
            pos2 = self.arena.get_node_position(path[i + 1])
            
            # Draw thick glowing line
            pygame.draw.line(self.screen, COLOR_PATH, pos1, pos2, 4)
    
    def draw_agents(self, player: Agent, enemy: Agent, current_time: float) -> None:
        """Draw player and enemy agents with modern style."""
        # Draw player
        if player.in_transit:
            px, py = player.movement_segment.get_interpolated_pos(current_time, self.arena)
        else:
            px, py = self.arena.get_node_position(player.pos)
        
        # Player glow
        pygame.draw.circle(self.screen, COLOR_PLAYER_GLOW, (int(px), int(py)), NODE_RADIUS + 8)
        # Player body
        pygame.draw.circle(self.screen, COLOR_PLAYER, (int(px), int(py)), NODE_RADIUS)
        # Player highlight
        pygame.draw.circle(self.screen, (150, 220, 255), (int(px) - 5, int(py) - 5), NODE_RADIUS // 3)
        
        # Draw enemy
        if enemy.in_transit:
            ex, ey = enemy.movement_segment.get_interpolated_pos(current_time, self.arena)
        else:
            ex, ey = self.arena.get_node_position(enemy.pos)
        
        # Enemy glow
        pygame.draw.circle(self.screen, COLOR_ENEMY_GLOW, (int(ex), int(ey)), NODE_RADIUS + 8)
        # Enemy body
        pygame.draw.circle(self.screen, COLOR_ENEMY, (int(ex), int(ey)), NODE_RADIUS)
        # Enemy highlight
        pygame.draw.circle(self.screen, (255, 120, 140), (int(ex) - 5, int(ey) - 5), NODE_RADIUS // 3)
    
    def draw_pause_indicator(self, paused: bool) -> None:
        """Draw modern pause overlay."""
        if paused:
            # Semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))
            
            # Pause text with modern styling
            pause_text = self.font_title.render("PAUSED", True, COLOR_TEXT_HIGHLIGHT)
            pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            
            # Background for text
            bg_rect = pause_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, (25, 28, 40, 220), bg_rect, border_radius=10)
            pygame.draw.rect(self.screen, COLOR_TEXT_HIGHLIGHT, bg_rect, 2, border_radius=10)
            
            self.screen.blit(pause_text, pause_rect)
    
    def set_tooltip(self, content: list[str], mouse_pos: tuple[int, int]) -> None:
        """Set tooltip content and position."""
        self.tooltip_visible = True
        self.tooltip_content = content
        # Offset tooltip from mouse
        self.tooltip_pos = (mouse_pos[0] + 20, mouse_pos[1] + 20)
    
    def hide_tooltip(self) -> None:
        """Hide the tooltip."""
        self.tooltip_visible = False
    
    def draw_tooltip(self) -> None:
        """Draw modern styled tooltip."""
        if not self.tooltip_visible or not self.tooltip_content:
            return
        
        # Calculate tooltip size
        padding = 12
        line_height = 20
        max_width = max(self.font.size(line)[0] for line in self.tooltip_content) if self.tooltip_content else 100
        tooltip_width = max_width + padding * 2
        tooltip_height = len(self.tooltip_content) * line_height + padding * 2
        
        # Ensure tooltip stays on screen
        x, y = self.tooltip_pos
        if x + tooltip_width > WINDOW_WIDTH:
            x = WINDOW_WIDTH - tooltip_width - 10
        if y + tooltip_height > WINDOW_HEIGHT:
            y = WINDOW_HEIGHT - tooltip_height - 10
        
        # Draw modern tooltip with shadow
        shadow_rect = pygame.Rect(x + 3, y + 3, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=8)
        
        # Main tooltip background
        tooltip_rect = pygame.Rect(x, y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, (35, 40, 55), tooltip_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_TEXT_HIGHLIGHT, tooltip_rect, 2, border_radius=8)
        
        # Draw text lines
        for i, line in enumerate(self.tooltip_content):
            color = COLOR_TEXT if i > 0 else COLOR_TEXT_HIGHLIGHT
            text_surface = self.font.render(line, True, color)
            self.screen.blit(text_surface, (x + padding, y + padding + i * line_height))
    
    def draw_victory_screen(self, stats: Stats, algo: str) -> None:
        """Draw modern victory screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Victory panel
        panel_width = 600
        panel_height = 500
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        # Panel background with gradient effect
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (30, 35, 50), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100, 255, 150), panel_rect, 3, border_radius=15)
        
        # Title
        title = self.font_title.render("VICTORY!", True, (100, 255, 150))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 60))
        self.screen.blit(title, title_rect)
        
        # Stats
        y_offset = panel_y + 130
        stats_lines = self._format_stats_for_screen(stats, algo, victory=True)
        for line in stats_lines:
            text = self.font_medium.render(line, True, COLOR_TEXT)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 28
        
        # Footer
        footer = self.font.render("Press SPACE to return to menu", True, COLOR_TEXT_DIM)
        footer_rect = footer.get_rect(center=(WINDOW_WIDTH // 2, panel_y + panel_height - 40))
        self.screen.blit(footer, footer_rect)
    
    def draw_defeat_screen(self, stats: Stats, algo: str, reason: str) -> None:
        """Draw modern defeat screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Defeat panel
        panel_width = 600
        panel_height = 500
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (30, 35, 50), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 100, 100), panel_rect, 3, border_radius=15)
        
        # Title
        title = self.font_title.render("DEFEAT", True, (255, 100, 100))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 60))
        self.screen.blit(title, title_rect)
        
        # Reason
        reason_text = self.font_medium.render(reason, True, (255, 200, 100))
        reason_rect = reason_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 100))
        self.screen.blit(reason_text, reason_rect)
        
        # Stats
        y_offset = panel_y + 150
        stats_lines = self._format_stats_for_screen(stats, algo, victory=False)
        for line in stats_lines:
            text = self.font_medium.render(line, True, COLOR_TEXT)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 28
        
        # Footer
        footer = self.font.render("Press SPACE to return to menu", True, COLOR_TEXT_DIM)
        footer_rect = footer.get_rect(center=(WINDOW_WIDTH // 2, panel_y + panel_height - 40))
        self.screen.blit(footer, footer_rect)
    
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

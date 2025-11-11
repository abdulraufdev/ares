"""Rendering and visualization."""
import pygame
from typing import Optional
from config import *
from core.grid import Grid
from core.models import Agent, Stats
from core.node import Node
from core.themes import ThemeManager
from core.particles import ParticleSystem

class Renderer:
    """Handles all drawing operations."""
    
    def __init__(self, screen: pygame.Surface, grid: Grid, theme_manager: Optional[ThemeManager] = None):
        """Initialize renderer."""
        self.screen = screen
        self.grid = grid
        self.font = pygame.font.SysFont('Consolas', 14)
        self.font_large = pygame.font.SysFont('Consolas', 16)
        self.font_small = pygame.font.SysFont('Consolas', 10)
        self.theme_manager = theme_manager or ThemeManager()
        self.particle_system = ParticleSystem()
        self.nodes: Optional[list[list[Node]]] = None
    
    def draw_grid(self, algo: Optional[str] = None) -> None:
        """Draw the grid and obstacles with theme colors."""
        # Use theme background if available
        if algo and algo in ALGORITHM_THEMES:
            bg_color = self.theme_manager.get_color('background', algo)
            self.screen.fill(bg_color)
        else:
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
        
        # Draw node weights if nodes are available
        if self.nodes:
            self.draw_node_weights()
    
    def draw_node_weights(self) -> None:
        """Draw weights on weighted terrain nodes."""
        if not self.nodes:
            return
        
        for row in self.nodes:
            for node in row:
                if node.walkable and node.weight > 1.0:
                    x_px = node.x * CELL_SIZE + CELL_SIZE // 2
                    y_px = node.y * CELL_SIZE + CELL_SIZE // 2
                    
                    # Draw weight value
                    weight_text = self.font_small.render(str(int(node.weight)), True, (200, 200, 200))
                    text_rect = weight_text.get_rect(center=(x_px, y_px))
                    self.screen.blit(weight_text, text_rect)
    
    def draw_node_states(self, algo: Optional[str] = None) -> None:
        """Draw open and closed node states for visualization."""
        if not self.nodes:
            return
        
        for row in self.nodes:
            for node in row:
                if not node.walkable:
                    continue
                
                rect = pygame.Rect(node.x * CELL_SIZE, node.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                # Draw closed nodes
                if node.in_closed_list:
                    color = self.theme_manager.get_color('closed', algo)
                    pygame.draw.rect(self.screen, color, rect)
                
                # Draw open nodes
                elif node.in_open_list:
                    color = self.theme_manager.get_color('open', algo)
                    pygame.draw.rect(self.screen, color, rect)
    
    def draw_path(self, path: list[tuple[int, int]], algo: Optional[str] = None) -> None:
        """Draw the computed path with theme colors."""
        if len(path) < 2:
            return
        
        # Get path color from theme
        if algo and algo in ALGORITHM_THEMES:
            path_color = self.theme_manager.get_color('path', algo)
        else:
            path_color = COLOR_PATH
        
        points = [(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2) 
                  for x, y in path]
        pygame.draw.lines(self.screen, path_color, False, points, 3)
    
    def draw_agents(self, player: Agent, enemy: Agent) -> None:
        """Draw player and enemy agents with health bars."""
        # Draw player
        px, py = player.pos
        player_rect = pygame.Rect(px * CELL_SIZE + 4, py * CELL_SIZE + 4, 
                                   CELL_SIZE - 8, CELL_SIZE - 8)
        
        # Shield effect
        if player.shield_active:
            # Draw shield glow
            shield_rect = pygame.Rect(px * CELL_SIZE + 2, py * CELL_SIZE + 2,
                                     CELL_SIZE - 4, CELL_SIZE - 4)
            pygame.draw.rect(self.screen, (100, 200, 255), shield_rect, 2)
        
        pygame.draw.rect(self.screen, COLOR_PLAYER, player_rect)
        
        # Draw player health bar
        self.draw_health_bar(px, py, player.hp, player.max_hp, COLOR_PLAYER)
        
        # Draw enemy
        ex, ey = enemy.pos
        enemy_rect = pygame.Rect(ex * CELL_SIZE + 4, ey * CELL_SIZE + 4, 
                                  CELL_SIZE - 8, CELL_SIZE - 8)
        pygame.draw.rect(self.screen, COLOR_ENEMY, enemy_rect)
        
        # Draw enemy health bar
        self.draw_health_bar(ex, ey, enemy.hp, enemy.max_hp, COLOR_ENEMY)
    
    def draw_health_bar(self, x: int, y: int, hp: float, max_hp: float, 
                       color: tuple[int, int, int]) -> None:
        """Draw health bar above agent."""
        bar_width = CELL_SIZE - 4
        bar_height = 4
        bar_x = x * CELL_SIZE + 2
        bar_y = y * CELL_SIZE - 6
        
        # Background (red)
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (100, 0, 0), bg_rect)
        
        # Health (colored)
        if max_hp > 0:
            health_width = int(bar_width * (hp / max_hp))
            health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
            
            # Color gradient based on health
            if hp / max_hp > 0.5:
                health_color = (0, 200, 0)
            elif hp / max_hp > 0.25:
                health_color = (200, 200, 0)
            else:
                health_color = (200, 0, 0)
            
            pygame.draw.rect(self.screen, health_color, health_rect)
        
        # Border
        pygame.draw.rect(self.screen, (200, 200, 200), bg_rect, 1)
    
    def draw_labels(self, algo: str, stats: Stats, paused: bool, 
                   player: Optional[Agent] = None, enemy: Optional[Agent] = None) -> None:
        """Draw HUD with controls, metrics, and health."""
        # Background box
        hud_rect = pygame.Rect(10, 10, 600, 100)
        pygame.draw.rect(self.screen, COLOR_HUD_BG, hud_rect)
        pygame.draw.rect(self.screen, COLOR_TEXT, hud_rect, 1)
        
        # Title with theme name
        theme_name = self.theme_manager.get_name(algo)
        title_text = self.font_large.render(f"ARES - {algo} ({theme_name})", True, COLOR_TEXT)
        self.screen.blit(title_text, (20, 20))
        
        # Controls
        controls = "1=BFS  2=DFS  3=UCS  4=Greedy  5=A*  |  SPACE=Pause"
        controls_text = self.font.render(controls, True, COLOR_TEXT)
        self.screen.blit(controls_text, (20, 42))
        
        # Abilities
        abilities = "Q=Shield  W=Teleport  E=Block  R=Weight  |  Click=Move"
        abilities_text = self.font.render(abilities, True, COLOR_TEXT)
        self.screen.blit(abilities_text, (20, 60))
        
        # Metrics
        metrics = f"Nodes: {stats.nodes_expanded}  Time: {stats.compute_ms:.2f}ms  Path: {stats.path_len}"
        if stats.path_cost > 0:
            metrics += f"  Cost: {stats.path_cost:.1f}"
        metrics_text = self.font.render(metrics, True, COLOR_TEXT)
        self.screen.blit(metrics_text, (20, 80))
        
        # Health display in HUD
        if player and enemy:
            health_y = 95
            player_hp_text = f"Player HP: {int(player.hp)}/{int(player.max_hp)}"
            enemy_hp_text = f"Enemy HP: {int(enemy.hp)}/{int(enemy.max_hp)}"
            
            player_text = self.font.render(player_hp_text, True, COLOR_PLAYER)
            enemy_text = self.font.render(enemy_hp_text, True, COLOR_ENEMY)
            
            self.screen.blit(player_text, (WINDOW_WIDTH - 250, 20))
            self.screen.blit(enemy_text, (WINDOW_WIDTH - 250, 42))
        
        # Pause indicator
        if paused:
            pause_text = self.font_large.render("PAUSED", True, (255, 255, 0))
            self.screen.blit(pause_text, (WINDOW_WIDTH - 100, 70))
    
    def draw_ability_cooldowns(self, player: Agent, ability_manager, current_time: float) -> None:
        """Draw ability cooldown indicators."""
        from core.abilities import AbilityManager
        
        if not isinstance(ability_manager, AbilityManager):
            return
        
        # Position for ability UI
        start_x = 10
        start_y = WINDOW_HEIGHT - 80
        
        ability_names = ['shield', 'teleport', 'block', 'weight']
        ability_keys = ['Q', 'W', 'E', 'R']
        
        for i, (ability_name, key) in enumerate(zip(ability_names, ability_keys)):
            x = start_x + i * 70
            y = start_y
            
            # Background box
            box_rect = pygame.Rect(x, y, 60, 60)
            pygame.draw.rect(self.screen, COLOR_HUD_BG, box_rect)
            pygame.draw.rect(self.screen, COLOR_TEXT, box_rect, 1)
            
            # Ability key
            key_text = self.font_large.render(key, True, COLOR_TEXT)
            self.screen.blit(key_text, (x + 5, y + 5))
            
            # Cooldown or uses
            cooldown = ability_manager.get_cooldown_remaining(ability_name, player, current_time)
            uses = ability_manager.get_remaining_uses(ability_name)
            
            if cooldown > 0:
                cd_sec = cooldown / 1000.0
                cd_text = self.font.render(f"{cd_sec:.1f}s", True, (255, 100, 100))
                self.screen.blit(cd_text, (x + 5, y + 35))
            elif uses >= 0:
                uses_text = self.font.render(f"x{uses}", True, (100, 255, 100))
                self.screen.blit(uses_text, (x + 5, y + 35))
            else:
                ready_text = self.font.render("RDY", True, (100, 255, 100))
                self.screen.blit(ready_text, (x + 5, y + 35))
    
    def draw_particles(self, dt: float) -> None:
        """Update and draw particle effects."""
        self.particle_system.update(dt)
        self.particle_system.draw(self.screen)

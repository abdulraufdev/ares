"""Graphics rendering for Algorithm Arena."""
import pygame
import math
from config import *
from core.node import Node
from core.models import Stats


class GraphRenderer:
    """Renders the graph-based game world."""
    
    def __init__(self, screen: pygame.Surface, algorithm: str):
        """Initialize renderer with algorithm theme.
        
        Args:
            screen: Pygame display surface
            algorithm: Algorithm name for theme selection
        """
        self.screen = screen
        self.algorithm = algorithm
        self.theme = THEMES.get(algorithm, THEMES['BFS'])
        
        # Fonts - using modern Segoe UI / fallback to Arial
        try:
            self.font = pygame.font.SysFont('Segoe UI', NODE_LABEL_FONT_SIZE)
            self.small_font = pygame.font.SysFont('Segoe UI', 12)
            self.ui_font = pygame.font.SysFont('Segoe UI', 17)
            self.large_font = pygame.font.SysFont('Segoe UI', 22, bold=True)
        except:
            self.font = pygame.font.SysFont('Arial', NODE_LABEL_FONT_SIZE)
            self.small_font = pygame.font.SysFont('Arial', 12)
            self.ui_font = pygame.font.SysFont('Arial', 17)
            self.large_font = pygame.font.SysFont('Arial', 22, bold=True)
        
        # Tooltip
        self.tooltip_node = None
        self.tooltip_pos = None
    
    def set_theme(self, algorithm: str):
        """Change visual theme based on algorithm."""
        self.algorithm = algorithm
        self.theme = THEMES.get(algorithm, THEMES['BFS'])
    
    def draw_background(self):
        """Draw themed background."""
        self.screen.fill(self.theme['background'])
    
    def draw_edges(self, graph, enemy_path: list[Node] = None):
        """Draw all edges in the graph.
        
        Args:
            graph: Graph object
            enemy_path: List of nodes in enemy's current path (for highlighting)
        """
        # Build set of enemy path edges for quick lookup
        enemy_edges = set()
        if enemy_path and len(enemy_path) > 1:
            for i in range(len(enemy_path) - 1):
                # Add both directions since edges are bidirectional
                enemy_edges.add((enemy_path[i], enemy_path[i + 1]))
                enemy_edges.add((enemy_path[i + 1], enemy_path[i]))
        
        # Draw all edges
        drawn = set()
        for node in graph.nodes:
            for neighbor, weight in node.neighbors:
                # Only draw each edge once
                edge_id = (min(id(node), id(neighbor)), max(id(node), id(neighbor)))
                if edge_id in drawn:
                    continue
                drawn.add(edge_id)
                
                # Check if this is part of enemy path
                is_enemy_path = (node, neighbor) in enemy_edges
                
                # Choose color and width
                if is_enemy_path:
                    color = self.theme['enemy_path']
                    width = ENEMY_PATH_WIDTH
                else:
                    color = self.theme['edge']
                    width = EDGE_WIDTH
                
                # Draw line
                pygame.draw.line(self.screen, color, node.pos, neighbor.pos, width)
                
                # Draw weight label at midpoint
                if not is_enemy_path:  # Don't clutter enemy path
                    mid_x = (node.pos[0] + neighbor.pos[0]) / 2
                    mid_y = (node.pos[1] + neighbor.pos[1]) / 2
                    weight_text = self.small_font.render(str(int(weight)), True, self.theme['text'])
                    weight_rect = weight_text.get_rect(center=(mid_x, mid_y))
                    # Draw background for readability
                    bg_rect = weight_rect.inflate(4, 2)
                    pygame.draw.rect(self.screen, self.theme['background'], bg_rect)
                    self.screen.blit(weight_text, weight_rect)
    
    def draw_nodes(self, graph, player_node: Node, enemy_node: Node):
        """Draw all nodes in the graph.
        
        Args:
            graph: Graph object
            player_node: Current player position
            enemy_node: Current enemy position
        """
        for node in graph.nodes:
            # Determine node color
            if node == player_node:
                color = self.theme['player']
                draw_glow = True
            elif node == enemy_node:
                color = self.theme['enemy']
                draw_glow = True
            elif node.visited:
                color = self.theme['node_visited']
                draw_glow = False
            else:
                color = self.theme['node_default']
                draw_glow = False
            
            # Draw glow effect for player/enemy
            if draw_glow:
                for i in range(3):
                    radius = NODE_RADIUS + (3 - i) * 5
                    alpha = 50 + i * 30
                    glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (*color, alpha), (radius, radius), radius)
                    self.screen.blit(glow_surface, (node.pos[0] - radius, node.pos[1] - radius))
            
            # Draw node circle
            pygame.draw.circle(self.screen, color, node.pos, NODE_RADIUS)
            pygame.draw.circle(self.screen, self.theme['text'], node.pos, NODE_RADIUS, 2)
            
            # Draw label
            label_text = self.font.render(node.label, True, (0, 0, 0))
            label_rect = label_text.get_rect(center=node.pos)
            self.screen.blit(label_text, label_rect)
    
    def draw_health_bars(self, player_node: Node, enemy_node: Node, 
                        player_hp: float, enemy_hp: float):
        """Draw health bars above player and enemy.
        
        Args:
            player_node: Player's current node
            enemy_node: Enemy's current node
            player_hp: Player health percentage (0.0 to 1.0)
            enemy_hp: Enemy health percentage (0.0 to 1.0)
        """
        bar_width = 50
        bar_height = 6
        
        def draw_bar(node, hp_percent, is_player):
            x = node.pos[0] - bar_width / 2
            y = node.pos[1] - NODE_RADIUS - 15
            
            # Background
            pygame.draw.rect(self.screen, (60, 60, 60), (x, y, bar_width, bar_height))
            
            # Health bar
            hp_color = (100, 255, 100) if is_player else (255, 100, 100)
            hp_width = bar_width * hp_percent
            pygame.draw.rect(self.screen, hp_color, (x, y, hp_width, bar_height))
            
            # Border
            pygame.draw.rect(self.screen, (200, 200, 200), (x, y, bar_width, bar_height), 1)
        
        draw_bar(player_node, player_hp, True)
        draw_bar(enemy_node, enemy_hp, False)
    
    def draw_ui_panel(self, stats: Stats, paused: bool, game_time: int):
        """Draw UI panel with game information.
        
        Args:
            stats: Pathfinding statistics (hidden during gameplay)
            paused: Whether game is paused
            game_time: Elapsed game time in seconds
        """
        # Panel background - made smaller since we removed stats
        panel_rect = pygame.Rect(10, 10, 300, 80)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*self.theme['background'], 200), panel_surface.get_rect(), 
                        border_radius=10)
        pygame.draw.rect(panel_surface, self.theme['ui_accent'], panel_surface.get_rect(), 2,
                        border_radius=10)
        self.screen.blit(panel_surface, panel_rect)
        
        # Algorithm name
        y = 20
        algo_text = self.large_font.render(f'Algorithm: {self.algorithm}', True, self.theme['ui_accent'])
        self.screen.blit(algo_text, (20, y))
        y += 30
        
        # Game time
        minutes = game_time // 60
        seconds = game_time % 60
        time_text = self.ui_font.render(f'Time: {minutes:02d}:{seconds:02d}', True, self.theme['text'])
        self.screen.blit(time_text, (20, y))
        
        # Controls hint moved to bottom of screen
        hint = self.small_font.render('SPACE: Pause  |  ESC: Menu  |  Hover: Node Info', 
                                     True, self.theme['text'])
        self.screen.blit(hint, (10, WINDOW_HEIGHT - 25))
        
        # Pause indicator
        if paused:
            pause_text = self.large_font.render('PAUSED', True, (255, 255, 100))
            pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            # Background
            bg_rect = pause_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect, border_radius=8)
            self.screen.blit(pause_text, pause_rect)
    
    def set_tooltip(self, node: Node | None, mouse_pos: tuple[int, int]):
        """Set tooltip for hovering over node.
        
        Args:
            node: Node being hovered, or None
            mouse_pos: Mouse position
        """
        self.tooltip_node = node
        self.tooltip_pos = mouse_pos
    
    def draw_tooltip(self):
        """Draw tooltip if hovering over a node."""
        if not self.tooltip_node or not self.tooltip_pos:
            return
        
        node = self.tooltip_node
        
        # Build tooltip lines - ALWAYS show for every node
        lines = [f"Node {node.label}"]
        
        # Show neighbor count for all nodes
        lines.append(f"Neighbors: {len(node.neighbors)}")
        
        # Add algorithm-specific information - show for all nodes, not just visited
        if self.algorithm in ['BFS', 'DFS']:
            lines.append(f"Visited: {'Yes' if node.visited else 'No'}")
        
        # UCS shows path cost
        if self.algorithm == 'UCS':
            if node.g_cost > 0 or node.visited:
                lines.append(f"Path Cost: {node.g_cost:.1f}")
            else:
                lines.append(f"Path Cost: Not explored")
        
        # Greedy algorithms show heuristic AND path cost
        if 'Greedy' in self.algorithm:
            if node.h_cost > 0:
                lines.append(f"Heuristic: {node.h_cost:.1f}")
            else:
                lines.append(f"Heuristic: Not calculated")
            if node.g_cost > 0 or node.visited:
                lines.append(f"Path Cost: {node.g_cost:.1f}")
            else:
                lines.append(f"Path Cost: Not explored")
        
        # A* shows heuristic, path cost, and f(n)
        if 'A*' in self.algorithm:
            if node.h_cost > 0:
                lines.append(f"Heuristic: {node.h_cost:.1f}")
            else:
                lines.append(f"Heuristic: Not calculated")
            if node.g_cost > 0 or node.visited:
                lines.append(f"Path Cost: {node.g_cost:.1f}")
            else:
                lines.append(f"Path Cost: Not explored")
            if node.f_cost > 0:
                lines.append(f"f(n) = {node.f_cost:.1f}")
            else:
                lines.append(f"f(n) = Not calculated")
        
        # Render tooltip
        padding = TOOLTIP_PADDING
        line_height = 18
        
        # Calculate size
        max_width = max(self.ui_font.size(line)[0] for line in lines)
        tooltip_width = max_width + padding * 2
        tooltip_height = len(lines) * line_height + padding * 2
        
        # Position tooltip (offset from mouse, keep on screen)
        x = self.tooltip_pos[0] + 15
        y = self.tooltip_pos[1] + 15
        
        if x + tooltip_width > WINDOW_WIDTH:
            x = self.tooltip_pos[0] - tooltip_width - 15
        if y + tooltip_height > WINDOW_HEIGHT:
            y = self.tooltip_pos[1] - tooltip_height - 15
        
        # Draw tooltip background
        tooltip_rect = pygame.Rect(x, y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, TOOLTIP_BG, tooltip_rect, border_radius=5)
        pygame.draw.rect(self.screen, TOOLTIP_BORDER, tooltip_rect, 2, border_radius=5)
        
        # Draw text
        text_y = y + padding
        for line in lines:
            text = self.ui_font.render(line, True, TOOLTIP_TEXT)
            self.screen.blit(text, (x + padding, text_y))
            text_y += line_height
    
    def draw_victory_screen(self, player_stats: dict, enemy_stats: dict, game_time: int):
        """Draw victory screen with statistics.
        
        Args:
            player_stats: Dictionary of player statistics
            enemy_stats: Dictionary of enemy statistics
            game_time: Game duration in seconds
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))
        
        # Victory box
        box_width = 500
        box_height = 500
        box_x = WINDOW_WIDTH // 2 - box_width // 2
        box_y = WINDOW_HEIGHT // 2 - box_height // 2
        
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(self.screen, (40, 40, 60), box_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.theme['ui_accent'], box_rect, 3, border_radius=15)
        
        # Title
        y = box_y + 30
        title = pygame.font.SysFont('Arial', 32, bold=True).render('🎉 VICTORY! 🎉', True, (100, 255, 100))
        title_rect = title.get_rect(centerx=WINDOW_WIDTH // 2)
        self.screen.blit(title, (title_rect.x, y))
        y += 50
        
        # Subtitle
        minutes = game_time // 60
        seconds = game_time % 60
        subtitle = self.ui_font.render(f'You outsmarted the {self.algorithm} algorithm!', True, (220, 220, 220))
        time_text = self.ui_font.render(f'Time: {minutes:02d}:{seconds:02d}', True, (220, 220, 220))
        self.screen.blit(subtitle, (box_x + 50, y))
        self.screen.blit(time_text, (box_x + 50, y + 25))
        y += 70
        
        # Player stats
        self._draw_stat_section('PLAYER STATS:', box_x + 50, y, [
            f"Final Position: {player_stats.get('position', 'N/A')}",
            f"Nodes Visited: {player_stats.get('nodes_visited', 0)}",
            f"Final HP: {player_stats.get('hp', 0)}/100"
        ])
        y += 110
        
        # Enemy stats
        self._draw_stat_section('ENEMY STATS:', box_x + 50, y, [
            f"Final Position: {enemy_stats.get('position', 'N/A')}",
            f"Nodes Explored: {enemy_stats.get('nodes_explored', 0)}",
            f"Path Status: {enemy_stats.get('path_status', 'N/A')}"
        ])
        y += 110
        
        # Buttons (will be drawn separately)
    
    def draw_defeat_screen(self, player_stats: dict, enemy_stats: dict, game_time: int):
        """Draw defeat screen with statistics.
        
        Args:
            player_stats: Dictionary of player statistics
            enemy_stats: Dictionary of enemy statistics
            game_time: Game duration in seconds
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))
        
        # Defeat box
        box_width = 500
        box_height = 500
        box_x = WINDOW_WIDTH // 2 - box_width // 2
        box_y = WINDOW_HEIGHT // 2 - box_height // 2
        
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(self.screen, (40, 40, 60), box_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 100, 100), box_rect, 3, border_radius=15)
        
        # Title
        y = box_y + 30
        title = pygame.font.SysFont('Arial', 32, bold=True).render('💀 DEFEAT! 💀', True, (255, 100, 100))
        title_rect = title.get_rect(centerx=WINDOW_WIDTH // 2)
        self.screen.blit(title, (title_rect.x, y))
        y += 50
        
        # Subtitle
        minutes = game_time // 60
        seconds = game_time % 60
        subtitle = self.ui_font.render(f'The {self.algorithm} algorithm caught you!', True, (220, 220, 220))
        time_text = self.ui_font.render(f'Time Survived: {minutes:02d}:{seconds:02d}', True, (220, 220, 220))
        self.screen.blit(subtitle, (box_x + 50, y))
        self.screen.blit(time_text, (box_x + 50, y + 25))
        y += 70
        
        # Player stats
        self._draw_stat_section('PLAYER STATS:', box_x + 50, y, [
            f"Final HP: 0/100",
            f"Final Position: {player_stats.get('position', 'N/A')}",
            f"Nodes Visited: {player_stats.get('nodes_visited', 0)}"
        ])
        y += 110
        
        # Enemy stats
        self._draw_stat_section('ENEMY STATS:', box_x + 50, y, [
            f"Nodes Explored: {enemy_stats.get('nodes_explored', 0)}",
            f"Final Path Cost: {enemy_stats.get('path_cost', 0):.1f}",
            f"Path Length: {enemy_stats.get('path_length', 0)} nodes"
        ])
        y += 110
        
        # Enemy path (if available)
        if enemy_stats.get('path_string'):
            path_label = self.ui_font.render('ENEMY\'S WINNING PATH:', True, (200, 200, 200))
            self.screen.blit(path_label, (box_x + 50, y))
            y += 25
            path_text = self.small_font.render(enemy_stats['path_string'], True, (180, 180, 180))
            self.screen.blit(path_text, (box_x + 50, y))
    
    def _draw_stat_section(self, title: str, x: int, y: int, stats: list[str]):
        """Helper to draw a section of statistics."""
        # Title
        title_text = pygame.font.SysFont('Arial', 18, bold=True).render(title, True, (200, 200, 200))
        self.screen.blit(title_text, (x, y))
        y += 25
        
        # Stats
        for stat in stats:
            stat_text = self.ui_font.render(f"├─ {stat}", True, (180, 180, 180))
            self.screen.blit(stat_text, (x, y))
            y += 22

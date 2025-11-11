"""Rendering and visualization."""
import pygame
import math
from config import *
from core.graph import Graph
from core.models import Agent, Stats


class Renderer:
    """Handles all drawing operations."""
    
    def __init__(self, screen: pygame.Surface, graph: Graph):
        """Initialize renderer."""
        self.screen = screen
        self.graph = graph
        self.font = pygame.font.SysFont('Arial', 12, bold=True)
        self.font_large = pygame.font.SysFont('Arial', 16, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 10)
        self.current_theme = THEMES['BFS']
        self.enemy_path_edges = set()
    
    def set_theme(self, algo: str) -> None:
        """Set the rendering theme based on algorithm."""
        if algo in THEMES:
            self.current_theme = THEMES[algo]
    
    def set_enemy_path(self, path: list[int]) -> None:
        """Set the enemy path for highlighting edges."""
        self.enemy_path_edges = set()
        if len(path) > 1:
            for i in range(len(path) - 1):
                self.enemy_path_edges.add((path[i], path[i + 1]))
                self.enemy_path_edges.add((path[i + 1], path[i]))
    
    def draw_graph(self, visited_nodes: set[int] = None) -> None:
        """Draw the graph with nodes and edges."""
        if visited_nodes is None:
            visited_nodes = set()
        
        # Fill background
        self.screen.fill(self.current_theme['background'])
        
        # Draw edges first (so they appear behind nodes)
        self._draw_edges()
        
        # Draw nodes
        self._draw_nodes(visited_nodes)
    
    def _draw_edges(self) -> None:
        """Draw all edges with weights."""
        drawn = set()
        
        for (from_id, to_id), edge in self.graph.edges.items():
            # Only draw each edge once
            if (from_id, to_id) in drawn or (to_id, from_id) in drawn:
                continue
            drawn.add((from_id, to_id))
            
            from_node = self.graph.nodes[from_id]
            to_node = self.graph.nodes[to_id]
            
            # Check if this edge is in the enemy path
            is_highlighted = (from_id, to_id) in self.enemy_path_edges
            
            if is_highlighted:
                color = self.current_theme['edge_highlight']
                width = 4
            else:
                color = self.current_theme['edge']
                width = 2
            
            # Draw line with anti-aliasing
            pygame.draw.line(
                self.screen, color,
                (int(from_node.x), int(from_node.y)),
                (int(to_node.x), int(to_node.y)),
                width
            )
            
            # Draw weight label in middle of edge
            mid_x = (from_node.x + to_node.x) / 2
            mid_y = (from_node.y + to_node.y) / 2
            
            weight_text = self.font_small.render(str(int(edge.weight)), True, self.current_theme['text'])
            text_rect = weight_text.get_rect(center=(int(mid_x), int(mid_y)))
            
            # Draw small background for weight text
            bg_rect = text_rect.inflate(6, 4)
            pygame.draw.rect(self.screen, self.current_theme['background'], bg_rect)
            pygame.draw.rect(self.screen, color, bg_rect, 1)
            
            self.screen.blit(weight_text, text_rect)
    
    def _draw_nodes(self, visited_nodes: set[int]) -> None:
        """Draw all nodes."""
        for node_id, node in self.graph.nodes.items():
            # Determine if visited
            is_visited = node_id in visited_nodes
            node_color = self.current_theme['node_visited'] if is_visited else self.current_theme['node']
            
            # Draw node circle
            pygame.draw.circle(
                self.screen, node_color,
                (int(node.x), int(node.y)),
                NODE_RADIUS
            )
            
            # Draw node border
            pygame.draw.circle(
                self.screen, self.current_theme['edge'],
                (int(node.x), int(node.y)),
                NODE_RADIUS, 2
            )
            
            # Draw node label
            label_text = self.font.render(node.label, True, self.current_theme['text'])
            label_rect = label_text.get_rect(center=(int(node.x), int(node.y)))
            self.screen.blit(label_text, label_rect)
    
    def draw_agents(self, player: Agent, enemy: Agent) -> None:
        """Draw player and enemy agents on nodes."""
        # Draw player
        if player.pos in self.graph.nodes:
            player_node = self.graph.nodes[player.pos]
            
            # Outer glow effect
            for i in range(3):
                alpha_surface = pygame.Surface((NODE_RADIUS * 2 + 20, NODE_RADIUS * 2 + 20), pygame.SRCALPHA)
                glow_radius = NODE_RADIUS + 10 - i * 3
                glow_color = (*self.current_theme['player'], 100 - i * 30)
                pygame.draw.circle(
                    alpha_surface, glow_color,
                    (NODE_RADIUS + 10, NODE_RADIUS + 10),
                    glow_radius
                )
                self.screen.blit(alpha_surface, 
                               (int(player_node.x) - NODE_RADIUS - 10, 
                                int(player_node.y) - NODE_RADIUS - 10))
            
            # Player circle
            pygame.draw.circle(
                self.screen, self.current_theme['player'],
                (int(player_node.x), int(player_node.y)),
                NODE_RADIUS
            )
            
            # Player border
            pygame.draw.circle(
                self.screen, (255, 255, 255),
                (int(player_node.x), int(player_node.y)),
                NODE_RADIUS, 3
            )
            
            # Player label
            label_text = self.font.render("P", True, (255, 255, 255))
            label_rect = label_text.get_rect(center=(int(player_node.x), int(player_node.y)))
            self.screen.blit(label_text, label_rect)
        
        # Draw enemy
        if enemy.pos in self.graph.nodes:
            enemy_node = self.graph.nodes[enemy.pos]
            
            # Outer glow effect
            for i in range(3):
                alpha_surface = pygame.Surface((NODE_RADIUS * 2 + 20, NODE_RADIUS * 2 + 20), pygame.SRCALPHA)
                glow_radius = NODE_RADIUS + 10 - i * 3
                glow_color = (*self.current_theme['enemy'], 100 - i * 30)
                pygame.draw.circle(
                    alpha_surface, glow_color,
                    (NODE_RADIUS + 10, NODE_RADIUS + 10),
                    glow_radius
                )
                self.screen.blit(alpha_surface, 
                               (int(enemy_node.x) - NODE_RADIUS - 10, 
                                int(enemy_node.y) - NODE_RADIUS - 10))
            
            # Enemy circle
            pygame.draw.circle(
                self.screen, self.current_theme['enemy'],
                (int(enemy_node.x), int(enemy_node.y)),
                NODE_RADIUS
            )
            
            # Enemy border
            pygame.draw.circle(
                self.screen, (255, 255, 255),
                (int(enemy_node.x), int(enemy_node.y)),
                NODE_RADIUS, 3
            )
            
            # Enemy label
            label_text = self.font.render("E", True, (255, 255, 255))
            label_rect = label_text.get_rect(center=(int(enemy_node.x), int(enemy_node.y)))
            self.screen.blit(label_text, label_rect)
    
    def draw_labels(self, algo: str, stats: Stats, paused: bool) -> None:
        """Draw HUD with controls and metrics."""
        # Modern rounded background box with gradient effect
        hud_rect = pygame.Rect(10, 10, 940, 90)
        
        # Draw gradient background
        for i in range(hud_rect.height):
            alpha = 180 - (i * 30 // hud_rect.height)
            color = tuple(min(c + 20, 255) for c in self.current_theme['background'])
            pygame.draw.rect(
                self.screen, color,
                pygame.Rect(hud_rect.x, hud_rect.y + i, hud_rect.width, 1)
            )
        
        # Draw rounded border
        pygame.draw.rect(self.screen, self.current_theme['text'], hud_rect, 2, border_radius=10)
        
        # Title with theme name
        theme_name = self.current_theme['name']
        title_text = self.font_large.render(
            f"Algorithm Arena - {algo} ({theme_name})", 
            True, self.current_theme['text']
        )
        self.screen.blit(title_text, (20, 20))
        
        # Controls
        controls = "1=BFS  2=DFS  3=UCS  4=Greedy  5=A*  |  SPACE=Pause  M=New Map"
        controls_text = self.font.render(controls, True, self.current_theme['text'])
        self.screen.blit(controls_text, (20, 48))
        
        # Metrics
        metrics = f"Nodes Expanded: {stats.nodes_expanded}  |  Time: {stats.compute_ms:.2f}ms  |  Path Length: {stats.path_len}"
        metrics_text = self.font.render(metrics, True, self.current_theme['text'])
        self.screen.blit(metrics_text, (20, 70))
        
        # Pause indicator with modern styling
        if paused:
            pause_rect = pygame.Rect(WINDOW_WIDTH - 150, 15, 130, 30)
            pygame.draw.rect(self.screen, (255, 200, 0), pause_rect, border_radius=8)
            pygame.draw.rect(self.screen, (255, 255, 0), pause_rect, 2, border_radius=8)
            
            pause_text = self.font_large.render("⏸ PAUSED", True, (0, 0, 0))
            text_rect = pause_text.get_rect(center=pause_rect.center)
            self.screen.blit(pause_text, text_rect)


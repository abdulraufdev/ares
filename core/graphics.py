"""Rendering and visualization."""
import pygame
from typing import Optional, Tuple, List
from config import *
from core.grid import Grid
from core.graph import Graph
from core.models import Agent, Stats


class Renderer:
    """Handles all drawing operations."""
    
    def __init__(self, screen: pygame.Surface, grid: Grid = None, graph: Graph = None):
        """Initialize renderer."""
        self.screen = screen
        self.grid = grid
        self.graph = graph
        self.font = pygame.font.SysFont('Consolas', 14)
        self.font_large = pygame.font.SysFont('Consolas', 16)
        self.font_small = pygame.font.SysFont('Consolas', 12)
        self.font_node = pygame.font.SysFont('Consolas', 18, bold=True)
        self.title_font = pygame.font.SysFont('Consolas', 36, bold=True)
        
        # Hover state
        self.hovered_node: Optional[str] = None
        self.tooltip_info: Optional[dict] = None
    
    def set_graph(self, graph: Graph) -> None:
        """Set the graph for rendering."""
        self.graph = graph
    
    def draw_grid(self) -> None:
        """Draw the grid and obstacles (legacy)."""
        if not self.grid:
            return
        
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
    
    def draw_graph(self) -> None:
        """Draw the graph with nodes and edges."""
        if not self.graph:
            return
        
        self.screen.fill(COLOR_BACKGROUND)
        
        # Draw edges first (so they're behind nodes)
        self._draw_edges()
        
        # Draw nodes
        self._draw_nodes()
    
    def _draw_edges(self) -> None:
        """Draw all edges between nodes."""
        if not self.graph:
            return
        
        drawn_edges = set()  # Track drawn edges to avoid duplicates
        
        for label, node in self.graph.nodes.items():
            for neighbor_label, weight in node.edges.items():
                # Create edge key (sort to avoid drawing A->B and B->A)
                edge_key = tuple(sorted([label, neighbor_label]))
                if edge_key in drawn_edges:
                    continue
                drawn_edges.add(edge_key)
                
                # Get node positions
                neighbor = self.graph.get_node(neighbor_label)
                if not neighbor:
                    continue
                
                # Draw edge line
                pygame.draw.line(
                    self.screen,
                    COLOR_EDGE,
                    (int(node.pos[0]), int(node.pos[1])),
                    (int(neighbor.pos[0]), int(neighbor.pos[1])),
                    EDGE_LINE_WIDTH
                )
                
                # Draw weight label at midpoint
                mid_x = (node.pos[0] + neighbor.pos[0]) / 2
                mid_y = (node.pos[1] + neighbor.pos[1]) / 2
                
                weight_text = self.font_small.render(str(int(weight)), True, COLOR_EDGE_WEIGHT)
                weight_rect = weight_text.get_rect(center=(int(mid_x), int(mid_y)))
                
                # Draw background for weight text
                bg_rect = weight_rect.inflate(6, 4)
                pygame.draw.rect(self.screen, COLOR_BACKGROUND, bg_rect)
                pygame.draw.rect(self.screen, COLOR_EDGE_WEIGHT, bg_rect, 1)
                
                self.screen.blit(weight_text, weight_rect)
    
    def _draw_nodes(self) -> None:
        """Draw all nodes."""
        if not self.graph:
            return
        
        for label, node in self.graph.nodes.items():
            # Determine node color based on state
            if not node.walkable:
                color = COLOR_NODE_BLOCKED
            elif node.occupied_by_player:
                color = COLOR_NODE_PLAYER
            elif node.occupied_by_enemy:
                color = COLOR_NODE_ENEMY
            elif node.visited_by_enemy:
                color = COLOR_NODE_VISITED
            elif node.in_open_list:
                color = COLOR_NODE_OPEN
            else:
                color = COLOR_NODE_DEFAULT
            
            # Draw node circle
            pos = (int(node.pos[0]), int(node.pos[1]))
            pygame.draw.circle(self.screen, color, pos, NODE_RADIUS)
            
            # Draw outline
            outline_color = COLOR_NODE_TARGET if node.is_target else COLOR_TEXT
            outline_width = 3 if node.is_target else 2
            pygame.draw.circle(self.screen, outline_color, pos, NODE_RADIUS, outline_width)
            
            # Draw glow for player/enemy
            if node.occupied_by_player:
                pygame.draw.circle(self.screen, COLOR_NODE_PLAYER, pos, NODE_RADIUS + 5, 2)
            elif node.occupied_by_enemy:
                pygame.draw.circle(self.screen, COLOR_NODE_ENEMY, pos, NODE_RADIUS + 5, 2)
            
            # Draw node label
            label_text = self.font_node.render(label, True, COLOR_TEXT)
            label_rect = label_text.get_rect(center=pos)
            self.screen.blit(label_text, label_rect)
    
    def draw_path(self, path: list[tuple[int, int]]) -> None:
        """Draw the computed path (legacy grid version)."""
        if len(path) < 2:
            return
        
        points = [(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2) 
                  for x, y in path]
        pygame.draw.lines(self.screen, COLOR_PATH, False, points, 3)
    
    def draw_graph_path(self, path: List[str]) -> None:
        """Draw the computed path on the graph."""
        if not self.graph or len(path) < 2:
            return
        
        # Convert path to screen positions
        points = []
        for label in path:
            node = self.graph.get_node(label)
            if node:
                points.append((int(node.pos[0]), int(node.pos[1])))
        
        if len(points) >= 2:
            pygame.draw.lines(self.screen, COLOR_PATH, False, points, 3)
    
    def draw_agents(self, player: Agent, enemy: Agent) -> None:
        """Draw player and enemy agents (legacy grid version)."""
        if not self.grid:
            return
        
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
        hud_rect = pygame.Rect(10, 10, 450, 100)
        pygame.draw.rect(self.screen, COLOR_HUD_BG, hud_rect)
        pygame.draw.rect(self.screen, COLOR_TEXT, hud_rect, 1)
        
        # Title
        title_text = self.font_large.render(f"Algorithm Arena - {algo}", True, COLOR_TEXT)
        self.screen.blit(title_text, (20, 20))
        
        # Controls
        controls = "Click adjacent nodes to move  |  SPACE=Pause  ESC=Menu"
        controls_text = self.font.render(controls, True, COLOR_TEXT)
        self.screen.blit(controls_text, (20, 42))
        
        # Metrics (algorithm-specific)
        self._draw_algorithm_metrics(algo, stats, 20, 64)
        
        # Pause indicator
        if paused:
            pause_text = self.font_large.render("PAUSED", True, (255, 255, 0))
            self.screen.blit(pause_text, (WINDOW_WIDTH - 100, 20))
    
    def _draw_algorithm_metrics(self, algo: str, stats: Stats, x: int, y: int) -> None:
        """Draw algorithm-specific metrics."""
        metrics_lines = []
        
        if algo == 'BFS':
            metrics_lines.append(f"Nodes: {stats.nodes_expanded}  Path: {stats.path_len}  Frontier: {stats.frontier_size}")
        
        elif algo == 'DFS':
            metrics_lines.append(f"Nodes: {stats.nodes_expanded}  Path: {stats.path_len}  Stack: {stats.frontier_size}")
        
        elif algo == 'UCS':
            metrics_lines.append(f"Cost: {stats.path_cost:.1f}  Nodes: {stats.nodes_expanded}  Path: {stats.path_len}")
        
        elif algo == 'Greedy':
            metrics_lines.append(f"Nodes: {stats.nodes_expanded}  Path: {stats.path_len}  h={stats.heuristic_value:.1f}")
        
        elif algo == 'A*':
            metrics_lines.append(f"f={stats.f_cost:.1f} (g={stats.g_cost:.1f} + h={stats.h_cost:.1f})  Nodes: {stats.nodes_expanded}")
        
        else:
            metrics_lines.append(f"Nodes: {stats.nodes_expanded}  Path: {stats.path_len}")
        
        for i, line in enumerate(metrics_lines):
            text = self.font.render(line, True, COLOR_TEXT)
            self.screen.blit(text, (x, y + i * 18))
    
    def draw_hover_tooltip(self, node_label: str, algo: str, player_node: str) -> None:
        """Draw hover tooltip for a node."""
        if not self.graph:
            return
        
        node = self.graph.get_node(node_label)
        if not node:
            return
        
        # Calculate tooltip info
        info_lines = [f"Node {node_label}"]
        
        # Distance from player (visual)
        player = self.graph.get_node(player_node)
        if player:
            dist = ((node.pos[0] - player.pos[0])**2 + (node.pos[1] - player.pos[1])**2)**0.5
            info_lines.append(f"Distance: {dist:.1f}")
        
        # Edge weight (if neighbor)
        if node.is_neighbor(player_node):
            weight = node.get_weight(player_node)
            info_lines.append(f"Weight: {weight:.1f}")
        
        # Algorithm-specific info
        if algo in ['UCS', 'A*']:
            if node.is_neighbor(player_node):
                weight = node.get_weight(player_node)
                info_lines.append(f"Edge Cost: {weight:.1f}")
        
        if algo in ['Greedy', 'A*']:
            # Could add heuristic value here
            pass
        
        # Draw tooltip background
        tooltip_width = 180
        tooltip_height = len(info_lines) * 20 + 10
        tooltip_x = int(node.pos[0]) + NODE_RADIUS + 10
        tooltip_y = int(node.pos[1]) - tooltip_height // 2
        
        # Keep tooltip on screen
        tooltip_x = max(5, min(tooltip_x, WINDOW_WIDTH - tooltip_width - 5))
        tooltip_y = max(5, min(tooltip_y, WINDOW_HEIGHT - tooltip_height - 5))
        
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, (40, 40, 50), tooltip_rect)
        pygame.draw.rect(self.screen, COLOR_TEXT, tooltip_rect, 2)
        
        # Draw tooltip text
        for i, line in enumerate(info_lines):
            text = self.font.render(line, True, COLOR_TEXT)
            self.screen.blit(text, (tooltip_x + 5, tooltip_y + 5 + i * 20))
    
    def get_node_at_pos(self, pos: Tuple[int, int]) -> Optional[str]:
        """Get the node label at the given screen position."""
        if not self.graph:
            return None
        
        x, y = pos
        for label, node in self.graph.nodes.items():
            node_x, node_y = int(node.pos[0]), int(node.pos[1])
            dist = ((x - node_x)**2 + (y - node_y)**2)**0.5
            if dist <= NODE_RADIUS:
                return label
        
        return None
    
    def draw_victory_screen(self, algo: str, player: Agent, enemy: Agent, stats: Stats, survival_time: float) -> None:
        """Draw victory screen with detailed stats."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Victory title
        title = self.title_font.render("🎉 VICTORY! 🎉", True, (100, 255, 100))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Victory message
        msg = self.font_large.render(f"You defeated the {algo} algorithm!", True, COLOR_TEXT)
        msg_rect = msg.get_rect(center=(WINDOW_WIDTH // 2, 130))
        self.screen.blit(msg, msg_rect)
        
        # Stats
        y = 180
        stats_lines = [
            f"Time Survived: {self._format_time(survival_time)}",
            "",
            "PLAYER STATS:",
            f"  Final Position: Node {player.node_label}",
            f"  Distance Traveled: {player.total_distance:.1f}",
            f"  Total Path Cost: {player.total_cost:.1f}",
            f"  Nodes Visited: {len(player.visited_nodes)}",
            "",
            "ENEMY STATS:",
            f"  Final Position: Node {enemy.node_label}",
            f"  Nodes Explored: {stats.nodes_expanded}",
            f"  Path Length: {stats.path_len}",
        ]
        
        for line in stats_lines:
            text = self.font.render(line, True, COLOR_TEXT)
            self.screen.blit(text, (200, y))
            y += 22
        
        # Buttons hint
        hint = self.font_large.render("Press ENTER for Main Menu", True, (180, 180, 180))
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(hint, hint_rect)
    
    def draw_defeat_screen(self, algo: str, player: Agent, enemy: Agent, stats: Stats, survival_time: float) -> None:
        """Draw defeat screen with detailed stats."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Defeat title
        title = self.title_font.render("💀 DEFEAT! 💀", True, (255, 100, 100))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Defeat message
        msg = self.font_large.render(f"The {algo} algorithm caught you!", True, COLOR_TEXT)
        msg_rect = msg.get_rect(center=(WINDOW_WIDTH // 2, 130))
        self.screen.blit(msg, msg_rect)
        
        # Stats
        y = 180
        stats_lines = [
            f"Time Survived: {self._format_time(survival_time)}",
            "",
            "PLAYER STATS:",
            f"  Final HP: {player.hp:.0f}/{PLAYER_MAX_HP}",
            f"  Final Position: Node {player.node_label}",
            f"  Distance Traveled: {player.total_distance:.1f}",
            f"  Nodes Visited: {len(player.visited_nodes)}",
            "",
            "ENEMY STATS:",
            f"  Nodes Explored: {stats.nodes_expanded}",
            f"  Final Path Cost: {stats.path_cost:.1f}",
            f"  Path Length: {stats.path_len}",
        ]
        
        for line in stats_lines:
            text = self.font.render(line, True, COLOR_TEXT)
            self.screen.blit(text, (200, y))
            y += 22
        
        # Buttons hint
        hint = self.font_large.render("Press ENTER for Main Menu", True, (180, 180, 180))
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(hint, hint_rect)
    
    def _format_time(self, seconds: float) -> str:
        """Format time in seconds to MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

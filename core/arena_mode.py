"""Algorithm Arena - Interactive gameplay mode where player evades enemy AI."""
import pygame
import random
import time
from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from core.models import Stats
from algorithms import bfs, dfs, ucs, greedy, astar

# Enemy movement speeds per algorithm (milliseconds between moves)
ENEMY_SPEEDS = {
    'BFS': 600,   # Slower
    'DFS': 600,   # Slower
    'UCS': 500,   # Medium
    'Greedy': 400, # Faster - rushes toward goal
    'A*': 500     # Medium - balanced
}

@dataclass
class Node:
    """Represents a node in the arena graph."""
    pos: Tuple[int, int]
    label: str
    neighbors: List['Node'] = field(default_factory=list)
    weights: dict = field(default_factory=dict)  # {neighbor_label: weight}
    blocked: bool = False
    distance: float = float('inf')
    g_cost: float = 0.0
    h_cost: float = 0.0
    f_cost: float = 0.0
    
    def __hash__(self):
        """Make Node hashable based on label."""
        return hash(self.label)
    
    def __eq__(self, other):
        """Check equality based on label."""
        if not isinstance(other, Node):
            return False
        return self.label == other.label
    
@dataclass
class Ability:
    """Player ability with cooldown."""
    name: str
    key: int  # pygame key constant
    cooldown_ms: int
    duration_ms: int = 0
    last_used: float = 0
    active_until: float = 0
    
    def is_ready(self, current_time: float) -> bool:
        """Check if ability is off cooldown."""
        return current_time - self.last_used >= self.cooldown_ms
    
    def is_active(self, current_time: float) -> bool:
        """Check if ability effect is currently active."""
        return current_time < self.active_until
    
    def use(self, current_time: float) -> bool:
        """Try to use ability. Returns True if successful."""
        if self.is_ready(current_time):
            self.last_used = current_time
            self.active_until = current_time + self.duration_ms
            return True
        return False

class EnemyAI:
    """Enemy agent that chases player using pathfinding."""
    
    def __init__(self, start_node: Node, algorithm: str = 'BFS'):
        """Initialize enemy AI."""
        self.current_node = start_node
        self.algorithm = algorithm
        self.path: List[Node] = []
        self.path_index = 0
        self.move_delay = ENEMY_SPEEDS.get(algorithm, 500)
        self.last_move_time = 0
        self.stats = Stats()
        
    def update_path(self, graph: 'ArenaGraph', target_node: Node):
        """Recompute path to target using current algorithm."""
        # Use BFS on the graph structure to find path
        if self.current_node == target_node:
            self.path = []
            self.path_index = 0
            return
        
        # Simple BFS-based pathfinding on graph
        from collections import deque
        
        queue = deque([(self.current_node, [self.current_node])])
        visited = {self.current_node}
        
        while queue:
            current, path = queue.popleft()
            
            if current == target_node:
                # Found path - skip first node (current position)
                self.path = path[1:] if len(path) > 1 else []
                self.path_index = 0
                self.stats.path_len = len(self.path)
                return
            
            # Explore neighbors
            for neighbor in current.neighbors:
                if neighbor not in visited and not neighbor.blocked:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        # No path found
        self.path = []
        self.path_index = 0
        
    def update(self, current_time: float, graph: 'ArenaGraph', target_node: Node) -> bool:
        """Update enemy state. Returns True if moved."""
        if current_time - self.last_move_time < self.move_delay:
            return False
        
        # Recompute path every move (player might have moved)
        self.update_path(graph, target_node)
        
        if self.path and self.path_index < len(self.path):
            self.current_node = self.path[self.path_index]
            self.path_index += 1
            self.last_move_time = current_time
            return True
        
        return False

class ArenaGraph:
    """Graph structure for the arena."""
    
    def __init__(self, num_nodes: int = 25):
        """Initialize arena with nodes."""
        self.nodes: List[Node] = []
        self.num_nodes = num_nodes
        self.generate_graph()
        
    def generate_graph(self):
        """Generate a connected graph with specified number of nodes."""
        self.nodes = []
        
        # Generate nodes in a grid-like pattern with some randomness
        grid_size = int(self.num_nodes ** 0.5) + 1
        node_id = 0
        
        for i in range(grid_size):
            for j in range(grid_size):
                if node_id >= self.num_nodes:
                    break
                    
                # Add some position variance for visual interest
                x = 100 + j * 120 + random.randint(-15, 15)
                y = 100 + i * 120 + random.randint(-15, 15)
                
                node = Node(
                    pos=(x, y),
                    label=f"N{node_id}"
                )
                self.nodes.append(node)
                node_id += 1
        
        # Connect nodes (create edges)
        self._connect_nodes()
    
    def _connect_nodes(self):
        """Create edges between nodes with random weights."""
        # Connect each node to nearby nodes
        for node in self.nodes:
            for other in self.nodes:
                if node == other:
                    continue
                
                # Calculate distance
                dx = node.pos[0] - other.pos[0]
                dy = node.pos[1] - other.pos[1]
                dist = (dx*dx + dy*dy) ** 0.5
                
                # Connect if close enough (within ~150 pixels)
                if dist < 150:
                    if other not in node.neighbors:
                        node.neighbors.append(other)
                        # Random weight between 1 and 5
                        weight = random.randint(1, 5)
                        node.weights[other] = weight
    
    def get_random_node(self) -> Optional[Node]:
        """Get a random non-blocked node."""
        available = [n for n in self.nodes if not n.blocked]
        return random.choice(available) if available else None
    
    def get_node_at_pos(self, screen_pos: Tuple[int, int], radius: int = 20) -> Optional[Node]:
        """Get node at screen position (for click detection)."""
        x, y = screen_pos
        for node in self.nodes:
            nx, ny = node.pos
            dist = ((x - nx)**2 + (y - ny)**2) ** 0.5
            if dist < radius:
                return node
        return None

class ArenaMode:
    """Main game mode for Algorithm Arena."""
    
    def __init__(self, screen: pygame.Surface):
        """Initialize arena mode."""
        self.screen = screen
        self.graph = ArenaGraph(num_nodes=28)
        
        # Setup player and enemy
        self.player_node = self.graph.get_random_node()
        self.enemy_node = self.graph.get_random_node()
        while self.enemy_node == self.player_node:
            self.enemy_node = self.graph.get_random_node()
        
        self.enemy = EnemyAI(self.enemy_node, algorithm='BFS')
        self.current_algorithm = 'BFS'
        
        # Abilities
        self.abilities = [
            Ability("Shield", pygame.K_q, cooldown_ms=10000, duration_ms=3000),
            Ability("Teleport", pygame.K_w, cooldown_ms=8000),
            Ability("Block Node", pygame.K_e, cooldown_ms=12000),
            Ability("Increase Weight", pygame.K_r, cooldown_ms=6000, duration_ms=5000),
        ]
        
        # UI state
        self.hovered_node: Optional[Node] = None
        self.paused = False
        self.game_over = False
        self.score = 0
        self.start_time = time.time()
        
        # Fonts
        self.font_small = pygame.font.Font(None, 18)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 36)
    
    def handle_event(self, event: pygame.event.Event) -> str:
        """Handle input events. Returns 'menu', 'playing', or 'quit'."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'menu'
            elif event.key == pygame.K_SPACE:
                self.paused = not self.paused
                return 'playing'
            
            # Algorithm switching
            algo_keys = {
                pygame.K_1: 'BFS',
                pygame.K_2: 'DFS',
                pygame.K_3: 'UCS',
                pygame.K_4: 'Greedy',
                pygame.K_5: 'A*'
            }
            if event.key in algo_keys:
                self.current_algorithm = algo_keys[event.key]
                self.enemy.algorithm = self.current_algorithm
                self.enemy.move_delay = ENEMY_SPEEDS.get(self.current_algorithm, 500)
                return 'playing'
            
            # Abilities
            current_time = pygame.time.get_ticks()
            for ability in self.abilities:
                if event.key == ability.key:
                    if ability.use(current_time):
                        self._activate_ability(ability, current_time)
        
        elif event.type == pygame.MOUSEMOTION:
            # Update hovered node
            self.hovered_node = self.graph.get_node_at_pos(event.pos, radius=25)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                clicked_node = self.graph.get_node_at_pos(event.pos, radius=25)
                if clicked_node and self._is_adjacent(clicked_node):
                    self.player_node = clicked_node
        
        return 'playing'
    
    def _is_adjacent(self, node: Node) -> bool:
        """Check if node is adjacent to player's current node."""
        return node in self.player_node.neighbors
    
    def _activate_ability(self, ability: Ability, current_time: float):
        """Execute ability effect."""
        if ability.name == "Shield":
            pass  # Shield is handled in collision check
        elif ability.name == "Teleport":
            # Teleport to random nearby node
            nearby = [n for n in self.graph.nodes 
                     if n != self.player_node and not n.blocked
                     and self._calculate_distance(n.pos, self.player_node.pos) < 200]
            if nearby:
                self.player_node = random.choice(nearby)
        elif ability.name == "Block Node":
            # Block a random node near enemy
            nearby = [n for n in self.graph.nodes
                     if n != self.enemy.current_node and n != self.player_node
                     and not n.blocked
                     and self._calculate_distance(n.pos, self.enemy.current_node.pos) < 150]
            if nearby:
                node_to_block = random.choice(nearby)
                node_to_block.blocked = True
        elif ability.name == "Increase Weight":
            # Increase weights of edges near player
            for neighbor in self.player_node.neighbors:
                if neighbor in self.player_node.weights:
                    self.player_node.weights[neighbor] *= 2
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two positions."""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return (dx*dx + dy*dy) ** 0.5
    
    def update(self):
        """Update game state."""
        if self.paused or self.game_over:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Update enemy
        self.enemy.update(current_time, self.graph, self.player_node)
        
        # Check collision
        shield_ability = self.abilities[0]  # Shield
        if self.enemy.current_node == self.player_node:
            if not shield_ability.is_active(current_time):
                self.game_over = True
        
        # Update score (survival time)
        self.score = int(time.time() - self.start_time)
    
    def draw(self):
        """Render the arena."""
        self.screen.fill((20, 20, 30))
        
        # Draw edges
        for node in self.graph.nodes:
            for neighbor in node.neighbors:
                color = (50, 50, 60)
                pygame.draw.line(self.screen, color, node.pos, neighbor.pos, 2)
                
                # Draw weight on edge
                mid_x = (node.pos[0] + neighbor.pos[0]) // 2
                mid_y = (node.pos[1] + neighbor.pos[1]) // 2
                weight = node.weights.get(neighbor, 1)
                weight_text = self.font_small.render(str(weight), True, (100, 100, 100))
                self.screen.blit(weight_text, (mid_x - 5, mid_y - 5))
        
        # Draw nodes
        for node in self.graph.nodes:
            if node.blocked:
                color = (100, 50, 50)
            else:
                color = (60, 60, 80)
            pygame.draw.circle(self.screen, color, node.pos, 20)
            pygame.draw.circle(self.screen, (100, 100, 120), node.pos, 20, 2)
            
            # Draw label
            label_text = self.font_small.render(node.label, True, (200, 200, 200))
            label_rect = label_text.get_rect(center=node.pos)
            self.screen.blit(label_text, label_rect)
        
        # Draw enemy path
        if self.enemy.path and len(self.enemy.path) > 0:
            # Draw path line
            path_points = [self.enemy.current_node.pos] + [node.pos for node in self.enemy.path]
            if len(path_points) > 1:
                pygame.draw.lines(self.screen, (255, 150, 150), False, path_points, 2)
        
        # Draw player
        if self.player_node:
            pygame.draw.circle(self.screen, (100, 150, 255), self.player_node.pos, 15)
            
            # Draw shield effect if active
            current_time = pygame.time.get_ticks()
            if self.abilities[0].is_active(current_time):
                pygame.draw.circle(self.screen, (150, 200, 255), self.player_node.pos, 25, 3)
        
        # Draw enemy
        if self.enemy.current_node:
            pygame.draw.circle(self.screen, (255, 100, 100), self.enemy.current_node.pos, 15)
            
            # Draw enemy cooldown bar
            self._draw_enemy_cooldown()
        
        # Draw HUD
        self._draw_hud()
        
        # Draw tooltip
        if self.hovered_node:
            self._draw_tooltip(self.hovered_node)
        
        # Draw game over
        if self.game_over:
            self._draw_game_over()
    
    def _draw_enemy_cooldown(self):
        """Draw cooldown progress bar above enemy."""
        current_time = pygame.time.get_ticks()
        time_since_move = current_time - self.enemy.last_move_time
        progress = min(1.0, time_since_move / self.enemy.move_delay)
        
        enemy_pos = self.enemy.current_node.pos
        bar_width = 40
        bar_height = 4
        bar_x = enemy_pos[0] - bar_width // 2
        bar_y = enemy_pos[1] - 30
        
        # Background
        pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        # Progress
        pygame.draw.rect(self.screen, (255, 100, 100), (bar_x, bar_y, bar_width * progress, bar_height))
    
    def _draw_hud(self):
        """Draw HUD with game info."""
        # HUD background
        hud_rect = pygame.Rect(10, 10, 500, 120)
        pygame.draw.rect(self.screen, (40, 40, 50), hud_rect)
        pygame.draw.rect(self.screen, (100, 100, 120), hud_rect, 2)
        
        y_offset = 20
        
        # Title
        title = self.font_medium.render(f"Algorithm Arena - {self.current_algorithm}", True, (220, 220, 220))
        self.screen.blit(title, (20, y_offset))
        y_offset += 30
        
        # Score
        score_text = self.font_small.render(f"Survival Time: {self.score}s", True, (200, 200, 200))
        self.screen.blit(score_text, (20, y_offset))
        y_offset += 20
        
        # Controls
        controls = "1-5: Algorithm | SPACE: Pause | ESC: Menu"
        controls_text = self.font_small.render(controls, True, (180, 180, 180))
        self.screen.blit(controls_text, (20, y_offset))
        y_offset += 20
        
        # Abilities
        abilities_text = "Q: Shield | W: Teleport | E: Block | R: Inc Weight"
        abilities_surface = self.font_small.render(abilities_text, True, (180, 180, 180))
        self.screen.blit(abilities_surface, (20, y_offset))
        
        # Ability cooldowns (right side)
        current_time = pygame.time.get_ticks()
        ability_x = 520
        ability_y = 20
        for ability in self.abilities:
            if ability.is_active(current_time):
                color = (100, 255, 100)
                status = "ACTIVE"
            elif ability.is_ready(current_time):
                color = (100, 255, 100)
                status = "READY"
            else:
                color = (150, 150, 150)
                remaining = (ability.cooldown_ms - (current_time - ability.last_used)) / 1000
                status = f"{remaining:.1f}s"
            
            text = self.font_small.render(f"{ability.name}: {status}", True, color)
            self.screen.blit(text, (ability_x, ability_y))
            ability_y += 22
        
        # Pause indicator
        if self.paused:
            pause_text = self.font_large.render("PAUSED", True, (255, 255, 0))
            pause_rect = pause_text.get_rect(center=(self.screen.get_width() // 2, 50))
            self.screen.blit(pause_text, pause_rect)
    
    def _draw_tooltip(self, node: Node):
        """Draw Windows-style tooltip for hovered node."""
        # Tooltip content
        lines = [
            f"Node {node.label}",
            f"Connections: {len(node.neighbors)}",
        ]
        
        if node.blocked:
            lines.append("Status: BLOCKED")
        else:
            lines.append("Status: Open")
        
        # Add neighbor weights
        if node.neighbors:
            lines.append("Edge Weights:")
            for i, neighbor in enumerate(node.neighbors[:3]):  # Show first 3
                weight = node.weights.get(neighbor, 1)
                lines.append(f"  -> {neighbor.label}: {weight}")
            if len(node.neighbors) > 3:
                lines.append(f"  ... +{len(node.neighbors) - 3} more")
        
        # Algorithm info
        lines.append("")
        lines.append(f"Enemy Algorithm: {self.current_algorithm}")
        
        # Tooltip styling (Windows-style)
        bg_color = (255, 255, 225)  # Light yellow
        border_color = (0, 0, 0)
        text_color = (0, 0, 0)
        padding = 8
        line_height = 18
        
        # Calculate size
        max_width = max([self.font_small.size(line)[0] for line in lines if line])
        tooltip_width = max_width + padding * 2
        tooltip_height = len(lines) * line_height + padding * 2
        
        # Create surface
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height))
        tooltip_surface.fill(bg_color)
        pygame.draw.rect(tooltip_surface, border_color, tooltip_surface.get_rect(), 1)
        
        # Draw text
        for i, line in enumerate(lines):
            if line:  # Skip empty lines in rendering
                text = self.font_small.render(line, True, text_color)
                tooltip_surface.blit(text, (padding, padding + i * line_height))
        
        # Position near mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tooltip_x = mouse_x + 15
        tooltip_y = mouse_y + 15
        
        # Keep on screen
        if tooltip_x + tooltip_width > self.screen.get_width():
            tooltip_x = mouse_x - tooltip_width - 5
        if tooltip_y + tooltip_height > self.screen.get_height():
            tooltip_y = mouse_y - tooltip_height - 5
        
        self.screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
    
    def _draw_game_over(self):
        """Draw game over overlay."""
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font_large.render("GAME OVER", True, (255, 100, 100))
        game_over_rect = game_over_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_text = self.font_medium.render(f"Survival Time: {self.score} seconds", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.font_small.render("Press ESC to return to menu", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

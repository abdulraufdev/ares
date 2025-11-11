"""Main menu and algorithm selection system."""
import pygame
from dataclasses import dataclass
from typing import Optional, List, Tuple


@dataclass
class Button:
    """Represents a clickable button."""
    rect: pygame.Rect
    text: str
    color: Tuple[int, int, int]
    hover_color: Tuple[int, int, int]
    text_color: Tuple[int, int, int]
    hovered: bool = False
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the button."""
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, self.text_color, self.rect, 2)
        
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if the button is clicked at the given position."""
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos: Tuple[int, int]) -> None:
        """Update hover state based on mouse position."""
        self.hovered = self.rect.collidepoint(pos)


class AlgorithmOption:
    """Represents an algorithm selection option."""
    
    def __init__(self, name: str, description: str, rect: pygame.Rect):
        self.name = name
        self.description = description
        self.rect = rect
        self.selected = False
        self.hovered = False
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font, desc_font: pygame.font.Font) -> None:
        """Draw the algorithm option."""
        # Background
        if self.selected:
            color = (80, 120, 200)
        elif self.hovered:
            color = (60, 60, 80)
        else:
            color = (40, 40, 50)
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (220, 220, 220), self.rect, 2)
        
        # Selection indicator
        if self.selected:
            indicator_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 20, 20, 20)
            pygame.draw.circle(screen, (100, 255, 100), indicator_rect.center, 10)
            pygame.draw.circle(screen, (220, 220, 220), indicator_rect.center, 10, 2)
        
        # Algorithm name
        name_surface = font.render(self.name, True, (220, 220, 220))
        screen.blit(name_surface, (self.rect.x + 40, self.rect.y + 15))
        
        # Description
        desc_surface = desc_font.render(self.description, True, (180, 180, 180))
        screen.blit(desc_surface, (self.rect.x + 40, self.rect.y + 45))
    
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if the option is clicked."""
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos: Tuple[int, int]) -> None:
        """Update hover state."""
        self.hovered = self.rect.collidepoint(pos)


class MainMenu:
    """Main menu system with algorithm selection."""
    
    # Menu states
    STATE_MENU = 'menu'
    STATE_TUTORIAL = 'tutorial'
    STATE_ALGO_SELECT = 'algo_select'
    STATE_PLAYING = 'playing'
    
    def __init__(self, width: int, height: int):
        """Initialize main menu."""
        self.width = width
        self.height = height
        self.state = self.STATE_MENU
        self.selected_algo: Optional[str] = None
        
        # Fonts
        self.title_font = pygame.font.SysFont('Consolas', 48, bold=True)
        self.button_font = pygame.font.SysFont('Consolas', 24)
        self.text_font = pygame.font.SysFont('Consolas', 16)
        self.desc_font = pygame.font.SysFont('Consolas', 14)
        
        # Colors
        self.bg_color = (20, 20, 30)
        self.button_color = (60, 60, 80)
        self.button_hover_color = (80, 80, 100)
        self.text_color = (220, 220, 220)
        
        # Create buttons
        self._create_buttons()
        
        # Create algorithm options
        self._create_algo_options()
    
    def _create_buttons(self) -> None:
        """Create menu buttons."""
        center_x = self.width // 2
        button_width = 300
        button_height = 60
        button_spacing = 80
        start_y = self.height // 2
        
        # Main menu buttons
        self.tutorial_button = Button(
            rect=pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height),
            text="TUTORIAL",
            color=self.button_color,
            hover_color=self.button_hover_color,
            text_color=self.text_color
        )
        
        self.select_algo_button = Button(
            rect=pygame.Rect(center_x - button_width // 2, start_y + button_spacing, button_width, button_height),
            text="SELECT ALGORITHM",
            color=self.button_color,
            hover_color=self.button_hover_color,
            text_color=self.text_color
        )
        
        self.quit_button = Button(
            rect=pygame.Rect(center_x - button_width // 2, start_y + button_spacing * 2, button_width, button_height),
            text="QUIT",
            color=self.button_color,
            hover_color=self.button_hover_color,
            text_color=self.text_color
        )
        
        # Back button (for sub-menus)
        self.back_button = Button(
            rect=pygame.Rect(50, self.height - 100, 150, 50),
            text="BACK",
            color=self.button_color,
            hover_color=self.button_hover_color,
            text_color=self.text_color
        )
        
        # Start game button (in algorithm selection)
        self.start_game_button = Button(
            rect=pygame.Rect(self.width - 250, self.height - 100, 200, 50),
            text="START GAME",
            color=(80, 150, 80),
            hover_color=(100, 180, 100),
            text_color=self.text_color
        )
    
    def _create_algo_options(self) -> None:
        """Create algorithm selection options."""
        algos = [
            ("BFS", "Explores level by level. No weights considered."),
            ("DFS", "Dives deep first. No weights considered."),
            ("UCS", "Finds lowest cost path. Uses edge weights."),
            ("Greedy", "Rushes toward goal. Uses heuristic estimation."),
            ("A*", "Optimal path finding. Uses cost + heuristic.")
        ]
        
        self.algo_options: List[AlgorithmOption] = []
        
        option_width = 600
        option_height = 80
        start_x = (self.width - option_width) // 2
        start_y = 150
        spacing = 90
        
        for i, (name, desc) in enumerate(algos):
            rect = pygame.Rect(start_x, start_y + i * spacing, option_width, option_height)
            option = AlgorithmOption(name, desc, rect)
            self.algo_options.append(option)
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle menu events.
        
        Returns:
            Command string: 'quit', 'start_game', or None
        """
        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            
            if self.state == self.STATE_MENU:
                self.tutorial_button.update_hover(pos)
                self.select_algo_button.update_hover(pos)
                self.quit_button.update_hover(pos)
            
            elif self.state == self.STATE_TUTORIAL:
                self.back_button.update_hover(pos)
            
            elif self.state == self.STATE_ALGO_SELECT:
                self.back_button.update_hover(pos)
                if self.selected_algo:
                    self.start_game_button.update_hover(pos)
                for option in self.algo_options:
                    option.update_hover(pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                pos = event.pos
                
                if self.state == self.STATE_MENU:
                    if self.tutorial_button.is_clicked(pos):
                        self.state = self.STATE_TUTORIAL
                    elif self.select_algo_button.is_clicked(pos):
                        self.state = self.STATE_ALGO_SELECT
                    elif self.quit_button.is_clicked(pos):
                        return 'quit'
                
                elif self.state == self.STATE_TUTORIAL:
                    if self.back_button.is_clicked(pos):
                        self.state = self.STATE_MENU
                
                elif self.state == self.STATE_ALGO_SELECT:
                    if self.back_button.is_clicked(pos):
                        self.state = self.STATE_MENU
                    elif self.selected_algo and self.start_game_button.is_clicked(pos):
                        self.state = self.STATE_PLAYING
                        return 'start_game'
                    
                    # Check algorithm options
                    for option in self.algo_options:
                        if option.is_clicked(pos):
                            # Deselect all
                            for opt in self.algo_options:
                                opt.selected = False
                            # Select this one
                            option.selected = True
                            self.selected_algo = option.name
        
        return None
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the current menu state."""
        screen.fill(self.bg_color)
        
        if self.state == self.STATE_MENU:
            self._draw_main_menu(screen)
        elif self.state == self.STATE_TUTORIAL:
            self._draw_tutorial(screen)
        elif self.state == self.STATE_ALGO_SELECT:
            self._draw_algo_selection(screen)
    
    def _draw_main_menu(self, screen: pygame.Surface) -> None:
        """Draw main menu screen."""
        # Title
        title = self.title_font.render("ALGORITHM ARENA", True, self.text_color)
        title_rect = title.get_rect(center=(self.width // 2, 150))
        screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.text_font.render("Strategic Graph Traversal Game", True, (180, 180, 180))
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 200))
        screen.blit(subtitle, subtitle_rect)
        
        # Buttons
        self.tutorial_button.draw(screen, self.button_font)
        self.select_algo_button.draw(screen, self.button_font)
        self.quit_button.draw(screen, self.button_font)
    
    def _draw_tutorial(self, screen: pygame.Surface) -> None:
        """Draw tutorial screen."""
        # Title
        title = self.title_font.render("TUTORIAL", True, self.text_color)
        title_rect = title.get_rect(center=(self.width // 2, 80))
        screen.blit(title, title_rect)
        
        # Tutorial text
        tutorial_lines = [
            "OBJECTIVE:",
            "• Survive as long as possible or trap the enemy",
            "• The enemy uses the selected algorithm to chase you",
            "",
            "CONTROLS:",
            "• Click on adjacent nodes to move your character",
            "• Hover over nodes to see algorithm-specific information",
            "• Use abilities to manipulate the graph",
            "",
            "MOVEMENT SPEED:",
            "• Low weight edges (1-2): Fast movement",
            "• Medium weight edges (3-5): Normal movement",
            "• High weight edges (6-10): Slow movement",
            "",
            "ABILITIES:",
            "• Increase Weight: Make an edge 5x more costly",
            "• Block Node: Make a node unwalkable",
            "",
            "VICTORY CONDITIONS:",
            "• Enemy cannot find a path to you",
            "• Survive for the time limit",
        ]
        
        y = 150
        for line in tutorial_lines:
            if line.startswith("•"):
                text = self.text_font.render(line, True, (200, 200, 200))
            elif line == "":
                y += 10
                continue
            else:
                text = self.button_font.render(line, True, self.text_color)
                y += 5
            screen.blit(text, (100, y))
            y += 25
        
        # Back button
        self.back_button.draw(screen, self.button_font)
    
    def _draw_algo_selection(self, screen: pygame.Surface) -> None:
        """Draw algorithm selection screen."""
        # Title
        title = self.title_font.render("SELECT ALGORITHM", True, self.text_color)
        title_rect = title.get_rect(center=(self.width // 2, 80))
        screen.blit(title, title_rect)
        
        # Draw algorithm options
        for option in self.algo_options:
            option.draw(screen, self.button_font, self.desc_font)
        
        # Back button
        self.back_button.draw(screen, self.button_font)
        
        # Start game button (only if algorithm selected)
        if self.selected_algo:
            self.start_game_button.draw(screen, self.button_font)
    
    def reset(self) -> None:
        """Reset menu to initial state."""
        self.state = self.STATE_MENU
        self.selected_algo = None
        for option in self.algo_options:
            option.selected = False

"""Main menu and tutorial screens for Algorithm Arena."""
import pygame
from config import *


class Button:
    """Modern rounded button with gradient and hover effects."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 bg_color=UI_BUTTON_BG, hover_color=UI_BUTTON_HOVER):
        """Initialize button.
        
        Args:
            x, y: Position
            width, height: Size
            text: Button text
            bg_color: Normal background color
            hover_color: Hover background color
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.active_color = UI_BUTTON_ACTIVE
        self.is_hovered = False
        self.is_pressed = False
        self.hover_scale = 1.0  # For smooth animations
    
    def handle_event(self, event) -> bool:
        """Handle mouse events.
        
        Returns:
            True if button was clicked
        """
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            # Smooth scale animation on hover
            if self.is_hovered:
                self.hover_scale = min(1.05, self.hover_scale + 0.05)
            else:
                self.hover_scale = max(1.0, self.hover_scale - 0.05)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                return True
            self.is_pressed = False
        
        return False
    
    def draw(self, screen, font):
        """Draw the button with modern effects."""
        # Choose color based on state
        color = self.bg_color
        if self.is_pressed:
            color = self.active_color
        elif self.is_hovered:
            color = self.hover_color
        
        # Draw shadow effect
        shadow_rect = self.rect.copy()
        shadow_rect.y += 3
        pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect, border_radius=15)
        
        # Draw rounded rectangle with gradient effect
        # Create a slightly lighter color for gradient
        light_color = tuple(min(255, c + 20) for c in color)
        
        # Main button
        pygame.draw.rect(screen, color, self.rect, border_radius=15)
        
        # Highlight at top for 3D effect
        highlight_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height // 3)
        pygame.draw.rect(screen, light_color, highlight_rect, border_radius=15)
        
        # Border
        border_color = (200, 220, 255) if self.is_hovered else UI_BUTTON_TEXT
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=15)
        
        # Glow effect on hover
        if self.is_hovered:
            glow_rect = self.rect.inflate(4, 4)
            pygame.draw.rect(screen, (100, 150, 255, 128), glow_rect, 3, border_radius=15)
        
        # Draw text centered
        text_surface = font.render(self.text, True, UI_BUTTON_TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class RadioButton:
    """Radio button for algorithm selection."""
    
    def __init__(self, x: int, y: int, text: str, description: str):
        """Initialize radio button.
        
        Args:
            x, y: Position
            text: Algorithm name
            description: Algorithm description
        """
        self.x = x
        self.y = y
        self.text = text
        self.description = description
        self.selected = False
        self.circle_radius = 15  # Larger circles
        self.hover = False
        
        # Clickable area
        self.rect = pygame.Rect(x - 20, y - 20, 500, 40)
    
    def handle_event(self, event) -> bool:
        """Handle mouse events.
        
        Returns:
            True if radio button was clicked
        """
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        
        return False
    
    def draw(self, screen, font, color):
        """Draw the radio button."""
        # Outer circle with smooth transitions
        circle_color = color if self.hover or self.selected else (150, 150, 150)
        pygame.draw.circle(screen, circle_color, (self.x, self.y), self.circle_radius, 3)
        
        # Inner circle if selected
        if self.selected:
            pygame.draw.circle(screen, color, (self.x, self.y), self.circle_radius - 6)
        
        # Text with larger font
        text_surface = font.render(f"{self.text} - {self.description}", True, (230, 230, 230))
        screen.blit(text_surface, (self.x + 25, self.y - 12))


class MainMenu:
    """Main menu with algorithm selection."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize main menu.
        
        Args:
            screen_width: Window width
            screen_height: Window height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.selected_algorithm = None
        
        # Fonts - using modern Segoe UI / fallback to Arial
        try:
            self.title_font = pygame.font.SysFont('Segoe UI', 48, bold=True)
            self.font = pygame.font.SysFont('Segoe UI', 20, bold=True)
            self.algo_font = pygame.font.SysFont('Segoe UI', 18)
        except:
            self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
            self.font = pygame.font.SysFont('Arial', 20, bold=True)
            self.algo_font = pygame.font.SysFont('Arial', 18)
        
        # Algorithm radio buttons with improved spacing
        # Title at 80px, Tutorial button at 160px, Label at 240px, Radio buttons start at 280px
        center_x = screen_width // 2 - 100
        start_y = 280
        spacing = 60
        
        self.radio_buttons = [
            RadioButton(center_x, start_y, 'BFS', 'Breadth First Search'),
            RadioButton(center_x, start_y + spacing, 'DFS', 'Depth First Search'),
            RadioButton(center_x, start_y + spacing * 2, 'UCS', 'Uniform Cost Search'),
            RadioButton(center_x, start_y + spacing * 3, 'Greedy (Local Min)', 'Greedy Best-First (Local Minima)'),
            RadioButton(center_x, start_y + spacing * 4, 'Greedy (Local Max)', 'Greedy Best-First (Local Maxima)'),
            RadioButton(center_x, start_y + spacing * 5, 'A* (Local Min)', 'A* Search (Local Minima)'),
            RadioButton(center_x, start_y + spacing * 6, 'A* (Local Max)', 'A* Search (Local Maxima)'),
        ]
        
        # Buttons with improved spacing
        button_width = 240
        button_height = 60
        button_x = screen_width // 2 - button_width // 2
        
        self.tutorial_button = Button(
            button_x, 160, button_width, button_height, 'TUTORIAL'
        )
        
        self.start_button = Button(
            button_x, 700, button_width, button_height, 'START GAME'
        )
        
        self.quit_button = Button(
            button_x, 770, button_width, button_height, 'QUIT'
        )
    
    def handle_event(self, event) -> tuple[str, str | None]:
        """Handle input events.
        
        Returns:
            Tuple of (action, selected_algorithm) where action is 'tutorial', 'start', 'quit', or ''
        """
        # Check tutorial button
        if self.tutorial_button.handle_event(event):
            return ('tutorial', self.selected_algorithm)
        
        # Check quit button
        if self.quit_button.handle_event(event):
            return ('quit', None)
        
        # Check start button (only if algorithm selected)
        if self.selected_algorithm and self.start_button.handle_event(event):
            return ('start', self.selected_algorithm)
        
        # Check radio buttons
        for radio in self.radio_buttons:
            if radio.handle_event(event):
                # Deselect all others
                for r in self.radio_buttons:
                    r.selected = False
                # Select this one
                radio.selected = True
                self.selected_algorithm = radio.text
        
        return ('', None)
    
    def draw(self, screen):
        """Draw the main menu."""
        # Modern gradient background (dark blue to purple)
        for y in range(self.screen_height):
            # Gradient from dark blue (15, 25, 45) to dark purple (35, 15, 55)
            ratio = y / self.screen_height
            r = int(15 + (35 - 15) * ratio)
            g = int(25 + (15 - 25) * ratio)
            b = int(45 + (55 - 45) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (self.screen_width, y))
        
        # Title at 80px from top with glow effect
        title = self.title_font.render('ALGORITHM ARENA', True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        
        # Glow effect for title
        glow = self.title_font.render('ALGORITHM ARENA', True, (100, 150, 255))
        glow_rect = glow.get_rect(center=(self.screen_width // 2 + 2, 82))
        screen.blit(glow, glow_rect)
        screen.blit(title, title_rect)
        
        # Tutorial button at 160px
        self.tutorial_button.draw(screen, self.font)
        
        # Selection label at 240px
        label = self.font.render('SELECT ALGORITHM:', True, (220, 220, 255))
        screen.blit(label, (self.screen_width // 2 - 100, 240))
        
        # Radio buttons starting at 280px
        for radio in self.radio_buttons:
            # Use algorithm color if available
            color = (150, 150, 200)
            if radio.text in THEMES:
                color = THEMES[radio.text]['ui_accent']
            radio.draw(screen, self.algo_font, color)
        
        # Start button at 700px (grayed out if no selection)
        if not self.selected_algorithm:
            # Draw grayed out button
            pygame.draw.rect(screen, (60, 60, 60), self.start_button.rect, 
                           border_radius=15)
            pygame.draw.rect(screen, (100, 100, 100), self.start_button.rect, 3,
                           border_radius=15)
            text = self.font.render('START GAME', True, (120, 120, 120))
            text_rect = text.get_rect(center=self.start_button.rect.center)
            screen.blit(text, text_rect)
        else:
            self.start_button.draw(screen, self.font)
        
        # Quit button at 770px
        self.quit_button.draw(screen, self.font)


class TutorialScreen:
    """Tutorial screen with game instructions."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize tutorial screen.
        
        Args:
            screen_width: Window width
            screen_height: Window height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Fonts - using modern Segoe UI / fallback to Arial
        try:
            self.title_font = pygame.font.SysFont('Segoe UI', 30, bold=True)
            self.heading_font = pygame.font.SysFont('Segoe UI', 19, bold=True)
            self.font = pygame.font.SysFont('Segoe UI', 17)
        except:
            self.title_font = pygame.font.SysFont('Arial', 30, bold=True)
            self.heading_font = pygame.font.SysFont('Arial', 19, bold=True)
            self.font = pygame.font.SysFont('Arial', 17)
        
        # Back button
        button_width = 200
        button_height = 50
        self.back_button = Button(
            screen_width // 2 - button_width // 2,
            screen_height - 80,
            button_width, button_height,
            'BACK TO MENU'
        )
    
    def handle_event(self, event) -> bool:
        """Handle input events.
        
        Returns:
            True if back button was clicked
        """
        return self.back_button.handle_event(event)
    
    def draw(self, screen):
        """Draw the tutorial screen."""
        screen.fill((20, 20, 30))
        
        # Title
        title = self.title_font.render('HOW TO PLAY - ALGORITHM ARENA', True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 40))
        screen.blit(title, title_rect)
        
        y = 90
        line_spacing = 25
        section_spacing = 35
        
        # Helper to draw text
        def draw_text(text, font, y_pos, indent=0):
            rendered = font.render(text, True, (220, 220, 220))
            screen.blit(rendered, (60 + indent, y_pos))
            return y_pos + line_spacing
        
        # Objective
        y = draw_text('OBJECTIVE:', self.heading_font, y) - 5
        y = draw_text('Survive as long as possible! The enemy uses pathfinding', self.font, y)
        y = draw_text('algorithms to chase you.', self.font, y)
        y += section_spacing - line_spacing
        
        # Movement
        y = draw_text('MOVEMENT:', self.heading_font, y) - 5
        y = draw_text('• Click on adjacent nodes to move', self.font, y, 20)
        y = draw_text('• Movement speed depends on edge weight (for UCS/A*)', self.font, y, 20)
        y += section_spacing - line_spacing
        
        # Controls
        y = draw_text('CONTROLS:', self.heading_font, y) - 5
        y = draw_text('• Click: Move to adjacent node', self.font, y, 20)
        y = draw_text('• Hover: See node details', self.font, y, 20)
        y = draw_text('• SPACE: Pause game', self.font, y, 20)
        y = draw_text('• ESC: Return to menu', self.font, y, 20)
        y += section_spacing - line_spacing
        
        # Strategy
        y = draw_text('STRATEGY:', self.heading_font, y) - 5
        y = draw_text('• Low-weight paths = faster movement', self.font, y, 20)
        y = draw_text('• High-weight paths = slower', self.font, y, 20)
        y = draw_text('• Enemy recalculates when you move', self.font, y, 20)
        y = draw_text('• Use pause to examine the graph', self.font, y, 20)
        
        # Back button
        self.back_button.draw(screen, self.font)

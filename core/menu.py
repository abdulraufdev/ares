"""Menu system for Algorithm Arena."""
import pygame
from dataclasses import dataclass
from typing import Optional

@dataclass
class Button:
    """Represents a clickable button."""
    rect: pygame.Rect
    text: str
    action: str
    color: tuple[int, int, int] = (60, 60, 80)
    hover_color: tuple[int, int, int] = (100, 100, 150)
    text_color: tuple[int, int, int] = (220, 220, 220)

class MenuManager:
    """Manages menu screens and navigation."""
    
    def __init__(self, screen: pygame.Surface):
        """Initialize menu manager."""
        self.screen = screen
        self.state = 'main'  # 'main', 'tutorial', 'game', 'paused'
        self.buttons = []
        self.font_title = pygame.font.SysFont('Arial', 72, bold=True)
        self.font_button = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_text = pygame.font.SysFont('Arial', 20)
        self.font_small = pygame.font.SysFont('Arial', 16)
        self.hover_button = None
        
        # Animation state
        self.animation_offset = 0
        
    def update_animation(self):
        """Update background animation."""
        self.animation_offset = (self.animation_offset + 1) % 360
        
    def draw_main_menu(self) -> Optional[str]:
        """Draw main menu and return action if button clicked."""
        width, height = self.screen.get_size()
        
        # Animated background
        self.screen.fill((20, 20, 30))
        for i in range(0, width, 40):
            offset = (i + self.animation_offset) % width
            color = (30 + i % 20, 30 + i % 20, 40 + i % 20)
            pygame.draw.line(self.screen, color, (offset, 0), (offset, height), 2)
        
        # Title
        title_text = self.font_title.render("ALGORITHM ARENA", True, (100, 200, 255))
        title_rect = title_text.get_rect(center=(width // 2, height // 4))
        
        # Title shadow
        shadow_text = self.font_title.render("ALGORITHM ARENA", True, (20, 40, 60))
        shadow_rect = shadow_text.get_rect(center=(width // 2 + 3, height // 4 + 3))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font_text.render("AI Pathfinding Combat System", True, (180, 180, 180))
        subtitle_rect = subtitle_text.get_rect(center=(width // 2, height // 4 + 60))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Create buttons
        button_width = 300
        button_height = 60
        button_spacing = 20
        start_y = height // 2
        
        buttons = [
            Button(
                pygame.Rect((width - button_width) // 2, start_y, button_width, button_height),
                "Start Game",
                "start"
            ),
            Button(
                pygame.Rect((width - button_width) // 2, start_y + button_height + button_spacing, 
                           button_width, button_height),
                "Tutorial",
                "tutorial"
            ),
            Button(
                pygame.Rect((width - button_width) // 2, start_y + 2 * (button_height + button_spacing), 
                           button_width, button_height),
                "Quit",
                "quit"
            )
        ]
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            # Check hover
            is_hover = button.rect.collidepoint(mouse_pos)
            color = button.hover_color if is_hover else button.color
            
            # Draw button
            pygame.draw.rect(self.screen, color, button.rect, border_radius=10)
            pygame.draw.rect(self.screen, (100, 150, 200), button.rect, 3, border_radius=10)
            
            # Draw text
            text_surface = self.font_button.render(button.text, True, button.text_color)
            text_rect = text_surface.get_rect(center=button.rect.center)
            self.screen.blit(text_surface, text_rect)
        
        return buttons
    
    def draw_tutorial(self) -> bool:
        """Draw tutorial screen. Returns True when user wants to continue."""
        width, height = self.screen.get_size()
        
        # Background
        self.screen.fill((20, 20, 30))
        
        # Title
        title_text = self.font_title.render("TUTORIAL", True, (100, 200, 255))
        title_rect = title_text.get_rect(center=(width // 2, 60))
        self.screen.blit(title_text, title_rect)
        
        # Content sections
        y_offset = 130
        line_height = 30
        section_spacing = 15
        
        # Controls Section
        self.draw_section_title("CONTROLS", width // 2, y_offset, (255, 200, 100))
        y_offset += 40
        
        controls = [
            "• Click to Move - Click any node to move your player there",
            "• Press 1-5 to Switch Algorithms - Change enemy AI behavior",
            "  1=BFS  2=DFS  3=UCS  4=Greedy  5=A*",
            "• Press Q/W/E/R for Abilities - Use tactical abilities",
            "• Press SPACE to Pause - Pause/unpause the game"
        ]
        
        for control in controls:
            text = self.font_small.render(control, True, (220, 220, 220))
            self.screen.blit(text, (50, y_offset))
            y_offset += line_height
        
        y_offset += section_spacing
        
        # Abilities Section
        self.draw_section_title("ABILITIES", width // 2, y_offset, (100, 255, 150))
        y_offset += 40
        
        abilities = [
            "• Shield (Q) - Become invincible for 3 seconds",
            "• Teleport (W) - Jump to a nearby location instantly",
            "• Block (E) - Place an obstacle to trap the enemy",
            "• Weight (R) - Slow down enemy pathfinding algorithms"
        ]
        
        for ability in abilities:
            text = self.font_small.render(ability, True, (220, 220, 220))
            self.screen.blit(text, (50, y_offset))
            y_offset += line_height
        
        y_offset += section_spacing
        
        # Objective Section
        self.draw_section_title("OBJECTIVE", width // 2, y_offset, (255, 100, 150))
        y_offset += 40
        
        objective_text = "Survive as long as possible! The enemy uses different algorithms to chase you."
        text = self.font_text.render(objective_text, True, (220, 220, 220))
        text_rect = text.get_rect(center=(width // 2, y_offset))
        self.screen.blit(text, text_rect)
        y_offset += 50
        
        # Start prompt
        start_text = self.font_button.render("Press ENTER to Start", True, (100, 255, 100))
        start_rect = start_text.get_rect(center=(width // 2, height - 60))
        
        # Blinking effect
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            self.screen.blit(start_text, start_rect)
        
        return False
    
    def draw_section_title(self, text: str, x: int, y: int, color: tuple[int, int, int]):
        """Draw a section title."""
        text_surface = self.font_button.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)
        
        # Underline
        line_y = y + 20
        line_start = (x - text_rect.width // 2, line_y)
        line_end = (x + text_rect.width // 2, line_y)
        pygame.draw.line(self.screen, color, line_start, line_end, 2)
    
    def handle_menu_click(self, pos: tuple[int, int], buttons: list[Button]) -> Optional[str]:
        """Check if a button was clicked and return its action."""
        for button in buttons:
            if button.rect.collidepoint(pos):
                return button.action
        return None

"""Main menu for the game."""
import pygame
from typing import Optional

class Button:
    """Simple button for menu."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color=(100, 100, 120)):
        """Initialize button."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = (120, 120, 140)
        self.font = pygame.font.Font(None, 32)
    
    def draw(self, screen: pygame.Surface):
        """Draw the button."""
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Draw button background
        current_color = self.hover_color if is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect)
        pygame.draw.rect(screen, (150, 150, 170), self.rect, 2)
        
        # Draw text
        text_surface = self.font.render(self.text, True, (220, 220, 220))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, pos: tuple) -> bool:
        """Check if button was clicked at given position."""
        return self.rect.collidepoint(pos)

class MainMenu:
    """Main menu screen."""
    
    def __init__(self, screen: pygame.Surface):
        """Initialize main menu."""
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_subtitle = pygame.font.Font(None, 28)
        
        # Calculate button positions
        center_x = screen.get_width() // 2
        start_y = 250
        button_width = 300
        button_height = 60
        button_spacing = 80
        
        # Create buttons
        self.buttons = {
            'arena': Button(center_x - button_width // 2, start_y, 
                          button_width, button_height, "ALGORITHM ARENA"),
            'classic': Button(center_x - button_width // 2, start_y + button_spacing, 
                            button_width, button_height, "CLASSIC MODE"),
            'tutorial': Button(center_x - button_width // 2, start_y + button_spacing * 2, 
                             button_width, button_height, "HOW TO PLAY"),
            'quit': Button(center_x - button_width // 2, start_y + button_spacing * 3, 
                         button_width, button_height, "QUIT", color=(120, 60, 60))
        }
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle input. Returns action: 'arena', 'classic', 'tutorial', 'quit', or None."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'quit'
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                for action, button in self.buttons.items():
                    if button.is_clicked(event.pos):
                        return action
        return None
    
    def draw(self):
        """Draw the menu."""
        # Background
        self.screen.fill((20, 20, 30))
        
        # Title
        title = self.font_title.render("PROJECT ARES", True, (100, 200, 255))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 120))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_subtitle.render("AI Responsive Enemy System", True, (180, 180, 180))
        subtitle_rect = subtitle.get_rect(center=(self.screen.get_width() // 2, 170))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Draw all buttons
        for button in self.buttons.values():
            button.draw(self.screen)
        
        # Footer
        footer = pygame.font.Font(None, 18).render(
            "Educational project for AI coursework", True, (100, 100, 100)
        )
        footer_rect = footer.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 30))
        self.screen.blit(footer, footer_rect)

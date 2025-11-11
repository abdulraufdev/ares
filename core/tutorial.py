"""Tutorial screen for Algorithm Arena."""
import pygame
from typing import Optional

class TutorialScreen:
    """Displays game instructions and help."""
    
    def __init__(self, screen: pygame.Surface):
        """Initialize tutorial screen."""
        self.screen = screen
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 26)
        self.font_large = pygame.font.Font(None, 42)
        
        # Back button
        self.back_button_rect = pygame.Rect(
            screen.get_width() // 2 - 100,
            screen.get_height() - 100,
            200,
            50
        )
    
    def handle_event(self, event: pygame.event.Event) -> str:
        """Handle input. Returns 'menu' if back button clicked, else 'tutorial'."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'menu'
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.back_button_rect.collidepoint(event.pos):
                    return 'menu'
        return 'tutorial'
    
    def draw(self):
        """Draw tutorial content."""
        # Background
        self.screen.fill((20, 20, 30))
        
        # Title
        title_y = 50
        title = self.font_large.render("HOW TO PLAY", True, (220, 220, 220))
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, title_y))
        
        # Content area (leave space at bottom for back button)
        content_y = 120
        line_spacing = 25
        
        sections = [
            ("OBJECTIVE", "Survive as long as possible! The enemy uses pathfinding algorithms to chase you."),
            ("MOVEMENT", "Click on adjacent nodes to move. Speed depends on edge weight."),
            ("ABILITIES", [
                "Q - Shield: Become invincible for 3 seconds (10s cooldown)",
                "W - Teleport: Jump to a nearby node (8s cooldown)",
                "E - Block Node: Place obstacle to trap enemy (12s cooldown)",
                "R - Increase Weight: Make paths costly for enemy (6s cooldown, 5s duration)"
            ]),
            ("ALGORITHMS", [
                "1 - BFS: Slower enemy, explores breadth-first",
                "2 - DFS: Slower enemy, explores depth-first",
                "3 - UCS: Medium speed, considers edge weights",
                "4 - Greedy: Faster enemy, rushes toward goal",
                "5 - A*: Medium speed, optimal pathfinding"
            ]),
            ("CONTROLS", [
                "Click: Move to adjacent node",
                "Hover: See node details",
                "SPACE: Pause game",
                "ESC: Return to menu"
            ]),
            ("STRATEGY", "Use low-weight paths for quick escapes. Trap the enemy by blocking nodes or increasing weights. Save shield for emergencies!")
        ]
        
        y_offset = content_y
        
        for section_title, section_content in sections:
            # Check if we're running out of space
            if y_offset > self.screen.get_height() - 200:
                # Show indicator that there's more content
                more_text = self.font_small.render("(Scroll up to see more)", True, (150, 150, 150))
                self.screen.blit(more_text, (100, y_offset))
                break
            
            # Section header
            header = self.font_medium.render(section_title, True, (100, 200, 255))
            self.screen.blit(header, (100, y_offset))
            y_offset += 35
            
            # Section content
            if isinstance(section_content, list):
                for item in section_content:
                    text = self.font_small.render(f"  • {item}", True, (220, 220, 220))
                    self.screen.blit(text, (120, y_offset))
                    y_offset += line_spacing
            else:
                # Wrap long text
                words = section_content.split()
                line = ""
                for word in words:
                    test_line = line + word + " "
                    if self.font_small.size(test_line)[0] > self.screen.get_width() - 240:
                        text = self.font_small.render(line, True, (220, 220, 220))
                        self.screen.blit(text, (120, y_offset))
                        y_offset += line_spacing
                        line = word + " "
                    else:
                        line = test_line
                if line:
                    text = self.font_small.render(line, True, (220, 220, 220))
                    self.screen.blit(text, (120, y_offset))
                    y_offset += line_spacing
            
            y_offset += 15  # Space between sections
        
        # Back button
        self._draw_back_button()
    
    def _draw_back_button(self):
        """Draw the back button at the bottom."""
        # Button background
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.back_button_rect.collidepoint(mouse_pos)
        
        button_color = (120, 120, 140) if is_hovered else (100, 100, 120)
        pygame.draw.rect(self.screen, button_color, self.back_button_rect)
        pygame.draw.rect(self.screen, (150, 150, 170), self.back_button_rect, 2)
        
        # Button text
        text = self.font_medium.render("BACK TO MENU", True, (220, 220, 220))
        text_rect = text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(text, text_rect)

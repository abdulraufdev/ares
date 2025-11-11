"""Main entry point for Project ARES."""
import pygame
import sys
from config import *
from core.grid import Grid
from core.models import Agent
from core.gameplay import Game
from core.graphics import Renderer
from core.ui import UIHandler

class GameState:
    """Enum for game states."""
    MENU = "menu"
    PLAYING = "playing"
    VICTORY = "victory"
    DEFEAT = "defeat"

def draw_menu(screen: pygame.Surface, font_large: pygame.font.Font, font: pygame.font.Font) -> None:
    """Draw the algorithm selection menu."""
    screen.fill(COLOR_BACKGROUND)
    
    # Title
    title = font_large.render("Project ARES - Algorithm Arena", True, COLOR_TEXT)
    title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
    screen.blit(title, title_rect)
    
    # Instructions
    instructions = [
        "Select an algorithm to begin:",
        "",
        "1. BFS - Breadth-First Search",
        "2. DFS - Depth-First Search",
        "3. UCS - Uniform Cost Search",
        "4. Greedy - Greedy Best-First",
        "5. A* - A* Search",
        "",
        "Controls:",
        "SPACE - Pause/Unpause",
        "Hover over adjacent nodes for info",
        "",
        "Press 1-5 to start"
    ]
    
    y_offset = 180
    for line in instructions:
        text = font.render(line, True, COLOR_TEXT)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
        screen.blit(text, text_rect)
        y_offset += 30

def main():
    """Main game loop."""
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Project ARES - AI Responsive Enemy System")
    clock = pygame.time.Clock()
    
    # Fonts for menu
    font = pygame.font.SysFont('Consolas', 14)
    font_large = pygame.font.SysFont('Consolas', 20)
    
    # Game state
    game_state = GameState.MENU
    game = None
    renderer = None
    ui_handler = UIHandler()
    paused = False
    last_enemy_move_time = 0
    
    # Main loop
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if game_state == GameState.MENU:
                    # Algorithm selection
                    selected_algo = None
                    if event.key == pygame.K_1:
                        selected_algo = 'BFS'
                    elif event.key == pygame.K_2:
                        selected_algo = 'DFS'
                    elif event.key == pygame.K_3:
                        selected_algo = 'UCS'
                    elif event.key == pygame.K_4:
                        selected_algo = 'Greedy'
                    elif event.key == pygame.K_5:
                        selected_algo = 'A*'
                    
                    if selected_algo:
                        # Initialize new game
                        grid = Grid(GRID_WIDTH, GRID_HEIGHT, obstacle_ratio=OBSTACLE_RATIO, seed=DEFAULT_SEED)
                        
                        # Get opposite corner positions
                        player_start, enemy_start = grid.get_opposite_corners()
                        
                        player = Agent(name="Player", pos=player_start, stamina=100, hp=100)
                        enemy = Agent(name="Enemy", pos=enemy_start, stamina=100, hp=100)
                        
                        game = Game(grid, player, enemy)
                        renderer = Renderer(screen, grid)
                        
                        # Compute initial enemy path
                        game.compute_path(selected_algo)
                        
                        game_state = GameState.PLAYING
                        paused = False
                        last_enemy_move_time = current_time
                
                elif game_state == GameState.PLAYING:
                    # Handle in-game input
                    ui_state = ui_handler.handle_keypress(event.key)
                    if ui_state.paused is not None:
                        paused = ui_state.paused
                
                elif game_state in [GameState.VICTORY, GameState.DEFEAT]:
                    # Return to menu on any key
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        game_state = GameState.MENU
        
        # Render based on state
        if game_state == GameState.MENU:
            draw_menu(screen, font_large, font)
        
        elif game_state == GameState.PLAYING and game:
            # Update animations
            player_completed = game.update_movement(game.player, current_time)
            enemy_completed = game.update_movement(game.enemy, current_time)
            
            # Handle player arrival
            if player_completed:
                game.on_player_arrival(current_time)
            
            # Handle enemy movement (with delay)
            if not paused and current_time - last_enemy_move_time > MOVE_DELAY_MS:
                if game.step_enemy_along_path(current_time):
                    last_enemy_move_time = current_time
            
            # Check for collision
            if game.check_collision():
                game.game_over = True
                game.defeat_reason = "Caught by enemy"
                game_state = GameState.DEFEAT
            
            # Render game
            renderer.draw_grid()
            renderer.draw_path(game.path)
            renderer.draw_agents(game.player, game.enemy, current_time)
            renderer.draw_pause_indicator(paused)
            
            # Handle tooltip
            mouse_pos = pygame.mouse.get_pos()
            hovered_node = ui_handler.get_hovered_node(mouse_pos, CELL_SIZE)
            if hovered_node:
                tooltip_content = ui_handler.generate_tooltip_content(
                    hovered_node, game.player, game.grid, game.current_algo
                )
                if tooltip_content:
                    renderer.set_tooltip(tooltip_content, mouse_pos)
                else:
                    renderer.hide_tooltip()
            else:
                renderer.hide_tooltip()
            
            renderer.draw_tooltip()
        
        elif game_state == GameState.VICTORY and game:
            renderer.draw_grid()
            renderer.draw_path(game.path)
            renderer.draw_agents(game.player, game.enemy, current_time)
            renderer.draw_victory_screen(game.stats, game.current_algo)
        
        elif game_state == GameState.DEFEAT and game:
            renderer.draw_grid()
            renderer.draw_path(game.path)
            renderer.draw_agents(game.player, game.enemy, current_time)
            renderer.draw_defeat_screen(game.stats, game.current_algo, game.defeat_reason)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
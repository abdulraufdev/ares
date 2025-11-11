"""Main entry point for Project ARES."""
import pygame
import sys
from config import *
from core.grid import Grid
from core.models import Agent
from core.gameplay import Game
from core.graphics import Renderer
from core.ui import UIHandler
from core.menu import MenuManager

def main():
    """Main game loop."""
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Algorithm Arena - AI Pathfinding Combat")
    clock = pygame.time.Clock()
    
    # Initialize menu manager
    menu = MenuManager(screen)
    game_state = 'menu'  # 'menu', 'tutorial', 'playing', 'paused'
    
    # Game components (will be initialized when game starts)
    grid = None
    player = None
    enemy = None
    game = None
    renderer = None
    ui_handler = None
    paused = False
    current_algo = 'BFS'
    last_move_time = 0
    game_start_time = 0
    
    # Main loop
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if game_state == 'tutorial':
                    # Exit tutorial with ENTER
                    if event.key == pygame.K_RETURN:
                        game_state = 'playing'
                        # Initialize game
                        grid = Grid(GRID_WIDTH, GRID_HEIGHT, obstacle_ratio=OBSTACLE_RATIO, seed=DEFAULT_SEED)
                        player = Agent(name="Player", pos=(2, 2), stamina=100, hp=100)
                        enemy = Agent(name="Enemy", pos=(GRID_WIDTH - 3, GRID_HEIGHT - 3), stamina=100, hp=100)
                        game = Game(grid, player, enemy)
                        renderer = Renderer(screen, grid)
                        ui_handler = UIHandler()
                        game.compute_path(current_algo)
                        game_start_time = current_time
                
                elif game_state == 'playing':
                    ui_state = ui_handler.handle_keypress(event.key)
                    
                    if ui_state.paused is not None:
                        paused = ui_state.paused
                        game_state = 'paused' if paused else 'playing'
                    
                    if ui_state.algo_key and ui_state.algo_key in ALGORITHMS:
                        current_algo = ALGORITHMS[ui_state.algo_key]
                        game.compute_path(current_algo)
                
                elif game_state == 'paused':
                    if event.key == pygame.K_SPACE:
                        paused = False
                        game_state = 'playing'
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == 'menu':
                    # Handle menu clicks
                    buttons = menu.draw_main_menu()
                    action = menu.handle_menu_click(event.pos, buttons)
                    if action == 'start':
                        game_state = 'tutorial'
                    elif action == 'tutorial':
                        game_state = 'tutorial'
                    elif action == 'quit':
                        running = False
                
                elif game_state == 'playing':
                    # Handle player movement clicks
                    grid_x = event.pos[0] // CELL_SIZE
                    grid_y = event.pos[1] // CELL_SIZE
                    grid_pos = (grid_x, grid_y)
                    game.handle_player_click(grid_pos)
        
        # Update and render based on game state
        if game_state == 'menu':
            menu.update_animation()
            menu.draw_main_menu()
        
        elif game_state == 'tutorial':
            menu.draw_tutorial()
        
        elif game_state == 'playing':
            # Update player movement
            game.update_player_movement()
            
            # Update enemy movement
            if current_time - last_move_time > MOVE_DELAY_MS:
                if game.step_along_path():
                    last_move_time = current_time
                    # Recompute path if enemy reached player
                    if game.enemy.pos == player.pos:
                        game.compute_path(current_algo)
            
            # Render
            renderer.draw_grid()
            renderer.draw_graph_nodes(player.pos, enemy.pos, game.player_target)
            renderer.draw_path(game.path)
            renderer.draw_agents(player, enemy)
            
            # Calculate game time
            game_time = current_time - game_start_time
            
            renderer.draw_labels(
                current_algo, 
                game.stats, 
                False,
                game_time,
                game.current_path_cost,
                len(game.enemy_path)
            )
        
        elif game_state == 'paused':
            # Render paused state (same as playing but with pause indicator)
            renderer.draw_grid()
            renderer.draw_graph_nodes(player.pos, enemy.pos, game.player_target)
            renderer.draw_path(game.path)
            renderer.draw_agents(player, enemy)
            
            game_time = current_time - game_start_time
            
            renderer.draw_labels(
                current_algo, 
                game.stats, 
                True,
                game_time,
                game.current_path_cost,
                len(game.enemy_path)
            )
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
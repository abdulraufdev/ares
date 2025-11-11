"""Main entry point for Project ARES."""
import pygame
import sys
from config import *
from core.grid import Grid
from core.models import Agent
from core.gameplay import Game
from core.graphics import Renderer
from core.ui import UIHandler

def main():
    """Main game loop."""
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Project ARES - AI Responsive Enemy System")
    clock = pygame.time.Clock()
    
    # Initialize components
    grid = Grid(GRID_WIDTH, GRID_HEIGHT, obstacle_ratio=OBSTACLE_RATIO, seed=DEFAULT_SEED)
    
    # Create agents
    player = Agent(name="Player", pos=(2, 2), stamina=100, hp=100)
    enemy = Agent(name="Enemy", pos=(GRID_WIDTH - 3, GRID_HEIGHT - 3), stamina=100, hp=100)
    
    # Initialize game systems
    game = Game(grid, player, enemy)
    renderer = Renderer(screen, grid)
    ui_handler = UIHandler()
    
    # Initial path computation
    game.compute_path('BFS')
    
    paused = False
    current_algo = 'BFS'
    last_move_time = 0
    
    # Main loop
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                ui_state = ui_handler.handle_keypress(event.key)
                
                if ui_state.paused is not None:
                    paused = ui_state.paused
                
                if ui_state.algo_key and ui_state.algo_key in ALGORITHMS:
                    current_algo = ALGORITHMS[ui_state.algo_key]
                    game.compute_path(current_algo)
        
        # Update game state
        if not paused and current_time - last_move_time > MOVE_DELAY_MS:
            if game.step_along_path():
                last_move_time = current_time
        
        # Render
        renderer.draw_grid()
        renderer.draw_path(game.path)
        renderer.draw_agents(player, enemy)
        renderer.draw_labels(current_algo, game.stats, paused)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
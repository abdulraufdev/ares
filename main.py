"""Main entry point for Project ARES."""
import pygame
import sys
from config import *
from core.grid import Grid
from core.models import Agent
from core.gameplay import Game
from core.graphics import Renderer
from core.ui import UIHandler
from core.menu import MainMenu
from core.tutorial import TutorialScreen
from core.arena_mode import ArenaMode

def run_classic_mode(screen, clock):
    """Run classic pathfinding visualization mode."""
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
                return 'quit'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'menu'
                
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
    
    return 'quit'

def main():
    """Main game loop with menu system."""
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Project ARES - AI Responsive Enemy System")
    clock = pygame.time.Clock()
    
    # Initialize menu and screens
    menu = MainMenu(screen)
    tutorial = TutorialScreen(screen)
    
    # Game state
    current_state = 'menu'  # 'menu', 'arena', 'classic', 'tutorial', 'quit'
    arena_mode = None
    
    # Main loop
    running = True
    while running:
        if current_state == 'quit':
            running = False
            continue
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            
            # Route events to current screen
            if current_state == 'menu':
                action = menu.handle_event(event)
                if action:
                    if action == 'arena':
                        arena_mode = ArenaMode(screen)
                        current_state = 'arena'
                    elif action == 'classic':
                        result = run_classic_mode(screen, clock)
                        current_state = result if result else 'menu'
                    elif action == 'tutorial':
                        current_state = 'tutorial'
                    elif action == 'quit':
                        running = False
            
            elif current_state == 'tutorial':
                result = tutorial.handle_event(event)
                if result == 'menu':
                    current_state = 'menu'
            
            elif current_state == 'arena':
                if arena_mode:
                    result = arena_mode.handle_event(event)
                    if result == 'menu':
                        current_state = 'menu'
                        arena_mode = None
        
        # Update
        if current_state == 'arena' and arena_mode:
            arena_mode.update()
        
        # Render
        if current_state == 'menu':
            menu.draw()
        elif current_state == 'tutorial':
            tutorial.draw()
        elif current_state == 'arena' and arena_mode:
            arena_mode.draw()
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
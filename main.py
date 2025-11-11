"""Main entry point for Project ARES."""
import pygame
import sys
from config import *
from core.grid import Grid
from core.models import Agent
from core.gameplay import Game
from core.graphics import Renderer
from core.ui import UIHandler
from core.themes import ThemeManager

def main():
    """Main game loop."""
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Algorithm Arena - ARES Combat")
    clock = pygame.time.Clock()
    
    # Initialize components
    grid = Grid(GRID_WIDTH, GRID_HEIGHT, obstacle_ratio=OBSTACLE_RATIO, seed=DEFAULT_SEED)
    theme_manager = ThemeManager()
    
    # Create agents with max HP
    player = Agent(name="Player", pos=(2, 2), stamina=100, hp=PLAYER_MAX_HP, max_hp=PLAYER_MAX_HP)
    enemy = Agent(name="Enemy", pos=(GRID_WIDTH - 3, GRID_HEIGHT - 3), stamina=100, 
                 hp=ENEMY_MAX_HP, max_hp=ENEMY_MAX_HP)
    
    # Initialize game systems
    game = Game(grid, player, enemy)
    renderer = Renderer(screen, grid, theme_manager)
    ui_handler = UIHandler()
    
    # Generate initial map and compute path
    current_algo = 'BFS'
    game.generate_map(current_algo, DEFAULT_SEED)
    renderer.nodes = game.nodes
    theme_manager.set_theme(current_algo)
    game.compute_path(current_algo)
    
    paused = False
    last_move_time = 0
    last_frame_time = pygame.time.get_ticks()
    
    # Main loop
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        dt = current_time - last_frame_time
        last_frame_time = current_time
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                ui_state = ui_handler.handle_keypress(event.key)
                
                # Pause toggle
                if ui_state.paused is not None:
                    paused = ui_state.paused
                
                # Algorithm change
                if ui_state.algo_key and ui_state.algo_key in ALGORITHMS:
                    current_algo = ALGORITHMS[ui_state.algo_key]
                    
                    # Reset agents and generate new map
                    game.reset_agents()
                    game.generate_map(current_algo, DEFAULT_SEED)
                    renderer.nodes = game.nodes
                    theme_manager.set_theme(current_algo)
                    
                    # Compute initial path
                    game.compute_path(current_algo)
                    
                    # Reset game state
                    game.game_over = False
                    game.winner = None
                    player.hp = PLAYER_MAX_HP
                    enemy.hp = ENEMY_MAX_HP
                
                # Ability use
                if ui_state.ability_key and not paused:
                    if ui_state.ability_key == 'shield':
                        if game.use_ability('shield', current_time):
                            renderer.particle_system.emit_shield(player.pos[0], player.pos[1], CELL_SIZE)
                    
                    elif ui_state.ability_key in ['teleport', 'block', 'weight']:
                        # These require mouse position, store for next click
                        pass
            
            elif event.type == pygame.MOUSEBUTTONDOWN and not paused:
                ui_state = ui_handler.handle_mouse_click(event.pos, CELL_SIZE)
                
                if ui_state.mouse_click:
                    target_pos = ui_state.mouse_click
                    
                    # Check if target is valid
                    if grid.in_bounds(target_pos):
                        # Move player to clicked position
                        if game.move_player_to(target_pos, current_algo):
                            pass
        
        # Update game state
        if not paused and not game.game_over:
            # Update shield status
            game.ability_manager.update_shield(player, current_time)
            
            # Continuous enemy pathfinding (FIX FOR THE BUG!)
            game.compute_enemy_path(current_algo, current_time)
            
            # Move agents along their paths
            if current_time - last_move_time > MOVE_DELAY_MS:
                # Move player
                if game.step_along_path():
                    last_move_time = current_time
                
                # Move enemy
                game.step_enemy(current_time)
            
            # Update combat
            game.update_combat(current_time)
        
        # Render
        renderer.draw_grid(current_algo)
        
        # Draw enemy path (in lighter color)
        if game.enemy_path:
            renderer.draw_path(game.enemy_path, current_algo)
        
        # Draw player path (on top)
        if game.path:
            renderer.draw_path(game.path, current_algo)
        
        renderer.draw_agents(player, enemy)
        renderer.draw_labels(current_algo, game.stats, paused, player, enemy)
        renderer.draw_ability_cooldowns(player, game.ability_manager, current_time)
        renderer.draw_particles(dt)
        
        # Draw game over screen
        if game.game_over:
            game_over_font = pygame.font.SysFont('Consolas', 48)
            winner_text = game_over_font.render(f"{game.winner} WINS!", True, (255, 255, 0))
            text_rect = winner_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            
            # Semi-transparent background
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            screen.blit(winner_text, text_rect)
            
            # Instructions
            restart_font = pygame.font.SysFont('Consolas', 20)
            restart_text = restart_font.render("Press any number key to restart", True, (200, 200, 200))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
"""Main entry point for Algorithm Arena."""
import pygame
import sys
from config import *
from core.menu import MainMenu, TutorialScreen, AlgorithmSelectionScreen, Button
from core.gameplay import GameSession
from core.graphics import GraphRenderer


def main():
    """Main game loop."""
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Algorithm Arena - Educational Pathfinding Game")
    clock = pygame.time.Clock()
    
    # Game state
    game_state = STATE_MENU
    selected_algorithm = None
    game_session = None
    renderer = None
    
    # UI components
    main_menu = MainMenu(WINDOW_WIDTH, WINDOW_HEIGHT)
    tutorial_screen = TutorialScreen(WINDOW_WIDTH, WINDOW_HEIGHT)
    algorithm_selection_screen = AlgorithmSelectionScreen(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    # End screen buttons
    button_width = 180
    button_height = 50
    button_y = WINDOW_HEIGHT // 2 + 200
    
    play_again_button = Button(
        WINDOW_WIDTH // 2 - button_width - 10,
        button_y,
        button_width,
        button_height,
        f'RETRY'
    )
    
    main_menu_button = Button(
        WINDOW_WIDTH // 2 + 10,
        button_y,
        button_width,
        button_height,
        'MAIN MENU'
    )
    
    # Main loop
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        delta_time = clock.get_time() / 1000.0
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif game_state == STATE_MENU:
                action, algorithm = main_menu.handle_event(event)
                if action == 'quit':
                    running = False
                elif action == 'tutorial':
                    game_state = STATE_TUTORIAL
                elif action == 'start':
                    game_state = STATE_ALGORITHM_SELECTION
            
            elif game_state == STATE_ALGORITHM_SELECTION:
                action, algorithm = algorithm_selection_screen.handle_event(event)
                if action == 'back':
                    game_state = STATE_MENU
                elif action == 'continue' and algorithm:
                    selected_algorithm = algorithm
                    game_session = GameSession(algorithm)
                    renderer = GraphRenderer(screen, algorithm)
                    game_state = STATE_PLAYING
            
            elif game_state == STATE_TUTORIAL:
                if tutorial_screen.handle_event(event):
                    game_state = STATE_MENU
            
            elif game_state == STATE_PLAYING:
                # Keyboard controls
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_session.toggle_pause()
                        game_state = STATE_PAUSED if game_session.paused else STATE_PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        # Return to menu
                        game_state = STATE_MENU
                        game_session = None
                        renderer = None
                
                # Mouse controls
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        game_session.handle_click(event.pos, current_time)
                
                # Hover for tooltip
                elif event.type == pygame.MOUSEMOTION:
                    if renderer and game_session:
                        hovered_node = game_session.graph.get_node_at_pos(event.pos)
                        renderer.set_tooltip(hovered_node, event.pos)
            
            elif game_state == STATE_PAUSED:
                # Keyboard controls
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_session.toggle_pause()
                        game_state = STATE_PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        # Return to menu
                        game_state = STATE_MENU
                        game_session = None
                        renderer = None
                
                # Hover for tooltip (works while paused!)
                elif event.type == pygame.MOUSEMOTION:
                    if renderer and game_session:
                        hovered_node = game_session.graph.get_node_at_pos(event.pos)
                        renderer.set_tooltip(hovered_node, event.pos)
            
            elif game_state in [STATE_VICTORY, STATE_DEFEAT]:
                # Update button text for play again
                play_again_button.text = f'RETRY - {selected_algorithm}'
                
                # Handle button clicks
                if play_again_button.handle_event(event):
                    # Restart with same algorithm
                    game_session = GameSession(selected_algorithm)
                    renderer = GraphRenderer(screen, selected_algorithm)
                    game_state = STATE_PLAYING
                
                if main_menu_button.handle_event(event):
                    game_state = STATE_MENU
                    game_session = None
                    renderer = None
        
        # Update game logic
        if game_state == STATE_PLAYING and game_session:
            game_session.update(current_time, delta_time)
            
            # Check for victory/defeat
            if game_session.is_victory:
                game_state = STATE_VICTORY
            elif game_session.is_defeat:
                game_state = STATE_DEFEAT
        
        # Rendering
        if game_state == STATE_MENU:
            main_menu.draw(screen)
        
        elif game_state == STATE_ALGORITHM_SELECTION:
            algorithm_selection_screen.draw(screen)
        
        elif game_state == STATE_TUTORIAL:
            tutorial_screen.draw(screen)
        
        elif game_state in [STATE_PLAYING, STATE_PAUSED] and game_session and renderer:
            # Draw game world
            renderer.draw_background()
            renderer.draw_edges(game_session.graph, game_session.enemy.path)
            renderer.draw_nodes(game_session.graph, game_session.player, game_session.enemy)
            
            # Draw queued path visualization
            renderer.draw_queued_path(screen, game_session.player)
            
            # Draw health bars
            player_hp = game_session.combat.player.get_health_percentage()
            enemy_hp = game_session.combat.enemy.get_health_percentage()
            renderer.draw_health_bars(
                game_session.player,
                game_session.enemy,
                player_hp,
                enemy_hp
            )
            
            # Draw UI
            renderer.draw_ui_panel(
                game_session.enemy.stats,
                game_session.paused,
                game_session.game_time
            )
            
            # Draw tooltip
            renderer.draw_tooltip()
        
        elif game_state == STATE_VICTORY and game_session and renderer:
            # Draw final game state in background
            renderer.draw_background()
            renderer.draw_edges(game_session.graph, game_session.enemy.path)
            renderer.draw_nodes(game_session.graph, game_session.player, game_session.enemy)
            
            # Draw victory screen
            player_stats = game_session.get_player_stats()
            enemy_stats = game_session.get_enemy_stats()
            victory_reason = getattr(game_session, 'victory_reason', "")
            renderer.draw_victory_screen(player_stats, enemy_stats, game_session.game_time, victory_reason)
            
            # Draw buttons
            button_font = pygame.font.SysFont('Arial', 16)
            play_again_button.draw(screen, button_font)
            main_menu_button.draw(screen, button_font)
        
        elif game_state == STATE_DEFEAT and game_session and renderer:
            # Draw final game state in background
            renderer.draw_background()
            renderer.draw_edges(game_session.graph, game_session.enemy.path)
            renderer.draw_nodes(game_session.graph, game_session.player, game_session.enemy)
            
            # Draw defeat screen
            player_stats = game_session.get_player_stats()
            enemy_stats = game_session.get_enemy_stats()
            renderer.draw_defeat_screen(player_stats, enemy_stats, game_session.game_time)
            
            # Draw buttons
            button_font = pygame.font.SysFont('Arial', 16)
            play_again_button.draw(screen, button_font)
            main_menu_button.draw(screen, button_font)
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

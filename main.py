"""Main entry point for Algorithm Arena (formerly Project ARES)."""
import pygame
import sys
import time
from config import *
from core.graph import Graph
from core.models import Agent
from core.gameplay import Game
from core.graphics import Renderer
from core.menu import MainMenu


def main():
    """Main game loop with menu system."""
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Algorithm Arena - Strategic Graph Traversal")
    clock = pygame.time.Clock()
    
    # Initialize menu
    menu = MainMenu(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    # Game state
    game: Game = None
    renderer = Renderer(screen)
    paused = False
    
    # Main loop
    running = True
    while running:
        current_time = time.time()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Menu handling
            if menu.state != MainMenu.STATE_PLAYING:
                command = menu.handle_event(event)
                if command == 'quit':
                    running = False
                elif command == 'start_game':
                    # Initialize game with selected algorithm
                    game = start_new_game(menu.selected_algo)
                    renderer.set_graph(game.graph)
            
            # Game handling
            elif menu.state == MainMenu.STATE_PLAYING and game:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Return to menu
                        menu.state = MainMenu.STATE_MENU
                        menu.reset()
                        game = None
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_RETURN:
                        if game.game_over:
                            # Return to menu after game over
                            menu.state = MainMenu.STATE_MENU
                            menu.reset()
                            game = None
                
                elif event.type == pygame.MOUSEMOTION:
                    # Update hover state
                    if not game.game_over:
                        hovered_node = renderer.get_node_at_pos(event.pos)
                        renderer.hovered_node = hovered_node
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not game.game_over and not paused:
                        # Player clicks to move
                        clicked_node = renderer.get_node_at_pos(event.pos)
                        if clicked_node and game.is_node_adjacent_to_player(clicked_node):
                            game.move_player_to_node(clicked_node)
        
        # Update game state
        if menu.state == MainMenu.STATE_PLAYING and game and not paused and not game.game_over:
            game.update_enemy(current_time)
            game.update_visualization_states()
            
            # Check survival time victory condition
            survival_time = game.get_survival_time()
            if survival_time >= SURVIVAL_TIME_SECONDS:
                game.game_over = True
                game.victory = True
        
        # Render
        if menu.state != MainMenu.STATE_PLAYING:
            menu.draw(screen)
        else:
            if game:
                # Draw game
                renderer.draw_graph()
                renderer.draw_graph_path(game.enemy_path)
                renderer.draw_labels(game.current_algo, game.stats, paused)
                
                # Draw hover tooltip
                if renderer.hovered_node and not game.game_over:
                    if game.is_node_adjacent_to_player(renderer.hovered_node):
                        renderer.draw_hover_tooltip(
                            renderer.hovered_node, 
                            game.current_algo, 
                            game.player.node_label
                        )
                
                # Draw game over screens
                if game.game_over:
                    survival_time = game.get_survival_time()
                    if game.victory:
                        renderer.draw_victory_screen(
                            game.current_algo, 
                            game.player, 
                            game.enemy, 
                            game.stats, 
                            survival_time
                        )
                    else:
                        renderer.draw_defeat_screen(
                            game.current_algo, 
                            game.player, 
                            game.enemy, 
                            game.stats, 
                            survival_time
                        )
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


def start_new_game(algo: str) -> Game:
    """Initialize a new game with the selected algorithm."""
    # Create graph
    graph = Graph(
        num_nodes=GRAPH_NUM_NODES, 
        width=WINDOW_WIDTH - 100, 
        height=WINDOW_HEIGHT - 150,
        seed=DEFAULT_SEED,
        topology=GRAPH_TOPOLOGY
    )
    
    # Get start and end nodes
    all_labels = graph.get_all_labels()
    start_label = all_labels[0]  # Node A
    end_label = all_labels[-1]   # Last node
    
    # Create agents
    start_node = graph.get_node(start_label)
    end_node = graph.get_node(end_label)
    
    player = Agent(
        name="Player", 
        pos=(0, 0),  # Legacy, not used
        stamina=100, 
        hp=PLAYER_MAX_HP,
        node_label=start_label
    )
    
    enemy = Agent(
        name="Enemy", 
        pos=(0, 0),  # Legacy, not used
        stamina=100, 
        hp=ENEMY_MAX_HP,
        node_label=end_label
    )
    
    # Initialize game
    game = Game(graph=graph, player=player, enemy=enemy, algo=algo)
    
    # Set initial visualization states
    start_node.occupied_by_player = True
    end_node.occupied_by_enemy = True
    
    # Compute initial enemy path
    game.compute_enemy_path()
    game.update_visualization_states()
    
    return game


if __name__ == "__main__":
    main()
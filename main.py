"""Main entry point for Project ARES."""
import pygame
import sys
from config import *
from core.graph import Graph
from core.models import Agent
from core.gameplay import Game
from core.graphics import Renderer
from core.ui import UIHandler


def main():
    """Main game loop."""
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Algorithm Arena - Beautiful Graph Visualization")
    clock = pygame.time.Clock()
    
    # Initialize with BFS algorithm
    current_algo = 'BFS'
    graph = Graph(NUM_NODES, seed=DEFAULT_SEED, layout_type=GRAPH_LAYOUTS[current_algo])
    
    # Create agents at first and last nodes
    player = Agent(name="Player", pos=0, stamina=100, hp=100)
    enemy = Agent(name="Enemy", pos=NUM_NODES - 1, stamina=100, hp=100)
    
    # Initialize game systems
    game = Game(graph, player, enemy)
    renderer = Renderer(screen, graph)
    ui_handler = UIHandler()
    
    # Initial path computation
    game.compute_player_path(current_algo)
    game.compute_enemy_path()
    renderer.set_theme(current_algo)
    renderer.set_enemy_path(game.enemy_path)
    
    paused = False
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
                    # Regenerate graph with appropriate layout for algorithm
                    graph = Graph(NUM_NODES, seed=DEFAULT_SEED, 
                                layout_type=GRAPH_LAYOUTS[current_algo])
                    
                    # Reset agents
                    player.pos = 0
                    enemy.pos = NUM_NODES - 1
                    
                    # Reinitialize systems
                    game.graph = graph
                    renderer.graph = graph
                    renderer.set_theme(current_algo)
                    
                    # Compute new path
                    game.compute_player_path(current_algo)
                    game.compute_enemy_path()
                    renderer.set_enemy_path(game.enemy_path)
                
                if ui_state.map_switch:
                    # Generate new map with same algorithm
                    import random
                    new_seed = random.randint(1, 10000)
                    graph = Graph(NUM_NODES, seed=new_seed, 
                                layout_type=GRAPH_LAYOUTS[current_algo])
                    
                    # Reset agents
                    player.pos = 0
                    enemy.pos = NUM_NODES - 1
                    
                    # Reinitialize systems
                    game.graph = graph
                    renderer.graph = graph
                    
                    # Compute new path
                    game.compute_player_path(current_algo)
                    game.compute_enemy_path()
                    renderer.set_enemy_path(game.enemy_path)
        
        # Update game state with dynamic animation speed
        if not paused:
            animation_speed_seconds = game.get_animation_speed()
            animation_delay_ms = animation_speed_seconds * 1000
            
            if current_time - last_move_time > animation_delay_ms:
                if game.step_along_path():
                    last_move_time = current_time
                    renderer.set_enemy_path(game.enemy_path)
        
        # Render
        renderer.draw_graph(game.visited_nodes)
        renderer.draw_agents(player, enemy)
        renderer.draw_labels(current_algo, game.stats, paused)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

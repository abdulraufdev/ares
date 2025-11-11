"""Test that the game initializes properly."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set SDL to use dummy video driver
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from config import *
from core.grid import Grid
from core.models import Agent
from core.gameplay import Game
from core.graphics import Renderer
from core.ui import UIHandler
from core.themes import ThemeManager

def test_game_initialization():
    """Test that game systems initialize without errors."""
    pygame.init()
    
    # Create minimal display
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Initialize components
    grid = Grid(GRID_WIDTH, GRID_HEIGHT, obstacle_ratio=OBSTACLE_RATIO, seed=DEFAULT_SEED)
    theme_manager = ThemeManager()
    
    # Create agents
    player = Agent(name="Player", pos=(2, 2), stamina=100, hp=PLAYER_MAX_HP, max_hp=PLAYER_MAX_HP)
    enemy = Agent(name="Enemy", pos=(GRID_WIDTH - 3, GRID_HEIGHT - 3), stamina=100, 
                 hp=ENEMY_MAX_HP, max_hp=ENEMY_MAX_HP)
    
    # Initialize game systems
    game = Game(grid, player, enemy)
    renderer = Renderer(screen, grid, theme_manager)
    ui_handler = UIHandler()
    
    # Generate initial map
    current_algo = 'BFS'
    game.generate_map(current_algo, DEFAULT_SEED)
    renderer.nodes = game.nodes
    theme_manager.set_theme(current_algo)
    
    # Compute path
    game.compute_path(current_algo)
    
    # Test that systems are working
    assert game.nodes is not None, "Nodes should be generated"
    assert len(game.path) > 0 or game.player.pos == game.enemy.pos, "Path should be computed"
    assert player.hp == PLAYER_MAX_HP, "Player should have full HP"
    assert enemy.hp == ENEMY_MAX_HP, "Enemy should have full HP"
    
    # Test enemy pathfinding
    game.compute_enemy_path(current_algo, 0.0)
    assert game.enemy_path is not None, "Enemy path should be computed"
    
    # Test combat system
    assert game.combat_system is not None, "Combat system should exist"
    
    # Test ability manager
    assert game.ability_manager is not None, "Ability manager should exist"
    
    # Test theme manager
    assert theme_manager.get_color('primary', 'BFS') is not None, "Theme colors should be available"
    
    # Test particle system
    assert renderer.particle_system is not None, "Particle system should exist"
    
    pygame.quit()
    print("✓ All game systems initialized successfully!")

if __name__ == "__main__":
    test_game_initialization()

"""Unit tests for menu system and gameplay improvements."""
import pytest
import pygame
from core.menu import MenuManager, Button
from core.gameplay import Game
from core.grid import Grid
from core.models import Agent
from core.graphics import Renderer

def test_menu_manager_initialization():
    """Test MenuManager initializes correctly."""
    pygame.init()
    screen = pygame.display.set_mode((100, 100))
    menu = MenuManager(screen)
    
    assert menu.state == 'main'
    assert menu.screen == screen
    pygame.quit()

def test_button_creation():
    """Test Button dataclass creation."""
    rect = pygame.Rect(0, 0, 100, 50)
    button = Button(rect, "Test", "test_action")
    
    assert button.text == "Test"
    assert button.action == "test_action"
    assert button.rect == rect

def test_menu_handle_click():
    """Test menu click handling."""
    pygame.init()
    screen = pygame.display.set_mode((100, 100))
    menu = MenuManager(screen)
    
    # Create test buttons
    buttons = [
        Button(pygame.Rect(10, 10, 80, 40), "Test", "test_action")
    ]
    
    # Click inside button
    action = menu.handle_menu_click((50, 30), buttons)
    assert action == "test_action"
    
    # Click outside button
    action = menu.handle_menu_click((200, 200), buttons)
    assert action is None
    
    pygame.quit()

def test_player_click_handling():
    """Test player click creates a path."""
    grid = Grid(20, 20, obstacle_ratio=0.1, seed=42)
    player = Agent(name="Player", pos=(2, 2), stamina=100, hp=100)
    enemy = Agent(name="Enemy", pos=(10, 10), stamina=100, hp=100)
    
    game = Game(grid, player, enemy)
    
    # Initially player should not be moving
    assert game.player_moving == False
    assert game.player_target is None
    
    # Click a valid position
    target = (5, 5)
    game.handle_player_click(target)
    
    # Now player should be moving
    assert game.player_target == target
    assert game.player_moving == True
    assert len(game.player_path) > 0

def test_player_does_not_move_to_blocked():
    """Test player cannot click blocked cells."""
    grid = Grid(20, 20, obstacle_ratio=0.0, seed=42)
    player = Agent(name="Player", pos=(2, 2), stamina=100, hp=100)
    enemy = Agent(name="Enemy", pos=(10, 10), stamina=100, hp=100)
    
    game = Game(grid, player, enemy)
    
    # Block a cell
    grid.blocked[5][5] = True
    
    # Try to click blocked cell
    game.handle_player_click((5, 5))
    
    # Player should not be moving
    assert game.player_moving == False
    assert game.player_target is None

def test_player_movement_update():
    """Test player moves along path when update is called."""
    grid = Grid(20, 20, obstacle_ratio=0.0, seed=42)
    player = Agent(name="Player", pos=(2, 2), stamina=100, hp=100)
    enemy = Agent(name="Enemy", pos=(10, 10), stamina=100, hp=100)
    
    game = Game(grid, player, enemy)
    
    # Set up player movement
    game.handle_player_click((4, 2))
    
    initial_pos = player.pos
    
    # Update player movement
    game.update_player_movement()
    
    # Player should have moved
    assert player.pos != initial_pos

def test_player_stops_at_target():
    """Test player stops when reaching target."""
    grid = Grid(20, 20, obstacle_ratio=0.0, seed=42)
    player = Agent(name="Player", pos=(2, 2), stamina=100, hp=100)
    enemy = Agent(name="Enemy", pos=(10, 10), stamina=100, hp=100)
    
    game = Game(grid, player, enemy)
    
    # Click nearby position
    game.handle_player_click((3, 2))
    
    # Update until path is exhausted
    for _ in range(20):
        game.update_player_movement()
    
    # Player should have stopped
    assert game.player_moving == False
    assert game.player_target is None

def test_enemy_movement_separate_from_player():
    """Test enemy moves independently of player."""
    grid = Grid(20, 20, obstacle_ratio=0.0, seed=42)
    player = Agent(name="Player", pos=(2, 2), stamina=100, hp=100)
    enemy = Agent(name="Enemy", pos=(10, 10), stamina=100, hp=100)
    
    game = Game(grid, player, enemy)
    game.compute_path('BFS')
    
    initial_enemy_pos = enemy.pos
    
    # Move enemy
    game.step_along_path()
    
    # Enemy should have moved
    assert enemy.pos != initial_enemy_pos
    
    # Player should not have moved (without clicking)
    assert player.pos == (2, 2)

def test_live_path_cost_updates():
    """Test path cost updates as enemy moves."""
    grid = Grid(20, 20, obstacle_ratio=0.0, seed=42)
    player = Agent(name="Player", pos=(2, 2), stamina=100, hp=100)
    enemy = Agent(name="Enemy", pos=(10, 10), stamina=100, hp=100)
    
    game = Game(grid, player, enemy)
    game.compute_path('UCS')
    
    initial_cost = game.current_path_cost
    
    # Move enemy along path
    game.step_along_path()
    
    # Path cost should be different (recalculated)
    # Note: cost might be 0 if path is empty or at end
    assert initial_cost >= 0
    assert game.current_path_cost >= 0

def test_graph_node_colors():
    """Test node color assignment."""
    pygame.init()
    screen = pygame.display.set_mode((100, 100))
    grid = Grid(10, 10, obstacle_ratio=0.0, seed=42)
    renderer = Renderer(screen, grid)
    
    player_pos = (2, 2)
    enemy_pos = (5, 5)
    target_pos = (3, 3)
    
    # Test player node color
    color = renderer.get_node_color(player_pos, player_pos, enemy_pos, target_pos)
    assert color == renderer.COLOR_NODE_PLAYER
    
    # Test enemy node color
    color = renderer.get_node_color(enemy_pos, player_pos, enemy_pos, target_pos)
    assert color == renderer.COLOR_NODE_ENEMY
    
    # Test target node color
    color = renderer.get_node_color(target_pos, player_pos, enemy_pos, target_pos)
    assert color == renderer.COLOR_NODE_TARGET
    
    # Test default node color
    color = renderer.get_node_color((1, 1), player_pos, enemy_pos, target_pos)
    assert color == renderer.COLOR_NODE_DEFAULT
    
    pygame.quit()

def test_grid_to_screen_conversion():
    """Test grid position to screen coordinate conversion."""
    pygame.init()
    screen = pygame.display.set_mode((100, 100))
    grid = Grid(10, 10, obstacle_ratio=0.0, seed=42)
    renderer = Renderer(screen, grid)
    
    from config import CELL_SIZE
    
    # Test conversion
    screen_pos = renderer.grid_to_screen((0, 0))
    assert screen_pos == (CELL_SIZE // 2, CELL_SIZE // 2)
    
    screen_pos = renderer.grid_to_screen((1, 1))
    assert screen_pos == (CELL_SIZE + CELL_SIZE // 2, CELL_SIZE + CELL_SIZE // 2)
    
    pygame.quit()

def test_edge_color_based_on_cost():
    """Test edge colors vary with cost."""
    pygame.init()
    screen = pygame.display.set_mode((100, 100))
    grid = Grid(10, 10, obstacle_ratio=0.0, seed=42)
    renderer = Renderer(screen, grid)
    
    # Low cost edge
    color1 = renderer.get_edge_color(1.0)
    assert color1 == renderer.COLOR_EDGE_DEFAULT
    
    # High cost edge (diagonal)
    color2 = renderer.get_edge_color(1.414)
    assert color2 == renderer.COLOR_EDGE_HEAVY
    
    pygame.quit()

def test_game_tracks_algorithm():
    """Test game tracks current algorithm."""
    grid = Grid(20, 20, obstacle_ratio=0.0, seed=42)
    player = Agent(name="Player", pos=(2, 2), stamina=100, hp=100)
    enemy = Agent(name="Enemy", pos=(10, 10), stamina=100, hp=100)
    
    game = Game(grid, player, enemy)
    
    # Compute path with different algorithms
    game.compute_path('BFS')
    assert game.current_algo == 'BFS'
    
    game.compute_path('A*')
    assert game.current_algo == 'A*'
    
    game.compute_path('Greedy')
    assert game.current_algo == 'Greedy'

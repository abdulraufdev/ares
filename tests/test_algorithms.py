"""Unit tests for pathfinding algorithms."""
import pytest
from core.grid import Grid
from core.models import Agent, MovementSegment
from core.gameplay import Game
from core.ui import UIHandler
from algorithms import bfs, dfs, ucs, greedy, astar
from config import get_animation_duration

def test_bfs_simple():
    """Test BFS on a simple grid."""
    grid = Grid(10, 10, obstacle_ratio=0.0, eight_connected=False)
    start = (0, 0)
    goal = (5, 5)
    
    path, stats = bfs.find_path(grid, start, goal)
    
    assert len(path) > 0
    assert path[0] == start
    assert path[-1] == goal
    assert stats.nodes_expanded > 0

def test_astar_same_start_goal():
    """Test A* when start equals goal."""
    grid = Grid(10, 10, obstacle_ratio=0.0)
    start = (3, 3)
    goal = (3, 3)
    
    path, stats = astar.find_path(grid, start, goal)
    
    assert len(path) == 1
    assert path[0] == start

def test_no_path_exists():
    """Test behavior when no path exists."""
    grid = Grid(10, 10, obstacle_ratio=0.0)
    
    # Block all cells around goal
    goal = (5, 5)
    for y in range(4, 7):
        for x in range(4, 7):
            if (x, y) != goal:
                grid.blocked[y][x] = True
    
    start = (0, 0)
    path, stats = bfs.find_path(grid, start, goal)
    
    assert len(path) == 0

def test_movement_interpolation_timing():
    """Test that movement segments calculate duration correctly based on weight."""
    # Test fast movement (weight 1-2)
    assert get_animation_duration(1.0) == 300
    assert get_animation_duration(2.0) == 300
    
    # Test medium movement (weight 3-5)
    assert get_animation_duration(3.0) == 600
    assert get_animation_duration(5.0) == 600
    
    # Test slow movement (weight 6-10)
    assert get_animation_duration(6.0) == 1200
    assert get_animation_duration(10.0) == 1200

def test_movement_segment_progress():
    """Test MovementSegment progress calculation."""
    segment = MovementSegment(
        origin_node=(0, 0),
        target_node=(1, 1),
        start_time=0.0,
        duration=1000.0,
        weight=1.0
    )
    
    # At start
    assert segment.get_progress(0.0) == 0.0
    
    # Halfway
    assert segment.get_progress(500.0) == 0.5
    
    # Complete
    assert segment.get_progress(1000.0) == 1.0
    
    # Past complete (should cap at 1.0)
    assert segment.get_progress(1500.0) == 1.0

def test_movement_segment_interpolation():
    """Test MovementSegment position interpolation."""
    segment = MovementSegment(
        origin_node=(0, 0),
        target_node=(10, 10),
        start_time=0.0,
        duration=1000.0,
        weight=1.0
    )
    
    # At start
    pos = segment.get_interpolated_pos(0.0)
    assert pos == (0.0, 0.0)
    
    # Halfway
    pos = segment.get_interpolated_pos(500.0)
    assert pos == (5.0, 5.0)
    
    # Complete
    pos = segment.get_interpolated_pos(1000.0)
    assert pos == (10.0, 10.0)

def test_opposite_corner_spawn():
    """Test that opposite corner spawn logic works correctly."""
    grid = Grid(20, 20, obstacle_ratio=0.1, seed=42)
    
    player_pos, enemy_pos = grid.get_opposite_corners()
    
    # Both should be passable
    assert grid.passable(player_pos)
    assert grid.passable(enemy_pos)
    
    # They should not be adjacent (Chebyshev distance > 1)
    px, py = player_pos
    ex, ey = enemy_pos
    distance = max(abs(ex - px), abs(ey - py))
    assert distance > 1
    
    # Player should be at lower sum (top-left-ish)
    # Enemy should be at higher sum (bottom-right-ish)
    assert px + py < ex + ey

def test_enemy_recalculation_trigger():
    """Test that enemy recalculates path only on player arrival."""
    grid = Grid(10, 10, obstacle_ratio=0.0)
    player_pos, enemy_pos = grid.get_opposite_corners()
    
    player = Agent(name="Player", pos=player_pos, stamina=100, hp=100)
    enemy = Agent(name="Enemy", pos=enemy_pos, stamina=100, hp=100)
    
    game = Game(grid, player, enemy)
    game.compute_path('BFS')
    
    initial_recalcs = game.stats.enemy_path_recalculations
    assert initial_recalcs == 1  # Initial path computation
    
    # Simulate player arrival at new node
    game.on_player_arrival(0.0)
    
    # Should have triggered one more recalculation
    assert game.stats.enemy_path_recalculations == initial_recalcs + 1

def test_tooltip_content_bfs():
    """Test tooltip content for BFS (should not show weights)."""
    grid = Grid(10, 10, obstacle_ratio=0.0)
    player = Agent(name="Player", pos=(5, 5), stamina=100, hp=100)
    
    ui = UIHandler()
    
    # Hover over adjacent node
    hovered = (6, 5)
    content = ui.generate_tooltip_content(hovered, player, grid, 'BFS')
    
    # Should have content
    assert len(content) > 0
    
    # Should show node info
    assert "Node" in content[0]
    
    # Should NOT show edge weight for BFS
    content_str = " ".join(content)
    assert "Edge Weight" not in content_str

def test_tooltip_content_astar():
    """Test tooltip content for A* (should show weights)."""
    grid = Grid(10, 10, obstacle_ratio=0.0)
    player = Agent(name="Player", pos=(5, 5), stamina=100, hp=100)
    
    ui = UIHandler()
    
    # Hover over adjacent node
    hovered = (6, 5)
    content = ui.generate_tooltip_content(hovered, player, grid, 'A*')
    
    # Should have content
    assert len(content) > 0
    
    # Should show edge weight for A*
    content_str = " ".join(content)
    assert "Edge Weight" in content_str

def test_tooltip_content_ucs():
    """Test tooltip content for UCS (should show weights)."""
    grid = Grid(10, 10, obstacle_ratio=0.0)
    player = Agent(name="Player", pos=(5, 5), stamina=100, hp=100)
    
    ui = UIHandler()
    
    # Hover over adjacent node
    hovered = (6, 5)
    content = ui.generate_tooltip_content(hovered, player, grid, 'UCS')
    
    # Should have content
    assert len(content) > 0
    
    # Should show edge weight for UCS
    content_str = " ".join(content)
    assert "Edge Weight" in content_str

def test_tooltip_excludes_current_player_node():
    """Test that tooltip's next options excludes the current player node."""
    grid = Grid(10, 10, obstacle_ratio=0.0)
    player = Agent(name="Player", pos=(5, 5), stamina=100, hp=100)
    
    ui = UIHandler()
    
    # Hover over adjacent node
    hovered = (6, 5)
    content = ui.generate_tooltip_content(hovered, player, grid, 'BFS')
    
    # Check that player's position is not in the next options
    content_str = " ".join(content)
    assert "(5,5)" not in content_str or "(5, 5)" not in content_str

def test_stats_tracking():
    """Test that stats are properly tracked during gameplay."""
    grid = Grid(10, 10, obstacle_ratio=0.0)
    player_pos, enemy_pos = grid.get_opposite_corners()
    
    player = Agent(name="Player", pos=player_pos, stamina=100, hp=100)
    enemy = Agent(name="Enemy", pos=enemy_pos, stamina=100, hp=100)
    
    game = Game(grid, player, enemy)
    game.compute_path('A*')
    
    # Should have enemy exploration stats
    assert game.stats.enemy_nodes_explored > 0
    assert game.stats.enemy_path_recalculations == 1
    
    # Start a movement
    if game.enemy.path:
        target = game.enemy.path[0]
        game.start_movement(game.enemy, target, 0.0)
        
        # Check movement segment is created
        assert game.enemy.in_transit
        assert game.enemy.movement_segment is not None

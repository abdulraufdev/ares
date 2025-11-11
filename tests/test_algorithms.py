"""Unit tests for pathfinding algorithms."""
import pytest
from core.grid import Grid
from algorithms import bfs, dfs, ucs, greedy, astar

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

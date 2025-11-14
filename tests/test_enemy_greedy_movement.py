"""Tests for pure greedy enemy AI movement (no pathfinding/lookahead)."""
import pytest
from core.node import Node
from core.gameplay import EnemyAI


class MockGraph:
    """Mock graph for testing."""
    def __init__(self, nodes):
        self.nodes = nodes
    
    def reset_all_nodes(self):
        for node in self.nodes:
            node.reset_pathfinding()


class TestGreedyLocalMinMovement:
    """Test Greedy (Local Min) pure greedy movement."""
    
    def test_picks_lowest_heuristic_neighbor(self):
        """Test that enemy picks neighbor with lowest heuristic value."""
        # Create nodes with specific heuristic values
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        n4 = Node("N4", (150, 150))
        
        # Set static heuristic values
        n1.heuristic = 100.0
        n2.heuristic = 12.0  # Lowest - should be picked even if dead-end
        n3.heuristic = 214.0
        n4.heuristic = 102.0
        
        # Connect nodes
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 3)
        n1.add_neighbor(n4, 7)
        
        graph = MockGraph([n1, n2, n3, n4])
        enemy = EnemyAI(n1, 'Greedy (Local Min)', graph)
        
        # Enemy should pick n2 (lowest heuristic)
        next_move = enemy.get_next_move(n4)  # Player is at n4
        assert next_move == n2, "Enemy should pick neighbor with lowest heuristic"
    
    def test_avoids_visited_nodes(self):
        """Test that enemy doesn't revisit nodes."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        
        n1.heuristic = 100.0
        n2.heuristic = 10.0  # Lowest
        n3.heuristic = 50.0
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n1, 'Greedy (Local Min)', graph)
        
        # Mark n2 as visited
        enemy.visited_nodes.add(n2)
        
        # Enemy should pick n3 (only unvisited neighbor)
        next_move = enemy.get_next_move(n3)
        assert next_move == n3, "Enemy should skip visited nodes"
    
    def test_gets_stuck_at_dead_end(self):
        """Test that enemy gets stuck when all neighbors are visited."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))  # Leaf node (dead-end)
        
        n1.heuristic = 100.0
        n2.heuristic = 10.0
        
        n1.add_neighbor(n2, 5)
        # n2 only has n1 as neighbor (dead-end)
        
        graph = MockGraph([n1, n2])
        enemy = EnemyAI(n2, 'Greedy (Local Min)', graph)  # Start at leaf
        
        # Mark n1 as visited (came from there)
        enemy.visited_nodes.add(n1)
        
        # Enemy should be stuck
        next_move = enemy.get_next_move(n1)
        assert next_move is None, "Enemy should return None when stuck"
        assert enemy.stuck == True, "Enemy should set stuck flag"


class TestGreedyLocalMaxMovement:
    """Test Greedy (Local Max) pure greedy movement."""
    
    def test_picks_highest_heuristic_neighbor(self):
        """Test that enemy picks neighbor with highest heuristic value."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        n4 = Node("N4", (150, 150))
        
        n1.heuristic = 100.0
        n2.heuristic = 12.0
        n3.heuristic = 214.0  # Highest - should be picked
        n4.heuristic = 102.0
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 3)
        n1.add_neighbor(n4, 7)
        
        graph = MockGraph([n1, n2, n3, n4])
        enemy = EnemyAI(n1, 'Greedy (Local Max)', graph)
        
        next_move = enemy.get_next_move(n4)
        assert next_move == n3, "Enemy should pick neighbor with highest heuristic"


class TestUCSMovement:
    """Test UCS pure greedy movement."""
    
    def test_picks_lowest_path_cost_neighbor(self):
        """Test that enemy picks neighbor with lowest path cost value."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        n4 = Node("N4", (150, 150))
        
        n1.path_cost = 100.0
        n2.path_cost = 5.0   # Lowest - should be picked even if dead-end
        n3.path_cost = 50.0
        n4.path_cost = 23.0
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 3)
        n1.add_neighbor(n4, 7)
        
        graph = MockGraph([n1, n2, n3, n4])
        enemy = EnemyAI(n1, 'UCS', graph)
        
        next_move = enemy.get_next_move(n4)
        assert next_move == n2, "Enemy should pick neighbor with lowest path cost"


class TestAStarMovement:
    """Test A* variants pure greedy movement."""
    
    def test_astar_local_min_picks_lowest_f_cost(self):
        """Test that A* (Local Min) picks neighbor with lowest f-cost (h + g)."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        
        # Set heuristic and path_cost
        n1.heuristic = 10.0
        n1.path_cost = 10.0
        # f_cost = 20.0
        
        n2.heuristic = 5.0
        n2.path_cost = 10.0
        # f_cost = 15.0 (lowest)
        
        n3.heuristic = 20.0
        n3.path_cost = 5.0
        # f_cost = 25.0
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 3)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n1, 'A* (Local Min)', graph)
        
        next_move = enemy.get_next_move(n3)
        assert next_move == n2, "Enemy should pick neighbor with lowest f-cost"
    
    def test_astar_local_max_picks_highest_f_cost(self):
        """Test that A* (Local Max) picks neighbor with highest f-cost."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        
        n1.heuristic = 10.0
        n1.path_cost = 10.0
        # f_cost = 20.0
        
        n2.heuristic = 5.0
        n2.path_cost = 10.0
        # f_cost = 15.0
        
        n3.heuristic = 20.0
        n3.path_cost = 5.0
        # f_cost = 25.0 (highest)
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 3)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n1, 'A* (Local Max)', graph)
        
        next_move = enemy.get_next_move(n3)
        assert next_move == n3, "Enemy should pick neighbor with highest f-cost"


class TestBFSDFSMovement:
    """Test BFS and DFS pure greedy movement."""
    
    def test_bfs_picks_first_unvisited_neighbor(self):
        """Test that BFS picks first unvisited neighbor (queue behavior)."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        n4 = Node("N4", (150, 150))
        
        # Order matters for BFS - should pick first in neighbors list
        n1.neighbors = [(n2, 5), (n3, 3), (n4, 7)]
        n2.neighbors = [(n1, 5)]
        n3.neighbors = [(n1, 3)]
        n4.neighbors = [(n1, 7)]
        
        graph = MockGraph([n1, n2, n3, n4])
        enemy = EnemyAI(n1, 'BFS', graph)
        
        next_move = enemy.get_next_move(n4)
        assert next_move == n2, "BFS should pick first unvisited neighbor"
    
    def test_dfs_picks_last_unvisited_neighbor(self):
        """Test that DFS picks last unvisited neighbor (stack behavior)."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        n4 = Node("N4", (150, 150))
        
        # Order matters for DFS - should pick last in neighbors list
        n1.neighbors = [(n2, 5), (n3, 3), (n4, 7)]
        n2.neighbors = [(n1, 5)]
        n3.neighbors = [(n1, 3)]
        n4.neighbors = [(n1, 7)]
        
        graph = MockGraph([n1, n2, n3, n4])
        enemy = EnemyAI(n1, 'DFS', graph)
        
        next_move = enemy.get_next_move(n4)
        assert next_move == n4, "DFS should pick last unvisited neighbor"


class TestEnemyStuckDetection:
    """Test enemy stuck detection and victory condition."""
    
    def test_enemy_stuck_flag_set_when_no_moves(self):
        """Test that stuck flag is set when enemy has no valid moves."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        
        n1.add_neighbor(n2, 5)
        
        graph = MockGraph([n1, n2])
        enemy = EnemyAI(n1, 'Greedy (Local Min)', graph)
        
        # Mark all neighbors as visited
        enemy.visited_nodes.add(n2)
        
        # Get next move should return None and set stuck
        next_move = enemy.get_next_move(n2)
        assert next_move is None
        assert enemy.stuck == True
    
    def test_enemy_returns_none_when_already_stuck(self):
        """Test that get_next_move returns None when enemy is already stuck."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        
        n1.add_neighbor(n2, 5)
        
        graph = MockGraph([n1, n2])
        enemy = EnemyAI(n1, 'Greedy (Local Min)', graph)
        
        # Manually set stuck
        enemy.stuck = True
        
        # Should return None immediately
        next_move = enemy.get_next_move(n2)
        assert next_move is None
    
    def test_can_walk_into_dead_end(self):
        """Test that enemy can walk into a dead-end based on greedy choice."""
        # This tests the key behavior: enemy MUST follow algorithm rules
        # even if it leads to a dead-end
        
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))  # Dead-end with low heuristic
        n3 = Node("N3", (300, 100))  # Path to player with high heuristic
        
        n1.heuristic = 100.0
        n2.heuristic = 12.0  # Lowest - enemy picks this (trap!)
        n3.heuristic = 102.0  # Higher but leads to player
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        # n2 is a leaf (only connects back to n1)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n1, 'Greedy (Local Min)', graph)
        
        # Enemy should pick n2 even though it's a dead-end
        # because it has the lowest heuristic
        next_move = enemy.get_next_move(n3)
        assert next_move == n2, "Enemy must pick lowest heuristic even if it's a dead-end"

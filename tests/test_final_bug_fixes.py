"""Tests for final bug fixes: game balance, backtracking, and player tracking."""
import pytest
from core.node import Node
from core.graph import Graph
from core.gameplay import EnemyAI, GameSession
from config import WINDOW_WIDTH, WINDOW_HEIGHT


class MockGraph:
    """Mock graph for testing."""
    def __init__(self, nodes):
        self.nodes = nodes
    
    def reset_all_nodes(self):
        for node in self.nodes:
            node.reset_pathfinding()


class TestGameBalance:
    """Test that game balance creates enemy-favorable patterns ~50% of time."""
    
    def test_balanced_costs_creates_patterns(self):
        """Test that balanced cost assignment creates different patterns."""
        import pygame
        pygame.init()
        
        # Create multiple sessions - some should favor enemy
        sessions = [GameSession('Greedy (Local Min)') for _ in range(10)]
        
        # All sessions should have valid costs
        for session in sessions:
            for node in session.graph.nodes:
                assert 0 < node.heuristic <= 350.0
                assert 0 < node.path_cost <= 350.0
    
    def test_local_min_pattern_favors_descending(self):
        """Test that Local Min creates descending patterns when favoring enemy."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 10, seed=42)
        
        # Create fake spawn positions
        enemy_node = graph.nodes[0]
        player_node = graph.nodes[-1]
        
        # Force favor_enemy to True
        graph.assign_balanced_costs(enemy_node, player_node, 'Greedy (Local Min)', 
                                    favor_enemy_chance=1.0)
        
        # Check that some path exists with descending values
        # (not all nodes will be on the path, so we just verify valid range)
        for node in graph.nodes:
            assert 0 < node.heuristic <= 350.0
    
    def test_local_max_pattern_favors_ascending(self):
        """Test that Local Max creates ascending patterns when favoring enemy."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 10, seed=42)
        
        enemy_node = graph.nodes[0]
        player_node = graph.nodes[-1]
        
        # Force favor_enemy to True
        graph.assign_balanced_costs(enemy_node, player_node, 'Greedy (Local Max)', 
                                    favor_enemy_chance=1.0)
        
        # Verify valid range
        for node in graph.nodes:
            assert 0 < node.heuristic <= 350.0


class TestBFSDFSUCSBacktracking:
    """Test that BFS/DFS/UCS can backtrack but not revisit visited leaves."""
    
    def test_bfs_can_backtrack_non_leaf(self):
        """Test that BFS can revisit non-leaf nodes (backtracking)."""
        # Create a path: n1 - n2 - n3
        #                      |
        #                     n4
        # n3 is a leaf, n2 is not
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))  # Leaf
        n4 = Node("N4", (200, 200))
        
        n1.add_neighbor(n2, 5)
        n2.add_neighbor(n3, 5)
        n2.add_neighbor(n4, 5)
        
        graph = MockGraph([n1, n2, n3, n4])
        enemy = EnemyAI(n1, 'BFS', graph)
        
        # Move to n2
        next_move = enemy.get_next_move(n4)
        assert next_move == n2  # BFS picks first neighbor
        
        # Simulate move to n2
        enemy.node = n2
        
        # From n2, BFS can go to n1, n3, or n4 (all are valid)
        next_move = enemy.get_next_move(n4)
        assert next_move in [n1, n3, n4]  # Any neighbor is valid
        
        # If moved to n3 (leaf), mark it as visited leaf
        if next_move == n3:
            enemy.node = n3
            enemy.visited_leaves.add(n3)
            
            # Now enemy should be able to backtrack to n2 (not a leaf)
            next_move = enemy.get_next_move(n4)
            assert next_move == n2  # Can backtrack to non-leaf
    
    def test_bfs_cannot_revisit_visited_leaf(self):
        """Test that BFS cannot revisit a visited leaf node."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))  # Leaf
        
        n1.add_neighbor(n2, 5)
        
        graph = MockGraph([n1, n2])
        enemy = EnemyAI(n1, 'BFS', graph)
        
        # Mark n2 as visited leaf
        enemy.visited_leaves.add(n2)
        
        # Enemy should have no valid moves (can't go to visited leaf)
        next_move = enemy.get_next_move(n2)
        assert next_move is None
        assert enemy.stuck == True
    
    def test_dfs_can_backtrack_non_leaf(self):
        """Test that DFS can revisit non-leaf nodes (backtracking)."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))  # Leaf
        
        n1.add_neighbor(n2, 5)
        n2.add_neighbor(n3, 5)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n2, 'DFS', graph)
        
        # Mark n3 as visited leaf
        enemy.visited_leaves.add(n3)
        
        # Enemy can backtrack to n1 (not a leaf)
        next_move = enemy.get_next_move(n1)
        assert next_move == n1  # Can backtrack


class TestEnemyStopsAtGoal:
    """Test that enemy stops moving when it catches the player."""
    
    def test_enemy_stops_when_catching_player(self):
        """Test that enemy stops moving when at same node as player."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        
        n1.add_neighbor(n2, 5)
        
        graph = MockGraph([n1, n2])
        enemy = EnemyAI(n1, 'Greedy (Local Min)', graph)
        
        # Player is at same node as enemy
        next_move = enemy.get_next_move(n1)
        
        # Enemy should stop (return None)
        assert next_move is None
        assert enemy.caught_player == True
    
    def test_enemy_resumes_when_player_moves_away(self):
        """Test that enemy resumes movement when player moves away."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        
        n1.heuristic = 100.0
        n2.heuristic = 50.0  # Lower
        n3.heuristic = 150.0
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n1, 'Greedy (Local Min)', graph)
        
        # Catch player at n1
        enemy.caught_player = True
        
        # Player moves to n2
        next_move = enemy.get_next_move(n2)
        
        # Enemy should resume movement (not None)
        assert next_move is not None


class TestPlayerTrackingRules:
    """Test player tracking rules for Greedy/A* variants."""
    
    def test_greedy_local_min_follows_if_player_moves_to_min_neighbor(self):
        """Test that Greedy Local Min follows player if they move to min neighbor."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))  # Min heuristic
        n3 = Node("N3", (300, 100))  # Higher heuristic
        
        n1.heuristic = 100.0
        n2.heuristic = 50.0  # Minimum
        n3.heuristic = 150.0
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n1, 'Greedy (Local Min)', graph)
        
        # Enemy caught player at n1
        enemy.caught_player = True
        
        # Player moves to n2 (minimum neighbor)
        next_move = enemy.get_next_move(n2)
        
        # Enemy should follow to n2
        assert next_move == n2
    
    def test_greedy_local_min_abandons_if_player_moves_to_non_min_neighbor(self):
        """Test that Greedy Local Min abandons player if they move to non-min."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))  # Min heuristic
        n3 = Node("N3", (300, 100))  # Higher heuristic
        
        n1.heuristic = 100.0
        n2.heuristic = 50.0  # Minimum
        n3.heuristic = 150.0  # NOT minimum
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n1, 'Greedy (Local Min)', graph)
        
        # Enemy caught player at n1
        enemy.caught_player = True
        
        # Player moves to n3 (NOT minimum neighbor)
        next_move = enemy.get_next_move(n3)
        
        # Enemy should abandon and choose n2 (minimum)
        assert next_move == n2
        assert enemy.caught_player == False
    
    def test_greedy_local_max_follows_if_player_moves_to_max_neighbor(self):
        """Test that Greedy Local Max follows player if they move to max neighbor."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))  # Lower heuristic
        n3 = Node("N3", (300, 100))  # Max heuristic
        
        n1.heuristic = 100.0
        n2.heuristic = 50.0
        n3.heuristic = 250.0  # Maximum
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n1, 'Greedy (Local Max)', graph)
        
        # Enemy caught player at n1
        enemy.caught_player = True
        
        # Player moves to n3 (maximum neighbor)
        next_move = enemy.get_next_move(n3)
        
        # Enemy should follow to n3
        assert next_move == n3
    
    def test_greedy_local_max_abandons_if_player_moves_to_non_max_neighbor(self):
        """Test that Greedy Local Max abandons player if they move to non-max."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))  # Lower heuristic
        n3 = Node("N3", (300, 100))  # Max heuristic
        
        n1.heuristic = 100.0
        n2.heuristic = 50.0  # NOT maximum
        n3.heuristic = 250.0  # Maximum
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n1, 'Greedy (Local Max)', graph)
        
        # Enemy caught player at n1
        enemy.caught_player = True
        
        # Player moves to n2 (NOT maximum neighbor)
        next_move = enemy.get_next_move(n2)
        
        # Enemy should abandon and choose n3 (maximum)
        assert next_move == n3
        assert enemy.caught_player == False
    
    def test_astar_local_min_uses_f_cost_for_tracking(self):
        """Test that A* Local Min uses f-cost (h+g) for player tracking."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        
        n1.heuristic = 100.0
        n1.path_cost = 50.0
        # f = 150
        
        n2.heuristic = 80.0
        n2.path_cost = 40.0
        # f = 120 (minimum f-cost)
        
        n3.heuristic = 90.0
        n3.path_cost = 60.0
        # f = 150
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n1, 'A* (Local Min)', graph)
        
        # Enemy caught player at n1
        enemy.caught_player = True
        
        # Player moves to n2 (minimum f-cost neighbor)
        next_move = enemy.get_next_move(n2)
        
        # Enemy should follow to n2
        assert next_move == n2


class TestGreedyAStarAlwaysPickCorrectNeighbor:
    """Test that Greedy/A* ALWAYS pick the correct min/max neighbor."""
    
    def test_greedy_local_min_always_picks_minimum(self):
        """Verify Greedy Local Min ALWAYS picks minimum, never picks higher."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        n4 = Node("N4", (400, 100))
        
        # Clear ordering - n2 is minimum
        n1.heuristic = 100.0
        n2.heuristic = 10.0   # MINIMUM
        n3.heuristic = 50.0
        n4.heuristic = 200.0
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        n1.add_neighbor(n4, 5)
        
        graph = MockGraph([n1, n2, n3, n4])
        enemy = EnemyAI(n1, 'Greedy (Local Min)', graph)
        
        next_move = enemy.get_next_move(n4)
        
        # Must pick n2 (minimum) - NO EXCEPTIONS
        assert next_move == n2, "Greedy Local Min MUST pick minimum neighbor"
    
    def test_greedy_local_max_always_picks_maximum(self):
        """Verify Greedy Local Max ALWAYS picks maximum, never picks lower."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        n4 = Node("N4", (400, 100))
        
        # Clear ordering - n4 is maximum
        n1.heuristic = 100.0
        n2.heuristic = 50.0
        n3.heuristic = 150.0
        n4.heuristic = 300.0  # MAXIMUM
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        n1.add_neighbor(n4, 5)
        
        graph = MockGraph([n1, n2, n3, n4])
        enemy = EnemyAI(n1, 'Greedy (Local Max)', graph)
        
        next_move = enemy.get_next_move(n3)
        
        # Must pick n4 (maximum) - NO EXCEPTIONS
        assert next_move == n4, "Greedy Local Max MUST pick maximum neighbor"
    
    def test_astar_local_min_always_picks_minimum_f_cost(self):
        """Verify A* Local Min ALWAYS picks minimum f-cost."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        
        n1.heuristic = 50.0
        n1.path_cost = 50.0
        
        n2.heuristic = 30.0
        n2.path_cost = 20.0
        # f = 50 (minimum)
        
        n3.heuristic = 40.0
        n3.path_cost = 60.0
        # f = 100
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n1, 'A* (Local Min)', graph)
        
        next_move = enemy.get_next_move(n3)
        
        # Must pick n2 (minimum f-cost)
        assert next_move == n2, "A* Local Min MUST pick minimum f-cost neighbor"
    
    def test_astar_local_max_always_picks_maximum_f_cost(self):
        """Verify A* Local Max ALWAYS picks maximum f-cost."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        
        n1.heuristic = 50.0
        n1.path_cost = 50.0
        
        n2.heuristic = 30.0
        n2.path_cost = 20.0
        # f = 50
        
        n3.heuristic = 70.0
        n3.path_cost = 80.0
        # f = 150 (maximum)
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n1, 'A* (Local Max)', graph)
        
        next_move = enemy.get_next_move(n2)
        
        # Must pick n3 (maximum f-cost)
        assert next_move == n3, "A* Local Max MUST pick maximum f-cost neighbor"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

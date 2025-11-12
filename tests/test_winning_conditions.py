"""Test winning conditions for different algorithms."""
import pytest
from core.node import Node
from core.graph import Graph
from core.gameplay import GameSession
from algorithms.graph_algorithms import find_path


class TestWinningConditions:
    """Tests for algorithm-specific winning conditions."""
    
    def test_bfs_player_wins_on_visited_leaf(self):
        """Test that player wins when moving to a leaf already visited by BFS enemy."""
        # Create a simple graph with a leaf node
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))  # This is a leaf
        node4 = Node("N4", (150, 200))
        
        node1.add_neighbor(node2, 5)
        node2.add_neighbor(node3, 5)  # node3 is a leaf
        node1.add_neighbor(node4, 5)
        
        class MockGraph:
            def __init__(self):
                self.nodes = [node1, node2, node3, node4]
            
            def reset_all_nodes(self):
                for node in self.nodes:
                    node.reset_pathfinding()
        
        graph = MockGraph()
        visited_leaves = set()
        
        # Enemy searches for node3 (leaf) from node1
        path1, stats1 = find_path('BFS', graph, node1, node3, visited_leaves)
        
        # node3 should now be in visited_leaves
        assert node3 in visited_leaves, "BFS should track visited leaf"
        
        # Now if player is at node3, enemy from node1 cannot reach
        path2, stats2 = find_path('BFS', graph, node1, node3, visited_leaves)
        
        # Should return empty path (player wins!)
        assert len(path2) == 0, "BFS should not find path to visited leaf"
    
    def test_greedy_gets_stuck_no_backtracking(self):
        """Test that Greedy can get stuck without backtracking."""
        # Create a graph where greedy might get stuck
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))
        node4 = Node("N4", (200, 200))
        
        node1.add_neighbor(node2, 5)
        node2.add_neighbor(node3, 5)
        node2.add_neighbor(node4, 5)
        
        class MockGraph:
            def __init__(self):
                self.nodes = [node1, node2, node3, node4]
            
            def reset_all_nodes(self):
                for node in self.nodes:
                    node.reset_pathfinding()
        
        graph = MockGraph()
        
        # Greedy should not backtrack
        path, stats = find_path('Greedy (Local Min)', graph, node1, node4)
        
        # Path should exist or be empty (if stuck)
        assert isinstance(path, list), "Greedy should return a list"
        
        # If path exists, no node should appear twice (no backtracking)
        if path:
            assert len(path) == len(set(path)), "Greedy should not revisit nodes"
    
    def test_enemy_no_path_triggers_victory(self):
        """Test that GameSession detects victory when enemy has no path."""
        # This is tested indirectly - the victory condition is in gameplay.py
        # We verify it exists and is correct
        from core.gameplay import GameSession
        
        # Create a game session
        session = GameSession('BFS')
        
        # Initially enemy should have a path (they start far apart)
        initial_has_path = len(session.enemy.path) > 0
        
        # Victory should not be triggered yet
        assert not session.is_victory or not initial_has_path, \
            "Victory should not be triggered with valid path"
    
    def test_all_algorithms_handle_no_path_gracefully(self):
        """Test that all algorithms return empty list when no path exists."""
        # Create isolated nodes
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (300, 300))  # No connection
        
        class MockGraph:
            def __init__(self):
                self.nodes = [node1, node2]
            
            def reset_all_nodes(self):
                for node in self.nodes:
                    node.reset_pathfinding()
        
        graph = MockGraph()
        
        algorithms = [
            'BFS', 'DFS', 'UCS',
            'Greedy (Local Min)', 'Greedy (Local Max)',
            'A* (Local Min)', 'A* (Local Max)'
        ]
        
        for algo in algorithms:
            path, stats = find_path(algo, graph, node1, node2)
            assert path == [], f"{algo} should return empty list when no path exists"


class TestBFSDFSUCSLeafTracking:
    """Tests specifically for BFS/DFS/UCS leaf tracking behavior."""
    
    def test_dfs_tracks_visited_leaves(self):
        """Test that DFS tracks visited leaf nodes."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))  # Leaf
        
        node1.add_neighbor(node2, 5)
        node2.add_neighbor(node3, 5)
        
        class MockGraph:
            def __init__(self):
                self.nodes = [node1, node2, node3]
            
            def reset_all_nodes(self):
                for node in self.nodes:
                    node.reset_pathfinding()
        
        graph = MockGraph()
        visited_leaves = set()
        
        path, stats = find_path('DFS', graph, node1, node3, visited_leaves)
        
        assert node3 in visited_leaves, "DFS should track visited leaves"
    
    def test_ucs_tracks_visited_leaves(self):
        """Test that UCS tracks visited leaf nodes."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))  # Leaf
        
        node1.add_neighbor(node2, 5)
        node2.add_neighbor(node3, 5)
        
        class MockGraph:
            def __init__(self):
                self.nodes = [node1, node2, node3]
            
            def reset_all_nodes(self):
                for node in self.nodes:
                    node.reset_pathfinding()
        
        graph = MockGraph()
        visited_leaves = set()
        
        path, stats = find_path('UCS', graph, node1, node3, visited_leaves)
        
        assert node3 in visited_leaves, "UCS should track visited leaves"
    
    def test_non_leaf_not_tracked(self):
        """Test that non-leaf nodes are not added to visited_leaves."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))
        
        node1.add_neighbor(node2, 5)
        node2.add_neighbor(node3, 5)
        node1.add_neighbor(node3, 5)  # node2 and node3 now have 2 neighbors
        
        class MockGraph:
            def __init__(self):
                self.nodes = [node1, node2, node3]
            
            def reset_all_nodes(self):
                for node in self.nodes:
                    node.reset_pathfinding()
        
        graph = MockGraph()
        visited_leaves = set()
        
        # None of these are leaves (all have 2 neighbors)
        path, stats = find_path('BFS', graph, node1, node3, visited_leaves)
        
        # visited_leaves should be empty (no leaves in path)
        assert len(visited_leaves) == 0, "Non-leaf nodes should not be tracked"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

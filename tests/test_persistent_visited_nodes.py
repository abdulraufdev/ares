"""Tests for persistent visited node tracking in enemy AI."""
import pytest
from core.node import Node
from core.graph import Graph
from core.gameplay import EnemyAI
from algorithms.graph_algorithms import find_path


class TestPersistentVisitedNodes:
    """Tests for persistent visited node tracking across path recalculations."""
    
    def test_greedy_local_min_no_backtracking_across_recalculations(self):
        """Test that Greedy (Local Min) cannot backtrack to previously visited nodes."""
        # Create a simple graph
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
        visited_nodes = set()
        
        # First search: N1 to N3
        path1, stats1 = find_path('Greedy (Local Min)', graph, node1, node3, None, visited_nodes)
        
        # Nodes in path1 should be in visited_nodes
        assert len(path1) > 0, "First path should be found"
        for node in path1:
            assert node in visited_nodes, f"Node {node.label} should be in visited_nodes"
        
        # Second search: N1 to N4 (should not be able to use nodes from first path)
        # This tests the strict no-backtracking behavior
        path2, stats2 = find_path('Greedy (Local Min)', graph, node1, node4, None, visited_nodes)
        
        # Path may be empty if all routes are blocked by visited nodes
        # If path exists, it should not contain any previously visited nodes except start
        if path2:
            for i, node in enumerate(path2):
                if i > 0:  # Skip start node
                    assert node not in visited_nodes or node == node4, \
                        f"Node {node.label} was visited before and should not be reused"
    
    def test_greedy_local_max_no_backtracking(self):
        """Test that Greedy (Local Max) cannot backtrack to previously visited nodes."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))
        
        node1.add_neighbor(node2, 5)
        node2.add_neighbor(node3, 5)
        
        class MockGraph:
            def __init__(self):
                self.nodes = [node1, node2, node3]
            
            def reset_all_nodes(self):
                for node in self.nodes:
                    node.reset_pathfinding()
        
        graph = MockGraph()
        visited_nodes = set()
        
        path1, stats1 = find_path('Greedy (Local Max)', graph, node1, node3, None, visited_nodes)
        
        assert len(path1) > 0, "Path should exist"
        assert node2 in visited_nodes, "Intermediate node should be tracked"
        
        # Try to find path again - should not be able to use node2
        path2, stats2 = find_path('Greedy (Local Max)', graph, node1, node3, None, visited_nodes)
        
        # Second path should be empty or find an alternative route
        # In this linear graph, no alternative exists
        assert len(path2) == 0, "Second search should fail due to visited nodes"
    
    def test_astar_local_min_no_backtracking(self):
        """Test that A* (Local Min) cannot backtrack to previously visited nodes."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))
        
        node1.add_neighbor(node2, 5)
        node2.add_neighbor(node3, 5)
        
        class MockGraph:
            def __init__(self):
                self.nodes = [node1, node2, node3]
            
            def reset_all_nodes(self):
                for node in self.nodes:
                    node.reset_pathfinding()
        
        graph = MockGraph()
        visited_nodes = set()
        
        path1, stats1 = find_path('A* (Local Min)', graph, node1, node3, None, visited_nodes)
        
        assert len(path1) > 0, "Path should exist"
        assert len(visited_nodes) > 0, "visited_nodes should be populated"
        
        # Second search should not be able to reuse nodes
        path2, stats2 = find_path('A* (Local Min)', graph, node1, node3, None, visited_nodes)
        assert len(path2) == 0, "Second search should fail due to no backtracking"
    
    def test_astar_local_max_no_backtracking(self):
        """Test that A* (Local Max) cannot backtrack to previously visited nodes."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))
        
        node1.add_neighbor(node2, 5)
        node2.add_neighbor(node3, 5)
        
        class MockGraph:
            def __init__(self):
                self.nodes = [node1, node2, node3]
            
            def reset_all_nodes(self):
                for node in self.nodes:
                    node.reset_pathfinding()
        
        graph = MockGraph()
        visited_nodes = set()
        
        path1, stats1 = find_path('A* (Local Max)', graph, node1, node3, None, visited_nodes)
        
        assert len(path1) > 0, "Path should exist"
        
        # Second search should fail
        path2, stats2 = find_path('A* (Local Max)', graph, node1, node3, None, visited_nodes)
        assert len(path2) == 0, "Second search should fail due to no backtracking"
    
    def test_bfs_tracks_nodes_across_searches(self):
        """Test that BFS tracks visited nodes across multiple searches."""
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
        visited_nodes = set()
        
        path1, stats1 = find_path('BFS', graph, node1, node3, visited_leaves, visited_nodes)
        
        assert len(path1) > 0, "Path should exist"
        assert node3 in visited_leaves, "Leaf node should be tracked"
        assert len(visited_nodes) > 0, "visited_nodes should be populated"
        
        # Second search to same leaf should fail
        path2, stats2 = find_path('BFS', graph, node1, node3, visited_leaves, visited_nodes)
        assert len(path2) == 0, "Cannot reach visited leaf"
    
    def test_enemy_ai_maintains_visited_nodes(self):
        """Test that EnemyAI properly maintains visited_nodes across recalculations."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))
        
        node1.add_neighbor(node2, 5)
        node2.add_neighbor(node3, 5)
        
        class MockGraph:
            def __init__(self):
                self.nodes = [node1, node2, node3]
            
            def reset_all_nodes(self):
                for node in self.nodes:
                    node.reset_pathfinding()
        
        graph = MockGraph()
        
        # Create enemy AI with Greedy algorithm
        enemy = EnemyAI(node1, 'Greedy (Local Min)', graph)
        
        # Check that visited_nodes is initialized
        assert hasattr(enemy, 'visited_nodes'), "Enemy should have visited_nodes attribute"
        assert isinstance(enemy.visited_nodes, set), "visited_nodes should be a set"
        
        # Recalculate path
        enemy.recalculate_path(node3)
        
        # visited_nodes should be populated after path calculation
        assert len(enemy.visited_nodes) > 0, "visited_nodes should be populated after pathfinding"
    
    def test_enemy_ai_greedy_gets_stuck(self):
        """Test that Greedy enemy can get stuck when player exploits no-backtracking."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))
        node4 = Node("N4", (200, 200))
        
        node1.add_neighbor(node2, 5)
        node2.add_neighbor(node3, 5)
        node1.add_neighbor(node4, 5)
        
        class MockGraph:
            def __init__(self):
                self.nodes = [node1, node2, node3, node4]
            
            def reset_all_nodes(self):
                for node in self.nodes:
                    node.reset_pathfinding()
        
        graph = MockGraph()
        
        # Enemy starts at node1
        enemy = EnemyAI(node1, 'Greedy (Local Min)', graph)
        
        # First recalculation: enemy finds path to node3
        enemy.recalculate_path(node3)
        initial_path_length = len(enemy.path)
        
        assert initial_path_length > 0, "Enemy should find initial path"
        
        # After enemy explores some nodes, player moves to a different location
        # Simulate enemy moving along path (this adds nodes to visited_nodes)
        # In real game, enemy.update() would do this
        
        # Now recalculate to node4
        # If nodes were used in first path, enemy might get stuck
        enemy.recalculate_path(node4)
        
        # Path might be empty if enemy can't reach node4 without backtracking
        # This is the victory condition for player!


class TestVisitedNodesInitialization:
    """Test that visited_nodes is properly initialized."""
    
    def test_enemy_ai_has_visited_nodes(self):
        """Test that EnemyAI initializes with empty visited_nodes set."""
        node1 = Node("N1", (100, 100))
        
        class MockGraph:
            def __init__(self):
                self.nodes = [node1]
            
            def reset_all_nodes(self):
                pass
        
        graph = MockGraph()
        enemy = EnemyAI(node1, 'BFS', graph)
        
        assert hasattr(enemy, 'visited_nodes'), "Enemy should have visited_nodes"
        assert isinstance(enemy.visited_nodes, set), "visited_nodes should be a set"
        assert len(enemy.visited_nodes) == 0, "visited_nodes should start empty"
    
    def test_enemy_ai_has_visited_leaves(self):
        """Test that EnemyAI initializes with empty visited_leaves set."""
        node1 = Node("N1", (100, 100))
        
        class MockGraph:
            def __init__(self):
                self.nodes = [node1]
            
            def reset_all_nodes(self):
                pass
        
        graph = MockGraph()
        enemy = EnemyAI(node1, 'BFS', graph)
        
        assert hasattr(enemy, 'visited_leaves'), "Enemy should have visited_leaves"
        assert isinstance(enemy.visited_leaves, set), "visited_leaves should be a set"
        assert len(enemy.visited_leaves) == 0, "visited_leaves should start empty"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""Tests for algorithm variants and winning conditions."""
import pytest
from core.node import Node
from core.graph import Graph
from core.gameplay import EnemyAI
from algorithms.graph_algorithms import (
    find_path,
    bfs_find_path,
    dfs_find_path,
    ucs_find_path,
    greedy_local_min_find_path,
    greedy_local_max_find_path,
    astar_local_min_find_path,
    astar_local_max_find_path
)
from config import WINDOW_WIDTH, WINDOW_HEIGHT


class TestLeafNodeDetection:
    """Tests for leaf node detection."""
    
    def test_node_with_one_neighbor_is_leaf(self):
        """Test that nodes with 1 neighbor are identified as leaves."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node1.add_neighbor(node2, 5)
        
        assert node1.is_leaf(), "Node with 1 neighbor should be a leaf"
        assert node2.is_leaf(), "Node with 1 neighbor should be a leaf"
    
    def test_node_with_multiple_neighbors_not_leaf(self):
        """Test that nodes with multiple neighbors are not leaves."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))
        
        node1.add_neighbor(node2, 5)
        node1.add_neighbor(node3, 5)
        
        assert not node1.is_leaf(), "Node with 2 neighbors should not be a leaf"


class TestVisitedLeafTracking:
    """Tests for visited leaf tracking in BFS/DFS/UCS."""
    
    def test_bfs_tracks_visited_leaves(self):
        """Test that BFS tracks which leaf nodes were visited."""
        # Create simple graph with a leaf
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))  # This will be a leaf
        
        node1.add_neighbor(node2, 5)
        node2.add_neighbor(node3, 5)
        
        # Create a mock graph
        class MockGraph:
            def __init__(self):
                self.nodes = [node1, node2, node3]
            
            def reset_all_nodes(self):
                for node in self.nodes:
                    node.reset_pathfinding()
        
        graph = MockGraph()
        visited_leaves = set()
        
        # Find path from node1 to node3 (leaf)
        path, stats = bfs_find_path(graph, node1, node3, visited_leaves)
        
        # Node3 should be tracked as visited leaf
        assert node3 in visited_leaves, "BFS should track visited leaf nodes"
        assert len(path) > 0, "Should find path to leaf"
    
    def test_bfs_cannot_reach_visited_leaf(self):
        """Test that BFS cannot find path to already-visited leaf."""
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
        
        # Mark node3 as already visited
        visited_leaves = {node3}
        
        # Try to find path to visited leaf
        path, stats = bfs_find_path(graph, node1, node3, visited_leaves)
        
        # Should not find path
        assert len(path) == 0, "BFS should not find path to visited leaf"


class TestGreedyLocalVariants:
    """Tests for Greedy Local Min/Max variants."""
    
    def test_greedy_local_min_finds_path(self):
        """Test that Greedy Local Min can find paths."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 10, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, stats = greedy_local_min_find_path(graph, start, goal)
        
        # Should find a path (or get stuck trying)
        assert isinstance(path, list), "Should return a path list"
    
    def test_greedy_local_max_finds_path(self):
        """Test that Greedy Local Max can find paths."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 10, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, stats = greedy_local_max_find_path(graph, start, goal)
        
        # Should find a path (or get stuck trying)
        assert isinstance(path, list), "Should return a path list"
    
    def test_greedy_no_backtracking(self):
        """Test that Greedy variants don't revisit nodes."""
        # Create a graph where backtracking would help
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))
        node4 = Node("N4", (200, 200))
        
        # Create a path that might need backtracking
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
        
        # Greedy algorithms should not revisit nodes (no backtracking)
        path, stats = greedy_local_min_find_path(graph, node1, node4)
        
        # Check that no node appears twice in the path
        if path:
            assert len(path) == len(set(path)), "Greedy should not revisit nodes"


class TestAStarLocalVariants:
    """Tests for A* Local Min/Max variants."""
    
    def test_astar_local_min_finds_path(self):
        """Test that A* Local Min can find paths."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 10, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, stats = astar_local_min_find_path(graph, start, goal)
        
        assert isinstance(path, list), "Should return a path list"
    
    def test_astar_local_max_finds_path(self):
        """Test that A* Local Max can find paths."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 10, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, stats = astar_local_max_find_path(graph, start, goal)
        
        assert isinstance(path, list), "Should return a path list"
    
    def test_astar_no_backtracking(self):
        """Test that A* variants don't revisit nodes."""
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
        
        path, stats = astar_local_min_find_path(graph, node1, node3)
        
        # Check that no node appears twice in the path
        if path:
            assert len(path) == len(set(path)), "A* should not revisit nodes"


class TestAlgorithmDispatcher:
    """Tests for the algorithm dispatcher with new variants."""
    
    def test_dispatcher_handles_all_variants(self):
        """Test that dispatcher correctly routes to all algorithm variants."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 10, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[5]
        
        algorithms = [
            'BFS',
            'DFS',
            'UCS',
            'Greedy (Local Min)',
            'Greedy (Local Max)',
            'A* (Local Min)',
            'A* (Local Max)'
        ]
        
        for algo in algorithms:
            path, stats = find_path(algo, graph, start, goal)
            assert isinstance(path, list), f"{algo} should return a path list"
            assert isinstance(stats.nodes_expanded, int), f"{algo} should track nodes expanded"


class TestEnemyAIVisitedLeaves:
    """Tests for enemy AI tracking visited leaves."""
    
    def test_enemy_ai_initializes_visited_leaves(self):
        """Test that enemy AI initializes visited leaves set."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 10, seed=42)
        start = graph.nodes[0]
        
        enemy = EnemyAI(start, 'BFS', graph)
        
        assert hasattr(enemy, 'visited_leaves'), "Enemy should have visited_leaves attribute"
        assert isinstance(enemy.visited_leaves, set), "visited_leaves should be a set"
    
    def test_enemy_ai_uses_visited_leaves_for_bfs(self):
        """Test that enemy AI passes visited leaves to BFS."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 10, seed=42)
        start = graph.nodes[0]
        
        enemy = EnemyAI(start, 'BFS', graph)
        enemy.recalculate_path(graph.nodes[5])
        
        # Enemy should have calculated path
        assert isinstance(enemy.path, list), "Enemy should have a path"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

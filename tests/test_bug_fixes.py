"""Tests for bug fixes in Algorithm Arena game."""
import pytest
from core.node import Node
from core.graph import Graph
from core.gameplay import PlayerEntity, EnemyAI, GameSession
from algorithms.graph_algorithms import find_path
from config import WINDOW_WIDTH, WINDOW_HEIGHT, NUM_NODES, ENEMY_SPEEDS


class TestBugFix1_EnemySpeed:
    """Tests for Bug Fix 1: Enemy Speed adjustments."""
    
    def test_enemy_speeds_updated(self):
        """Test that enemy speeds are set to new values."""
        assert ENEMY_SPEEDS['BFS'] == 800, "BFS speed should be 800ms"
        assert ENEMY_SPEEDS['DFS'] == 800, "DFS speed should be 800ms"
        assert ENEMY_SPEEDS['UCS'] == 700, "UCS speed should be 700ms"
        assert ENEMY_SPEEDS['Greedy (Local Min)'] == 600, "Greedy (Local Min) speed should be 600ms"
        assert ENEMY_SPEEDS['Greedy (Local Max)'] == 600, "Greedy (Local Max) speed should be 600ms"
        assert ENEMY_SPEEDS['A* (Local Min)'] == 700, "A* (Local Min) speed should be 700ms"
        assert ENEMY_SPEEDS['A* (Local Max)'] == 700, "A* (Local Max) speed should be 700ms"


class TestBugFix2_EnemyStickingBug:
    """Tests for Bug Fix 2: Player can escape when enemy is on same node."""
    
    def test_player_can_move_to_adjacent_regardless_of_enemy(self):
        """Test that player can move to adjacent nodes even when enemy is on same node."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node1.add_neighbor(node2, 5)
        
        player = PlayerEntity(node1)
        
        # Player should be able to move to adjacent node
        assert player.can_move_to(node2), "Player should be able to move to adjacent node"
        
    def test_player_cannot_move_to_non_adjacent(self):
        """Test that player cannot move to non-adjacent nodes."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))
        node1.add_neighbor(node2, 5)
        
        player = PlayerEntity(node1)
        
        # Player should NOT be able to move to non-adjacent node
        assert not player.can_move_to(node3), "Player should not be able to move to non-adjacent node"


class TestBugFix3_GraphStructure:
    """Tests for Bug Fix 3: Graph structure with max 3 neighbors."""
    
    def test_graph_has_correct_node_count(self):
        """Test that graph has 25-30 nodes."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_NODES, seed=42)
        assert 25 <= len(graph.nodes) <= 30, f"Graph should have 25-30 nodes, got {len(graph.nodes)}"
    
    def test_max_neighbors_is_3(self):
        """Test that no node has more than 3 neighbors."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_NODES, seed=42)
        
        for node in graph.nodes:
            num_neighbors = len(node.neighbors)
            assert num_neighbors <= 3, f"Node {node.label} has {num_neighbors} neighbors, max should be 3"
    
    def test_min_neighbors_is_1(self):
        """Test that all nodes have at least 1 neighbor."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_NODES, seed=42)
        
        for node in graph.nodes:
            num_neighbors = len(node.neighbors)
            assert num_neighbors >= 1, f"Node {node.label} has {num_neighbors} neighbors, min should be 1"
    
    def test_graph_is_connected(self):
        """Test that graph is still fully connected with max 3 neighbors."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_NODES, seed=42)
        
        # BFS from first node
        visited = set()
        queue = [graph.nodes[0]]
        visited.add(graph.nodes[0])
        
        while queue:
            current = queue.pop(0)
            for neighbor, _ in current.neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        # All nodes should be reachable
        assert len(visited) == len(graph.nodes), "Graph should be fully connected"
    
    def test_some_dead_ends_exist(self):
        """Test that some nodes have only 1 neighbor (dead-ends for strategy)."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_NODES, seed=42)
        
        dead_end_count = sum(1 for node in graph.nodes if len(node.neighbors) == 1)
        assert dead_end_count >= 1, "Graph should have at least 1 dead-end node"


class TestBugFix4_PathCostDisplay:
    """Tests for Bug Fix 4: Enemy final path cost showing correctly."""
    
    def test_bfs_calculates_path_cost(self):
        """Test that BFS calculates path cost."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, stats = find_path('BFS', graph, start, goal)
        
        assert len(path) > 0, "Path should be found"
        assert stats.path_cost > 0, "BFS should calculate path cost"
        
        # Manually calculate path cost to verify
        expected_cost = 0.0
        for i in range(len(path) - 1):
            weight = path[i].get_weight_to(path[i + 1])
            expected_cost += weight
        
        assert abs(stats.path_cost - expected_cost) < 0.01, "Path cost should match manual calculation"
    
    def test_dfs_calculates_path_cost(self):
        """Test that DFS calculates path cost."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, stats = find_path('DFS', graph, start, goal)
        
        assert len(path) > 0, "Path should be found"
        assert stats.path_cost > 0, "DFS should calculate path cost"
    
    def test_ucs_calculates_path_cost(self):
        """Test that UCS calculates path cost."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, stats = find_path('UCS', graph, start, goal)
        
        assert len(path) > 0, "Path should be found"
        assert stats.path_cost > 0, "UCS should calculate path cost"
    
    def test_greedy_calculates_path_cost(self):
        """Test that Greedy calculates path cost."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, stats = find_path('Greedy', graph, start, goal)
        
        assert len(path) > 0, "Path should be found"
        assert stats.path_cost > 0, "Greedy should calculate path cost"
    
    def test_astar_calculates_path_cost(self):
        """Test that A* calculates path cost."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, stats = find_path('A*', graph, start, goal)
        
        assert len(path) > 0, "Path should be found"
        assert stats.path_cost > 0, "A* should calculate path cost"
    
    def test_same_start_goal_has_zero_cost(self):
        """Test that path cost is 0 when start equals goal."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 10, seed=42)
        node = graph.nodes[0]
        
        for algo in ['BFS', 'DFS', 'UCS', 'Greedy (Local Min)', 'Greedy (Local Max)', 
                     'A* (Local Min)', 'A* (Local Max)']:
            path, stats = find_path(algo, graph, node, node)
            assert stats.path_cost == 0.0, f"{algo} should have 0 path cost when start equals goal"
    
    def test_game_session_has_enemy_stats(self):
        """Test that GameSession.get_enemy_stats() returns path_cost."""
        session = GameSession('BFS')
        enemy_stats = session.get_enemy_stats()
        
        assert 'path_cost' in enemy_stats, "Enemy stats should include path_cost"
        assert isinstance(enemy_stats['path_cost'], (int, float)), "path_cost should be numeric"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

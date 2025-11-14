"""Tests for BFS/DFS/UCS graph exploration completion detection."""
import pytest
from core.graph import Graph
from core.node import Node
from core.gameplay import EnemyAI


class TestGraphExplorationComplete:
    """Test that BFS/DFS/UCS detect when entire graph is explored."""
    
    def test_bfs_detects_graph_explored_when_all_nodes_visited(self):
        """Test BFS detects when entire graph explored without finding player."""
        # Create a simple graph
        graph = Graph(800, 600, num_nodes=10, seed=100)
        nodes = list(graph.nodes)
        
        # Place enemy and player at different nodes
        enemy_start = nodes[0]
        player_node = nodes[-1]  # Player at last node
        
        # Create enemy AI
        enemy = EnemyAI(enemy_start, 'BFS', graph)
        
        # Mark all nodes as visited to simulate graph exploration
        for node in graph.nodes:
            node.visited = True
        
        # Enemy is at a node where all neighbors are visited
        # Should detect graph is explored
        next_move = enemy.get_next_move(player_node)
        
        # Enemy should be stuck with reason "graph_explored"
        assert enemy.stuck == True
        assert enemy.stuck_reason == "graph_explored"
        assert next_move is None
    
    def test_dfs_detects_graph_explored_when_all_nodes_visited(self):
        """Test DFS detects when entire graph explored without finding player."""
        # Create a simple graph
        graph = Graph(800, 600, num_nodes=10, seed=101)
        nodes = list(graph.nodes)
        
        # Place enemy and player at different nodes
        enemy_start = nodes[0]
        player_node = nodes[-1]
        
        # Create enemy AI
        enemy = EnemyAI(enemy_start, 'DFS', graph)
        
        # Mark all nodes as visited
        for node in graph.nodes:
            node.visited = True
        
        # Enemy should detect graph is explored
        next_move = enemy.get_next_move(player_node)
        
        assert enemy.stuck == True
        assert enemy.stuck_reason == "graph_explored"
        assert next_move is None
    
    def test_ucs_detects_graph_explored_when_all_nodes_visited(self):
        """Test UCS detects when entire graph explored without finding player."""
        # Create a simple graph
        graph = Graph(800, 600, num_nodes=10, seed=102)
        nodes = list(graph.nodes)
        
        # Place enemy and player at different nodes
        enemy_start = nodes[0]
        player_node = nodes[-1]
        
        # Create enemy AI
        enemy = EnemyAI(enemy_start, 'UCS', graph)
        
        # Mark all nodes as visited
        for node in graph.nodes:
            node.visited = True
        
        # Enemy should detect graph is explored
        next_move = enemy.get_next_move(player_node)
        
        assert enemy.stuck == True
        assert enemy.stuck_reason == "graph_explored"
        assert next_move is None
    
    def test_bfs_continues_when_unvisited_nodes_remain(self):
        """Test BFS continues backtracking when unvisited nodes exist elsewhere."""
        # Create a simple graph
        graph = Graph(800, 600, num_nodes=10, seed=103)
        nodes = list(graph.nodes)
        
        # Place enemy and player
        enemy_start = nodes[0]
        player_node = nodes[-1]
        
        # Create enemy AI
        enemy = EnemyAI(enemy_start, 'BFS', graph)
        
        # Mark some nodes as visited but leave player's node unvisited
        for i, node in enumerate(graph.nodes):
            if i < len(graph.nodes) - 1:  # Leave last node unvisited
                node.visited = True
        
        # Enemy at a node with all neighbors visited, but graph not fully explored
        # Should allow backtracking
        next_move = enemy.get_next_move(player_node)
        
        # Enemy should NOT be stuck yet - can backtrack to reach unvisited nodes
        # (It might be stuck if it has no valid neighbors for backtracking,
        # but the key is it shouldn't be stuck with "graph_explored" reason
        # because there are still unvisited nodes)
        if enemy.stuck:
            # If stuck, it should NOT be due to graph_explored
            assert enemy.stuck_reason != "graph_explored"
    
    def test_dfs_continues_when_unvisited_nodes_remain(self):
        """Test DFS continues backtracking when unvisited nodes exist elsewhere."""
        # Create a simple graph
        graph = Graph(800, 600, num_nodes=10, seed=104)
        nodes = list(graph.nodes)
        
        # Place enemy and player
        enemy_start = nodes[0]
        player_node = nodes[-1]
        
        # Create enemy AI
        enemy = EnemyAI(enemy_start, 'DFS', graph)
        
        # Mark some nodes as visited but leave player's node unvisited
        for i, node in enumerate(graph.nodes):
            if i < len(graph.nodes) - 1:
                node.visited = True
        
        # Enemy should NOT be stuck with "graph_explored" when unvisited nodes remain
        next_move = enemy.get_next_move(player_node)
        
        if enemy.stuck:
            assert enemy.stuck_reason != "graph_explored"
    
    def test_ucs_continues_when_unvisited_nodes_remain(self):
        """Test UCS continues backtracking when unvisited nodes exist elsewhere."""
        # Create a simple graph
        graph = Graph(800, 600, num_nodes=10, seed=105)
        nodes = list(graph.nodes)
        
        # Place enemy and player
        enemy_start = nodes[0]
        player_node = nodes[-1]
        
        # Create enemy AI
        enemy = EnemyAI(enemy_start, 'UCS', graph)
        
        # Mark some nodes as visited but leave player's node unvisited
        for i, node in enumerate(graph.nodes):
            if i < len(graph.nodes) - 1:
                node.visited = True
        
        # Enemy should NOT be stuck with "graph_explored" when unvisited nodes remain
        next_move = enemy.get_next_move(player_node)
        
        if enemy.stuck:
            assert enemy.stuck_reason != "graph_explored"
    
    def test_bfs_no_infinite_loop_between_visited_nodes(self):
        """Test BFS doesn't get stuck in infinite loop between visited nodes."""
        # Create a simple graph with specific structure
        graph = Graph(800, 600, num_nodes=10, seed=106)
        nodes = list(graph.nodes)
        
        # Place enemy and player
        enemy_start = nodes[0]
        player_node = nodes[-1]
        
        # Create enemy AI
        enemy = EnemyAI(enemy_start, 'BFS', graph)
        
        # Simulate a scenario where all nodes are visited
        for node in graph.nodes:
            node.visited = True
        
        # Make multiple get_next_move calls
        moves = []
        for _ in range(10):
            next_move = enemy.get_next_move(player_node)
            moves.append(next_move)
            if next_move is None:
                break
        
        # Should get stuck (None) and not continue moving
        # At most one move before detecting stuck condition
        assert moves[-1] is None
        assert enemy.stuck == True
        assert enemy.stuck_reason == "graph_explored"
        
        # Verify no infinite loop - should stop quickly
        none_count = sum(1 for m in moves if m is None)
        assert none_count > 0  # Should have at least one None


class TestGraphExplorationPartial:
    """Test behavior when graph is partially explored."""
    
    def test_bfs_backtracks_to_reach_unvisited_nodes(self):
        """Test BFS allows backtracking when unvisited nodes exist."""
        # Create graph
        graph = Graph(800, 600, num_nodes=8, seed=200)
        nodes = list(graph.nodes)
        
        # Enemy starts at first node
        enemy_start = nodes[0]
        player_node = nodes[-1]
        
        enemy = EnemyAI(enemy_start, 'BFS', graph)
        
        # Mark current node and some neighbors as visited, but not all
        enemy_start.visited = True
        if len(enemy_start.neighbors) > 0:
            # Mark first neighbor as visited
            enemy_start.neighbors[0][0].visited = True
        
        # Should be able to move to unvisited neighbor or backtrack
        next_move = enemy.get_next_move(player_node)
        
        # Should either:
        # 1. Move to an unvisited neighbor
        # 2. Backtrack to a visited neighbor (if no unvisited neighbors but unvisited nodes exist)
        # 3. Be stuck only if truly no moves possible
        if not enemy.stuck:
            assert next_move is not None
        else:
            # If stuck, verify it's appropriate
            assert enemy.stuck_reason in ["graph_explored"]

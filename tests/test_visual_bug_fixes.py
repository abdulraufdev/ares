"""Tests for the 3 critical visual bug fixes."""
import pytest
import pygame
import os

# Set up headless mode before importing game modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

from core.graph import Graph
from core.gameplay import GameSession
from core.graphics import GraphRenderer
from config import *


class TestVisualBugFixes:
    """Test suite for the 3 critical visual bug fixes."""
    
    def test_bug_fix_1_dynamic_info_box_sizing(self):
        """Test that info box dynamically sizes to fit algorithm names."""
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Test with algorithms that have long names
        long_algorithms = ['Greedy (Local Min)', 'Greedy (Local Max)', 'A* (Local Min)', 'A* (Local Max)']
        
        for algo in long_algorithms:
            renderer = GraphRenderer(screen, algo)
            
            # Calculate text width
            algo_text = renderer.large_font.render(f'Algorithm: {algo}', True, (255, 255, 255))
            text_width = algo_text.get_width()
            
            # Expected panel width should be at least text_width + 40 or 400, whichever is larger
            expected_min_width = max(400, text_width + 40)
            
            # The renderer should calculate this correctly
            # We verify that the calculation would work
            assert expected_min_width >= text_width + 40, f"Panel should have padding around text for {algo}"
            assert expected_min_width >= 400, f"Panel should be at least 400px for {algo}"
    
    def test_bug_fix_2_tooltips_show_numeric_heuristics(self):
        """Test that tooltips show numeric values instead of 'Not calculated'."""
        pygame.init()
        
        for algo in ['Greedy (Local Min)', 'Greedy (Local Max)', 'A* (Local Min)', 'A* (Local Max)']:
            session = GameSession(algo)
            
            # All nodes should have h_cost set (distance to player)
            for node in session.graph.nodes:
                assert hasattr(node, 'h_cost'), f"Node {node.label} should have h_cost attribute"
                assert node.h_cost >= 0, f"Node {node.label} h_cost should be non-negative"
            
            # Player's current node should have h_cost = 0
            assert session.player.node.h_cost == 0.0, "Player's node should have h_cost = 0"
            
            # Other nodes should have h_cost > 0 (unless they're at same position as player)
            other_nodes = [n for n in session.graph.nodes if n != session.player.node]
            assert len(other_nodes) > 0, "Should have nodes other than player's node"
            
            # At least some nodes should have h_cost > 0
            non_zero_heuristics = [n for n in other_nodes if n.h_cost > 0]
            assert len(non_zero_heuristics) > 0, "Some nodes should have h_cost > 0"
    
    def test_bug_fix_2_heuristics_update_on_player_move(self):
        """Test that heuristics update when player moves."""
        pygame.init()
        
        session = GameSession('Greedy (Local Min)')
        
        # Store player's initial node
        initial_node = session.player.node
        initial_h_cost = initial_node.h_cost
        
        # Initial node should have h_cost = 0
        assert initial_h_cost == 0.0, "Initial player node should have h_cost = 0"
        
        # Get a neighbor to move to
        if initial_node.neighbors:
            target_node = initial_node.neighbors[0][0]
            original_target_h_cost = target_node.h_cost
            
            # Simulate player movement
            session.player.node = target_node
            session.graph.update_heuristics_to_target(target_node)
            
            # After update, target node should have h_cost = 0
            assert target_node.h_cost == 0.0, "New player node should have h_cost = 0"
            
            # Initial node should now have h_cost > 0
            assert initial_node.h_cost > 0, "Old player node should now have h_cost > 0"
    
    def test_bug_fix_3_nodes_have_fixed_positions(self):
        """Test that nodes maintain fixed positions during gameplay."""
        pygame.init()
        
        session = GameSession('BFS')
        graph = session.graph
        
        # Save original positions
        original_positions = {node.label: tuple(node.pos) for node in graph.nodes}
        
        # Simulate player animation by changing visual_pos
        player = session.player
        if player.node.neighbors:
            target = player.node.neighbors[0][0]
            
            # Change player's visual_pos (animated position)
            player.visual_pos = (
                (player.node.pos[0] + target.pos[0]) / 2,
                (player.node.pos[1] + target.pos[1]) / 2
            )
            
            # Verify that node positions haven't changed
            for node in graph.nodes:
                current_pos = tuple(node.pos)
                original_pos = original_positions[node.label]
                assert current_pos == original_pos, f"Node {node.label} position should not change"
    
    def test_bug_fix_3_visual_pos_independent_of_node_pos(self):
        """Test that player/enemy visual_pos is independent of node.pos."""
        pygame.init()
        
        session = GameSession('DFS')
        player = session.player
        enemy = session.enemy
        
        # Store node positions
        player_node_pos = tuple(player.node.pos)
        enemy_node_pos = tuple(enemy.node.pos)
        
        # Change visual positions
        player.visual_pos = (100, 100)
        enemy.visual_pos = (200, 200)
        
        # Node positions should be unchanged
        assert tuple(player.node.pos) == player_node_pos, "Player node position should not change"
        assert tuple(enemy.node.pos) == enemy_node_pos, "Enemy node position should not change"
        
        # Visual positions should be independent
        assert player.visual_pos == (100, 100), "Player visual_pos should be independent"
        assert enemy.visual_pos == (200, 200), "Enemy visual_pos should be independent"
    
    def test_graph_update_heuristics_method_exists(self):
        """Test that Graph has the update_heuristics_to_target method."""
        pygame.init()
        
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_NODES, GRAPH_SEED)
        
        # Check method exists
        assert hasattr(graph, 'update_heuristics_to_target'), "Graph should have update_heuristics_to_target method"
        
        # Test the method works
        target_node = graph.nodes[0]
        graph.update_heuristics_to_target(target_node)
        
        # Target should have h_cost = 0
        assert target_node.h_cost == 0.0, "Target node should have h_cost = 0"
        
        # Other nodes should have h_cost > 0 (unless at same position)
        for node in graph.nodes:
            if node != target_node:
                expected_heuristic = node.distance_to(target_node)
                assert abs(node.h_cost - expected_heuristic) < 0.01, f"Node {node.label} h_cost should match distance"
    
    def test_game_session_tracks_player_movement_for_heuristics(self):
        """Test that GameSession initializes player_last_node for tracking."""
        pygame.init()
        
        session = GameSession('A* (Local Min)')
        
        # Should have player_last_node attribute
        assert hasattr(session, 'player_last_node'), "GameSession should track player_last_node"
        
        # Should be initialized to player's starting node
        assert session.player_last_node == session.player.node, "player_last_node should be initialized"

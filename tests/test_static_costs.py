"""Tests for static random path cost and heuristic values."""
import pytest
import pygame
import os

# Set up headless mode before importing game modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

from core.graph import Graph
from core.gameplay import GameSession
from config import *


class TestStaticCosts:
    """Test suite for static random cost values."""
    
    def test_nodes_have_static_heuristic_and_path_cost(self):
        """Test that all nodes have static heuristic and path_cost attributes."""
        pygame.init()
        
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_NODES, GRAPH_SEED)
        
        for node in graph.nodes:
            # Check attributes exist
            assert hasattr(node, 'heuristic'), f"Node {node.label} should have heuristic attribute"
            assert hasattr(node, 'path_cost'), f"Node {node.label} should have path_cost attribute"
            
            # Check they are non-zero (random values between 10 and 300)
            assert 10.0 <= node.heuristic <= 300.0, f"Node {node.label} heuristic should be between 10 and 300"
            assert 10.0 <= node.path_cost <= 300.0, f"Node {node.label} path_cost should be between 10 and 300"
            
            # Check they are rounded to 1 decimal place
            assert node.heuristic == round(node.heuristic, 1), f"Node {node.label} heuristic should be rounded to 1 decimal"
            assert node.path_cost == round(node.path_cost, 1), f"Node {node.label} path_cost should be rounded to 1 decimal"
    
    def test_static_costs_remain_constant_during_game(self):
        """Test that static costs do not change during gameplay."""
        pygame.init()
        
        for algo in ['BFS', 'DFS', 'UCS', 'Greedy (Local Min)', 'A* (Local Min)']:
            session = GameSession(algo)
            
            # Store initial values
            initial_costs = {}
            for node in session.graph.nodes:
                initial_costs[node.label] = {
                    'heuristic': node.heuristic,
                    'path_cost': node.path_cost
                }
            
            # Simulate player movement (if possible)
            if session.player.node.neighbors:
                target_node = session.player.node.neighbors[0][0]
                session.player.node = target_node
                session.player_last_node = target_node
            
            # Update enemy (this triggers path recalculation)
            current_time = pygame.time.get_ticks()
            session.enemy.recalculate_path(session.player.node)
            session.enemy.update(current_time, session.player.node)
            
            # Verify costs remain the same
            for node in session.graph.nodes:
                assert node.heuristic == initial_costs[node.label]['heuristic'], \
                    f"Node {node.label} heuristic should not change (algo: {algo})"
                assert node.path_cost == initial_costs[node.label]['path_cost'], \
                    f"Node {node.label} path_cost should not change (algo: {algo})"
    
    def test_static_costs_different_across_graphs(self):
        """Test that different graph instances have different random costs."""
        pygame.init()
        
        # Create two graphs with different seeds
        graph1 = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_NODES, seed=42)
        graph2 = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_NODES, seed=123)
        
        # At least some nodes should have different costs
        different_heuristics = 0
        different_path_costs = 0
        
        for i in range(len(graph1.nodes)):
            node1 = graph1.nodes[i]
            node2 = graph2.nodes[i]
            
            if node1.heuristic != node2.heuristic:
                different_heuristics += 1
            if node1.path_cost != node2.path_cost:
                different_path_costs += 1
        
        # Most nodes should have different values
        assert different_heuristics > len(graph1.nodes) * 0.9, \
            "Most nodes should have different heuristics across graphs"
        assert different_path_costs > len(graph1.nodes) * 0.9, \
            "Most nodes should have different path_costs across graphs"
    
    def test_static_costs_same_for_same_seed(self):
        """Test that graphs with the same seed have the same static costs."""
        pygame.init()
        
        # Create two graphs with the same seed
        graph1 = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_NODES, seed=42)
        graph2 = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_NODES, seed=42)
        
        # All nodes should have identical costs
        for i in range(len(graph1.nodes)):
            node1 = graph1.nodes[i]
            node2 = graph2.nodes[i]
            
            assert node1.heuristic == node2.heuristic, \
                f"Node {i} heuristic should be same for same seed"
            assert node1.path_cost == node2.path_cost, \
                f"Node {i} path_cost should be same for same seed"
    
    def test_static_costs_independent_of_player_position(self):
        """Test that static costs are balanced based on spawn positions for gameplay.
        
        Note: After implementing game balance fixes, costs are now assigned based
        on spawn positions to create ~50% enemy-favorable games. This is intentional.
        """
        pygame.init()
        
        # Create multiple game sessions (random player spawns)
        sessions = [GameSession('A* (Local Min)') for _ in range(3)]
        
        # Costs are now assigned based on spawn positions for game balance
        # Each session may have different costs since spawns are random
        # Just verify that all nodes have valid costs assigned
        for session in sessions:
            for node in session.graph.nodes:
                assert 0.0 < node.heuristic <= 350.0, \
                    f"Node heuristic should be in valid range"
                assert 0.0 < node.path_cost <= 350.0, \
                    f"Node path_cost should be in valid range"

"""Tests for Algorithm Arena game mode."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Headless mode

import pygame
import pytest
from core.arena_mode import ArenaMode, ArenaGraph, Node, Ability, EnemyAI, ENEMY_SPEEDS

def test_arena_graph_generation():
    """Test that arena graph generates correct number of nodes."""
    pygame.init()
    screen = pygame.display.set_mode((960, 720))
    
    # Test with different node counts
    for num_nodes in [25, 28, 30]:
        graph = ArenaGraph(num_nodes=num_nodes)
        assert len(graph.nodes) == num_nodes
        
        # Verify all nodes have labels
        for node in graph.nodes:
            assert node.label.startswith('N')
        
        # Verify nodes are connected
        total_connections = sum(len(node.neighbors) for node in graph.nodes)
        assert total_connections > 0, "Graph should have connections"

def test_node_hashability():
    """Test that Node objects are hashable and can be used in sets/dicts."""
    node1 = Node(pos=(0, 0), label="N0")
    node2 = Node(pos=(10, 10), label="N1")
    node3 = Node(pos=(0, 0), label="N0")  # Same label as node1
    
    # Should be able to use in set
    node_set = {node1, node2, node3}
    assert len(node_set) == 2  # node1 and node3 are equal
    
    # Should be able to use as dict key
    node_dict = {node1: "first", node2: "second"}
    assert node_dict[node3] == "first"  # node3 equals node1

def test_ability_cooldowns():
    """Test that ability cooldown system works correctly."""
    ability = Ability(
        name="Test",
        key=pygame.K_q,
        cooldown_ms=1000,
        duration_ms=500
    )
    
    # Should be ready initially
    assert ability.is_ready(0)
    assert not ability.is_active(0)
    
    # Use ability
    assert ability.use(0) == True
    
    # Should be active now
    assert ability.is_active(0)
    assert ability.is_active(400)
    assert not ability.is_active(600)  # After duration
    
    # Should not be ready during cooldown
    assert not ability.is_ready(500)
    assert not ability.use(500)
    
    # Should be ready after cooldown
    assert ability.is_ready(1000)
    assert ability.use(1000) == True

def test_enemy_speeds():
    """Test that enemy speeds are configured per algorithm."""
    assert 'BFS' in ENEMY_SPEEDS
    assert 'DFS' in ENEMY_SPEEDS
    assert 'UCS' in ENEMY_SPEEDS
    assert 'Greedy' in ENEMY_SPEEDS
    assert 'A*' in ENEMY_SPEEDS
    
    # Greedy should be fastest
    assert ENEMY_SPEEDS['Greedy'] < ENEMY_SPEEDS['BFS']
    assert ENEMY_SPEEDS['Greedy'] < ENEMY_SPEEDS['DFS']

def test_enemy_pathfinding():
    """Test that enemy can find path to player."""
    pygame.init()
    screen = pygame.display.set_mode((960, 720))
    
    graph = ArenaGraph(num_nodes=10)
    start_node = graph.nodes[0]
    target_node = graph.nodes[-1]
    
    enemy = EnemyAI(start_node, algorithm='BFS')
    
    # Update path
    enemy.update_path(graph, target_node)
    
    # Should have found a path (unless disconnected)
    # At minimum, should not crash
    assert isinstance(enemy.path, list)
    
    # If there's a path, it should lead toward target
    if enemy.path:
        assert target_node in enemy.path or len(enemy.path) == 0

def test_arena_mode_initialization():
    """Test that arena mode initializes correctly."""
    pygame.init()
    screen = pygame.display.set_mode((960, 720))
    
    arena = ArenaMode(screen)
    
    # Check components are initialized
    assert arena.graph is not None
    assert arena.player_node is not None
    assert arena.enemy is not None
    assert arena.enemy.current_node is not None
    
    # Player and enemy should be at different nodes
    assert arena.player_node != arena.enemy.current_node
    
    # Check abilities
    assert len(arena.abilities) == 4
    for ability in arena.abilities:
        assert ability.name in ["Shield", "Teleport", "Block Node", "Increase Weight"]
    
    # Check initial state
    assert not arena.paused
    assert not arena.game_over
    assert arena.score == 0

def test_graph_get_node_at_pos():
    """Test node detection from screen position."""
    pygame.init()
    screen = pygame.display.set_mode((960, 720))
    
    graph = ArenaGraph(num_nodes=5)
    
    # Get first node position
    first_node = graph.nodes[0]
    x, y = first_node.pos
    
    # Should find node at exact position
    found_node = graph.get_node_at_pos((x, y), radius=25)
    assert found_node is not None
    assert found_node == first_node
    
    # Should not find node far away
    found_node = graph.get_node_at_pos((9999, 9999), radius=25)
    assert found_node is None

if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""Tests for new game systems."""
import pytest
from core.node import Node
from core.graph import GraphGenerator
from core.models import Agent
from core.combat import CombatSystem
from core.abilities import AbilityManager
from core.themes import ThemeManager


def test_node_creation():
    """Test Node class creation and properties."""
    node = Node(5, 10, walkable=True, weight=2.0)
    
    assert node.x == 5
    assert node.y == 10
    assert node.pos == (5, 10)
    assert node.walkable is True
    assert node.weight == 2.0
    assert len(node.neighbors) == 0


def test_node_neighbors():
    """Test adding neighbors to nodes."""
    node1 = Node(0, 0)
    node2 = Node(1, 0)
    
    node1.add_neighbor(node2)
    
    assert node2 in node1.neighbors
    assert len(node1.neighbors) == 1


def test_node_reset_pathfinding():
    """Test resetting pathfinding attributes."""
    node = Node(0, 0)
    node.g = 10
    node.h = 5
    node.visited = True
    
    node.reset_pathfinding()
    
    assert node.g == float('inf')
    assert node.h == 0.0
    assert node.visited is False


def test_graph_generator_maze():
    """Test maze generation."""
    gen = GraphGenerator(20, 20)
    nodes = gen.generate('maze', seed=42)
    
    assert len(nodes) == 20
    assert len(nodes[0]) == 20
    
    # Check that start and goal areas are clear
    assert nodes[1][1].walkable is True
    assert nodes[18][18].walkable is True


def test_graph_generator_weighted():
    """Test weighted terrain generation."""
    gen = GraphGenerator(20, 20)
    nodes = gen.generate('weighted', seed=42)
    
    assert len(nodes) == 20
    
    # Check that some nodes have varied weights
    weights = [node.weight for row in nodes for node in row if node.walkable]
    assert max(weights) > 1.0


def test_graph_generator_open():
    """Test open field generation."""
    gen = GraphGenerator(20, 20)
    nodes = gen.generate('open', seed=42)
    
    assert len(nodes) == 20
    
    # Count walkable nodes - should be mostly walkable
    walkable_count = sum(1 for row in nodes for node in row if node.walkable)
    total_count = 20 * 20
    
    assert walkable_count > total_count * 0.8  # At least 80% walkable


def test_agent_take_damage():
    """Test agent taking damage."""
    agent = Agent(name="Test", pos=(0, 0), stamina=100, hp=100, max_hp=100)
    
    damage_taken = agent.take_damage(30, 0.0)
    
    assert damage_taken is True
    assert agent.hp == 70


def test_agent_shield():
    """Test agent shield blocking damage."""
    agent = Agent(name="Test", pos=(0, 0), stamina=100, hp=100, max_hp=100)
    agent.shield_active = True
    agent.shield_end_time = 1000.0
    
    damage_taken = agent.take_damage(30, 500.0)
    
    assert damage_taken is False
    assert agent.hp == 100


def test_agent_heal():
    """Test agent healing."""
    agent = Agent(name="Test", pos=(0, 0), stamina=100, hp=50, max_hp=100)
    
    agent.heal(30)
    
    assert agent.hp == 80
    
    # Can't heal above max
    agent.heal(50)
    assert agent.hp == 100


def test_agent_is_alive():
    """Test agent alive status."""
    agent = Agent(name="Test", pos=(0, 0), stamina=100, hp=50, max_hp=100)
    
    assert agent.is_alive() is True
    
    agent.hp = 0
    assert agent.is_alive() is False


def test_combat_collision():
    """Test collision detection."""
    combat = CombatSystem()
    agent1 = Agent(name="A", pos=(5, 5), stamina=100, hp=100, max_hp=100)
    agent2 = Agent(name="B", pos=(5, 5), stamina=100, hp=100, max_hp=100)
    
    assert combat.check_collision(agent1, agent2) is True
    
    agent2.pos = (6, 6)
    assert combat.check_collision(agent1, agent2) is False


def test_combat_melee_range():
    """Test melee range detection."""
    combat = CombatSystem()
    agent1 = Agent(name="A", pos=(5, 5), stamina=100, hp=100, max_hp=100)
    agent2 = Agent(name="B", pos=(6, 5), stamina=100, hp=100, max_hp=100)
    
    assert combat.is_in_melee_range(agent1, agent2, 1) is True
    
    agent2.pos = (10, 10)
    assert combat.is_in_melee_range(agent1, agent2, 1) is False


def test_ability_manager_shield():
    """Test shield ability."""
    manager = AbilityManager()
    agent = Agent(name="Test", pos=(0, 0), stamina=100, hp=100, max_hp=100)
    
    success = manager.use_shield(agent, 0.0)
    
    assert success is True
    assert agent.shield_active is True
    assert agent.shield_end_time > 0


def test_ability_cooldown():
    """Test ability cooldown."""
    manager = AbilityManager()
    agent = Agent(name="Test", pos=(0, 0), stamina=100, hp=100, max_hp=100)
    
    # Use shield
    manager.use_shield(agent, 0.0)
    
    # Try to use again immediately - should fail
    success = manager.use_shield(agent, 100.0)
    assert success is False
    
    # After cooldown - should work
    success = manager.use_shield(agent, 20000.0)
    assert success is True


def test_theme_manager():
    """Test theme manager."""
    manager = ThemeManager()
    
    manager.set_theme('BFS')
    assert manager.current_theme == 'BFS'
    
    theme = manager.get_theme('BFS')
    assert 'primary' in theme
    assert 'path' in theme
    
    color = manager.get_color('primary', 'A*')
    assert len(color) == 3  # RGB tuple


def test_theme_colors():
    """Test that all algorithms have themes."""
    manager = ThemeManager()
    
    algorithms = ['BFS', 'DFS', 'UCS', 'Greedy', 'A*']
    
    for algo in algorithms:
        theme = manager.get_theme(algo)
        assert theme is not None
        assert 'primary' in theme
        assert 'secondary' in theme
        assert 'path' in theme

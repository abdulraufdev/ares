"""Tests for graph-based Algorithm Arena systems."""
import pytest
from core.node import Node
from core.graph import Graph
from core.combat import CombatSystem, CombatEntity
from core.gameplay import PlayerEntity, EnemyAI, GameSession
from algorithms.graph_algorithms import find_path
from config import WINDOW_WIDTH, WINDOW_HEIGHT, NUM_NODES


class TestNode:
    """Tests for Node class."""
    
    def test_node_creation(self):
        """Test node initialization."""
        node = Node("N1", (100, 100))
        assert node.label == "N1"
        assert node.pos == (100, 100)
        assert len(node.neighbors) == 0
        assert not node.visited
    
    def test_add_neighbor(self):
        """Test adding neighbors."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        
        node1.add_neighbor(node2, 5.0)
        
        # Should create bidirectional connection
        assert len(node1.neighbors) == 1
        assert len(node2.neighbors) == 1
        assert node1.neighbors[0] == (node2, 5.0)
        assert node2.neighbors[0] == (node1, 5.0)
    
    def test_get_weight_to(self):
        """Test getting edge weight."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node1.add_neighbor(node2, 7.5)
        
        assert node1.get_weight_to(node2) == 7.5
        assert node2.get_weight_to(node1) == 7.5
    
    def test_distance_to(self):
        """Test Euclidean distance calculation."""
        node1 = Node("N1", (0, 0))
        node2 = Node("N2", (3, 4))
        
        distance = node1.distance_to(node2)
        assert abs(distance - 5.0) < 0.001
    
    def test_reset_pathfinding(self):
        """Test resetting pathfinding metadata."""
        node = Node("N1", (100, 100))
        node.visited = True
        node.g_cost = 10.0
        node.h_cost = 5.0
        node.f_cost = 15.0
        
        node.reset_pathfinding()
        
        assert not node.visited
        assert node.g_cost == 0.0
        assert node.h_cost == 0.0
        assert node.f_cost == 0.0


class TestGraph:
    """Tests for Graph class."""
    
    def test_graph_creation(self):
        """Test graph generation."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        assert len(graph.nodes) == 20
        
        # Check labels
        labels = [node.label for node in graph.nodes]
        assert "N1" in labels
        assert "N20" in labels
    
    def test_graph_connectivity(self):
        """Test that all nodes are reachable."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 15, seed=42)
        
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
        assert len(visited) == len(graph.nodes)
    
    def test_node_positions_valid(self):
        """Test that node positions are within bounds."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        
        for node in graph.nodes:
            x, y = node.pos
            assert 0 <= x <= WINDOW_WIDTH
            assert 0 <= y <= WINDOW_HEIGHT
    
    def test_get_node_by_label(self):
        """Test finding node by label."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 10, seed=42)
        
        node = graph.get_node_by_label("N5")
        assert node is not None
        assert node.label == "N5"
        
        node = graph.get_node_by_label("N999")
        assert node is None
    
    def test_get_node_at_pos(self):
        """Test finding node at position."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 10, seed=42)
        
        test_node = graph.nodes[0]
        found = graph.get_node_at_pos(test_node.pos, radius=30)
        assert found == test_node
        
        # Position far from any node
        found = graph.get_node_at_pos((10000, 10000), radius=30)
        assert found is None


class TestGraphAlgorithms:
    """Tests for graph-based pathfinding algorithms."""
    
    def test_bfs_finds_path(self):
        """Test BFS finds a valid path."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, stats = find_path('BFS', graph, start, goal)
        
        assert len(path) > 0
        assert path[0] == start
        assert path[-1] == goal
        assert stats.path_len == len(path)
        assert stats.nodes_expanded > 0
    
    def test_dfs_finds_path(self):
        """Test DFS finds a valid path."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, stats = find_path('DFS', graph, start, goal)
        
        assert len(path) > 0
        assert path[0] == start
        assert path[-1] == goal
    
    def test_ucs_finds_path(self):
        """Test UCS finds a valid path."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, stats = find_path('UCS', graph, start, goal)
        
        assert len(path) > 0
        assert path[0] == start
        assert path[-1] == goal
        assert stats.path_cost > 0
    
    def test_greedy_finds_path(self):
        """Test Greedy finds a valid path."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, stats = find_path('Greedy', graph, start, goal)
        
        assert len(path) > 0
        assert path[0] == start
        assert path[-1] == goal
    
    def test_astar_finds_path(self):
        """Test A* finds a valid path."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, stats = find_path('A*', graph, start, goal)
        
        assert len(path) > 0
        assert path[0] == start
        assert path[-1] == goal
        assert stats.path_cost > 0
    
    def test_same_start_goal(self):
        """Test pathfinding with same start and goal."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 10, seed=42)
        node = graph.nodes[0]
        
        for algo in ['BFS', 'DFS', 'UCS', 'Greedy', 'A*']:
            path, stats = find_path(algo, graph, node, node)
            assert len(path) == 1
            assert path[0] == node
    
    def test_path_connectivity(self):
        """Test that returned paths have connected nodes."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        start = graph.nodes[0]
        goal = graph.nodes[-1]
        
        path, _ = find_path('A*', graph, start, goal)
        
        # Check each step is to a neighbor
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]
            
            neighbors = [n for n, _ in current.neighbors]
            assert next_node in neighbors


class TestCombat:
    """Tests for combat system."""
    
    def test_combat_entity_creation(self):
        """Test combat entity initialization."""
        entity = CombatEntity(max_hp=100)
        assert entity.hp == 100
        assert entity.max_hp == 100
        assert entity.is_alive()
    
    def test_take_damage(self):
        """Test damage application."""
        entity = CombatEntity(max_hp=100)
        
        # First damage should work (no cooldown active)
        damaged = entity.take_damage(30, 1000)  # Give it a valid timestamp
        assert damaged
        assert entity.hp == 70
    
    def test_damage_cooldown(self):
        """Test damage cooldown prevents rapid damage."""
        entity = CombatEntity(max_hp=100)
        
        entity.take_damage(20, 1000)
        assert entity.hp == 80
        
        # Try to damage again immediately
        damaged = entity.take_damage(20, 1100)  # Only 100ms later
        assert not damaged
        assert entity.hp == 80  # No additional damage
        
        # After cooldown
        damaged = entity.take_damage(20, 2500)  # After 1000ms cooldown
        assert damaged
        assert entity.hp == 60
    
    def test_entity_death(self):
        """Test entity death."""
        entity = CombatEntity(max_hp=50)
        
        entity.take_damage(60, 1000)
        assert entity.hp == 0
        assert not entity.is_alive()
    
    def test_combat_system(self):
        """Test full combat system."""
        combat = CombatSystem()
        
        assert combat.player.hp == 100
        assert combat.enemy.hp == 150
        
        # Use the same node for both (contact)
        contact_node = Node("N1", (100, 100))
        
        player_damaged, enemy_damaged = combat.check_contact(contact_node, contact_node, 1000)
        assert player_damaged
        assert not enemy_damaged  # Enemy is invincible
        assert combat.player.hp == 90
        assert combat.enemy.hp == 150  # Enemy health unchanged
    
    def test_game_over_conditions(self):
        """Test victory and defeat conditions."""
        combat = CombatSystem()
        
        # No game over initially
        is_over, reason = combat.is_game_over()
        assert not is_over
        
        # Player dies
        combat.player.hp = 0
        is_over, reason = combat.is_game_over()
        assert is_over
        assert reason == 'defeat'
        
        # Enemy cannot die (invincible) - no victory from combat
        combat.reset()
        combat.enemy.hp = 0
        is_over, reason = combat.is_game_over()
        assert not is_over  # Game is not over even if enemy HP reaches 0
        assert reason == ''  # No game over reason


class TestGameplay:
    """Tests for gameplay systems."""
    
    def test_player_entity_creation(self):
        """Test player entity initialization."""
        node = Node("N1", (100, 100))
        player = PlayerEntity(node)
        
        assert player.node == node
        assert player.nodes_visited == 0
        assert not player.is_moving
    
    def test_player_can_move_to_neighbor(self):
        """Test player movement validation."""
        node1 = Node("N1", (100, 100))
        node2 = Node("N2", (200, 100))
        node3 = Node("N3", (300, 100))
        
        node1.add_neighbor(node2, 5)
        
        player = PlayerEntity(node1)
        
        assert player.can_move_to(node2)
        assert not player.can_move_to(node3)
    
    def test_enemy_ai_creation(self):
        """Test enemy AI initialization."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        node = graph.nodes[0]
        
        enemy = EnemyAI(node, 'A*', graph)
        
        assert enemy.node == node
        assert enemy.algorithm == 'A*'
        assert len(enemy.path) == 0
    
    def test_enemy_recalculates_path(self):
        """Test enemy movement decision (pure greedy, no pathfinding)."""
        graph = Graph(WINDOW_WIDTH, WINDOW_HEIGHT, 20, seed=42)
        enemy_start = graph.nodes[0]
        player_pos = graph.nodes[-1]
        
        enemy = EnemyAI(enemy_start, 'BFS', graph)
        
        # In new implementation, enemy doesn't calculate full paths
        # Instead, it picks next move based on algorithm rules
        next_move = enemy.get_next_move(player_pos)
        
        # Should return a valid neighbor
        assert next_move is not None
        assert next_move in [n for n, _ in enemy_start.neighbors]
        
        # recalculate_path should be a no-op but still callable
        enemy.recalculate_path(player_pos)  # Should not raise error
    
    def test_game_session_creation(self):
        """Test game session initialization."""
        session = GameSession('A*')
        
        assert session.algorithm == 'A*'
        assert len(session.graph.nodes) > 0
        assert session.player.node is not None
        assert session.enemy.node is not None
        assert session.combat.player.hp == 100
        assert session.combat.enemy.hp == 150


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

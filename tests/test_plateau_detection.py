"""Tests for plateau/ridge detection in Greedy and A* algorithms."""
import pytest
from core.node import Node
from core.gameplay import EnemyAI


class MockGraph:
    """Mock graph for testing."""
    def __init__(self, nodes):
        self.nodes = nodes
    
    def reset_all_nodes(self):
        for node in self.nodes:
            node.reset_pathfinding()


class TestGreedyLocalMinPlateauDetection:
    """Test that Greedy Local Min stops at local minimum (plateau)."""
    
    def test_stops_when_all_neighbors_have_greater_values(self):
        """Test enemy stops when stuck at local minimum."""
        # Create a local minimum: current node has value 4, all neighbors higher
        n1 = Node("N1", (100, 100))  # Current (value: 4)
        n2 = Node("N2", (200, 100))  # Neighbor (value: 7)
        n3 = Node("N3", (300, 100))  # Neighbor (value: 9)
        n4 = Node("N4", (150, 150))  # Neighbor (value: 6)
        
        n1.heuristic = 4.0   # LOCAL MINIMUM
        n2.heuristic = 7.0   # All neighbors > current
        n3.heuristic = 9.0
        n4.heuristic = 6.0
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        n1.add_neighbor(n4, 5)
        
        graph = MockGraph([n1, n2, n3, n4])
        enemy = EnemyAI(n1, 'Greedy (Local Min)', graph)
        
        # Enemy should be stuck (return None)
        next_move = enemy.get_next_move(n4)
        assert next_move is None, "Enemy should stop at local minimum"
        assert enemy.stuck == True, "Enemy stuck flag should be set"
    
    def test_continues_when_can_descend(self):
        """Test enemy continues when can still descend to lower values."""
        n1 = Node("N1", (100, 100))  # Current (value: 10)
        n2 = Node("N2", (200, 100))  # Lower (value: 5)
        n3 = Node("N3", (300, 100))  # Higher (value: 15)
        
        n1.heuristic = 10.0
        n2.heuristic = 5.0   # Can descend to this
        n3.heuristic = 15.0
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n1, 'Greedy (Local Min)', graph)
        
        # Enemy should move to n2 (minimum neighbor)
        next_move = enemy.get_next_move(n3)
        assert next_move == n2, "Enemy should pick minimum neighbor"
        assert enemy.stuck == False


class TestGreedyLocalMaxPlateauDetection:
    """Test that Greedy Local Max stops at local maximum (plateau)."""
    
    def test_stops_when_all_neighbors_have_smaller_values(self):
        """Test enemy stops when stuck at local maximum."""
        # Create a local maximum: current node has value 15, all neighbors lower
        m1 = Node("M1", (100, 100))  # Current (value: 15)
        m2 = Node("M2", (200, 100))  # Neighbor (value: 10)
        m3 = Node("M3", (300, 100))  # Neighbor (value: 8)
        m4 = Node("M4", (150, 150))  # Neighbor (value: 12)
        
        m1.heuristic = 15.0  # LOCAL MAXIMUM
        m2.heuristic = 10.0  # All neighbors < current
        m3.heuristic = 8.0
        m4.heuristic = 12.0
        
        m1.add_neighbor(m2, 5)
        m1.add_neighbor(m3, 5)
        m1.add_neighbor(m4, 5)
        
        graph = MockGraph([m1, m2, m3, m4])
        enemy = EnemyAI(m1, 'Greedy (Local Max)', graph)
        
        # Enemy should be stuck (return None)
        next_move = enemy.get_next_move(m4)
        assert next_move is None, "Enemy should stop at local maximum"
        assert enemy.stuck == True, "Enemy stuck flag should be set"
    
    def test_continues_when_can_ascend(self):
        """Test enemy continues when can still ascend to higher values."""
        m1 = Node("M1", (100, 100))  # Current (value: 10)
        m2 = Node("M2", (200, 100))  # Lower (value: 5)
        m3 = Node("M3", (300, 100))  # Higher (value: 20)
        
        m1.heuristic = 10.0
        m2.heuristic = 5.0
        m3.heuristic = 20.0  # Can ascend to this
        
        m1.add_neighbor(m2, 5)
        m1.add_neighbor(m3, 5)
        
        graph = MockGraph([m1, m2, m3])
        enemy = EnemyAI(m1, 'Greedy (Local Max)', graph)
        
        # Enemy should move to m3 (maximum neighbor)
        next_move = enemy.get_next_move(m2)
        assert next_move == m3, "Enemy should pick maximum neighbor"
        assert enemy.stuck == False


class TestAStarLocalMinPlateauDetection:
    """Test that A* Local Min stops at local minimum (plateau)."""
    
    def test_stops_when_all_neighbors_have_greater_f_cost(self):
        """Test enemy stops when stuck at local minimum (f-cost)."""
        # Create a local minimum: current f=20, all neighbors have higher f-cost
        a1 = Node("A1", (100, 100))  # Current (f=20)
        a2 = Node("A2", (200, 100))  # Neighbor (f=30)
        a3 = Node("A3", (300, 100))  # Neighbor (f=35)
        
        a1.heuristic = 10.0
        a1.path_cost = 10.0
        # f_cost = 20.0 (LOCAL MINIMUM)
        
        a2.heuristic = 15.0
        a2.path_cost = 15.0
        # f_cost = 30.0
        
        a3.heuristic = 20.0
        a3.path_cost = 15.0
        # f_cost = 35.0
        
        a1.add_neighbor(a2, 5)
        a1.add_neighbor(a3, 5)
        
        graph = MockGraph([a1, a2, a3])
        enemy = EnemyAI(a1, 'A* (Local Min)', graph)
        
        # Enemy should be stuck (return None)
        next_move = enemy.get_next_move(a3)
        assert next_move is None, "Enemy should stop at local minimum f-cost"
        assert enemy.stuck == True, "Enemy stuck flag should be set"
    
    def test_continues_when_can_descend_f_cost(self):
        """Test enemy continues when can still descend to lower f-cost."""
        a1 = Node("A1", (100, 100))  # Current (f=30)
        a2 = Node("A2", (200, 100))  # Lower (f=20)
        a3 = Node("A3", (300, 100))  # Higher (f=40)
        
        a1.heuristic = 15.0
        a1.path_cost = 15.0
        # f = 30
        
        a2.heuristic = 10.0
        a2.path_cost = 10.0
        # f = 20 (can descend)
        
        a3.heuristic = 20.0
        a3.path_cost = 20.0
        # f = 40
        
        a1.add_neighbor(a2, 5)
        a1.add_neighbor(a3, 5)
        
        graph = MockGraph([a1, a2, a3])
        enemy = EnemyAI(a1, 'A* (Local Min)', graph)
        
        # Enemy should move to a2 (minimum f-cost neighbor)
        next_move = enemy.get_next_move(a3)
        assert next_move == a2, "Enemy should pick minimum f-cost neighbor"
        assert enemy.stuck == False


class TestAStarLocalMaxPlateauDetection:
    """Test that A* Local Max stops at local maximum (plateau)."""
    
    def test_stops_when_all_neighbors_have_smaller_f_cost(self):
        """Test enemy stops when stuck at local maximum (f-cost)."""
        # Create a local maximum: current f=50, all neighbors have lower f-cost
        b1 = Node("B1", (100, 100))  # Current (f=50)
        b2 = Node("B2", (200, 100))  # Neighbor (f=30)
        b3 = Node("B3", (300, 100))  # Neighbor (f=25)
        
        b1.heuristic = 30.0
        b1.path_cost = 20.0
        # f_cost = 50.0 (LOCAL MAXIMUM)
        
        b2.heuristic = 15.0
        b2.path_cost = 15.0
        # f_cost = 30.0
        
        b3.heuristic = 15.0
        b3.path_cost = 10.0
        # f_cost = 25.0
        
        b1.add_neighbor(b2, 5)
        b1.add_neighbor(b3, 5)
        
        graph = MockGraph([b1, b2, b3])
        enemy = EnemyAI(b1, 'A* (Local Max)', graph)
        
        # Enemy should be stuck (return None)
        next_move = enemy.get_next_move(b3)
        assert next_move is None, "Enemy should stop at local maximum f-cost"
        assert enemy.stuck == True, "Enemy stuck flag should be set"
    
    def test_continues_when_can_ascend_f_cost(self):
        """Test enemy continues when can still ascend to higher f-cost."""
        b1 = Node("B1", (100, 100))  # Current (f=30)
        b2 = Node("B2", (200, 100))  # Lower (f=20)
        b3 = Node("B3", (300, 100))  # Higher (f=50)
        
        b1.heuristic = 15.0
        b1.path_cost = 15.0
        # f = 30
        
        b2.heuristic = 10.0
        b2.path_cost = 10.0
        # f = 20
        
        b3.heuristic = 30.0
        b3.path_cost = 20.0
        # f = 50 (can ascend)
        
        b1.add_neighbor(b2, 5)
        b1.add_neighbor(b3, 5)
        
        graph = MockGraph([b1, b2, b3])
        enemy = EnemyAI(b1, 'A* (Local Max)', graph)
        
        # Enemy should move to b3 (maximum f-cost neighbor)
        next_move = enemy.get_next_move(b2)
        assert next_move == b3, "Enemy should pick maximum f-cost neighbor"
        assert enemy.stuck == False


class TestPlateauEdgeCases:
    """Test edge cases for plateau detection."""
    
    def test_single_neighbor_not_plateau(self):
        """Test that having a single neighbor is not considered a plateau."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        
        n1.heuristic = 5.0
        n2.heuristic = 10.0  # Only neighbor, higher value
        
        n1.add_neighbor(n2, 5)
        
        graph = MockGraph([n1, n2])
        enemy = EnemyAI(n1, 'Greedy (Local Min)', graph)
        
        # Should still be stuck because only neighbor has higher value
        next_move = enemy.get_next_move(n2)
        assert next_move is None, "Should be stuck with only uphill neighbor"
        assert enemy.stuck == True
    
    def test_equal_values_not_plateau_for_min(self):
        """Test that equal values don't cause plateau for Local Min."""
        n1 = Node("N1", (100, 100))
        n2 = Node("N2", (200, 100))
        n3 = Node("N3", (300, 100))
        
        n1.heuristic = 10.0
        n2.heuristic = 10.0  # Equal value
        n3.heuristic = 15.0
        
        n1.add_neighbor(n2, 5)
        n1.add_neighbor(n3, 5)
        
        graph = MockGraph([n1, n2, n3])
        enemy = EnemyAI(n1, 'Greedy (Local Min)', graph)
        
        # Should pick n2 (equal or lower is acceptable)
        next_move = enemy.get_next_move(n3)
        assert next_move == n2, "Should pick equal value neighbor"
        assert enemy.stuck == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

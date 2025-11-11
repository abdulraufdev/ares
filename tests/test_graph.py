"""Tests for graph-based components."""
import pytest
from core.graph import Graph
from core.node import Node
from algorithms.graph_algorithms import bfs_graph, dfs_graph, ucs_graph, greedy_graph, astar_graph


def test_node_creation():
    """Test creating a node."""
    node = Node(label='A', pos=(100, 200))
    assert node.label == 'A'
    assert node.pos == (100, 200)
    assert node.walkable == True
    assert len(node.edges) == 0


def test_node_edges():
    """Test adding edges to a node."""
    node = Node(label='A', pos=(100, 200))
    node.add_edge('B', 5.0)
    node.add_edge('C', 3.0)
    
    assert node.is_neighbor('B')
    assert node.is_neighbor('C')
    assert not node.is_neighbor('D')
    assert node.get_weight('B') == 5.0
    assert node.get_weight('C') == 3.0


def test_graph_creation():
    """Test creating a graph."""
    graph = Graph(num_nodes=10, width=800, height=600, seed=42)
    
    assert len(graph.nodes) == 10
    assert 'A' in graph.nodes
    assert 'J' in graph.nodes
    assert 'K' not in graph.nodes  # Only 10 nodes


def test_graph_edges():
    """Test that graph creates edges between nodes."""
    graph = Graph(num_nodes=5, width=800, height=600, seed=42, topology='mesh')
    
    # Check that nodes have edges
    total_edges = sum(len(node.edges) for node in graph.nodes.values())
    assert total_edges > 0  # Mesh should have edges
    
    # Check bidirectional edges
    for label, node in graph.nodes.items():
        for neighbor_label, weight in node.edges.items():
            neighbor = graph.get_node(neighbor_label)
            assert neighbor is not None
            assert label in neighbor.edges  # Bidirectional


def test_graph_neighbors():
    """Test getting neighbors."""
    graph = Graph(num_nodes=5, width=800, height=600, seed=42)
    
    neighbors = graph.get_neighbors('A')
    assert isinstance(neighbors, list)
    assert all(isinstance(n, str) for n in neighbors)


def test_graph_block_node():
    """Test blocking a node."""
    graph = Graph(num_nodes=5, width=800, height=600, seed=42)
    
    graph.block_node('B')
    node_b = graph.get_node('B')
    assert node_b.walkable == False
    
    graph.unblock_node('B')
    assert node_b.walkable == True


def test_graph_increase_weight():
    """Test increasing edge weight."""
    graph = Graph(num_nodes=5, width=800, height=600, seed=42)
    
    # Find an edge
    node_a = graph.get_node('A')
    if node_a.edges:
        neighbor_label = list(node_a.edges.keys())[0]
        original_weight = node_a.get_weight(neighbor_label)
        
        graph.increase_edge_weight('A', neighbor_label, 5.0)
        new_weight = node_a.get_weight(neighbor_label)
        
        assert new_weight == original_weight * 5.0


def test_bfs_graph_simple():
    """Test BFS on graph."""
    graph = Graph(num_nodes=5, width=800, height=600, seed=42)
    
    path, stats = bfs_graph(graph, 'A', 'E')
    
    assert len(path) > 0
    assert path[0] == 'A'
    assert path[-1] == 'E'
    assert stats.nodes_expanded > 0


def test_dfs_graph_simple():
    """Test DFS on graph."""
    graph = Graph(num_nodes=5, width=800, height=600, seed=42)
    
    path, stats = dfs_graph(graph, 'A', 'E')
    
    assert len(path) > 0
    assert path[0] == 'A'
    assert path[-1] == 'E'
    assert stats.nodes_expanded > 0


def test_ucs_graph_simple():
    """Test UCS on graph."""
    graph = Graph(num_nodes=5, width=800, height=600, seed=42)
    
    path, stats = ucs_graph(graph, 'A', 'E')
    
    assert len(path) > 0
    assert path[0] == 'A'
    assert path[-1] == 'E'
    assert stats.path_cost > 0


def test_greedy_graph_simple():
    """Test Greedy on graph."""
    graph = Graph(num_nodes=5, width=800, height=600, seed=42)
    
    path, stats = greedy_graph(graph, 'A', 'E')
    
    assert len(path) > 0
    assert path[0] == 'A'
    assert path[-1] == 'E'


def test_astar_graph_simple():
    """Test A* on graph."""
    graph = Graph(num_nodes=5, width=800, height=600, seed=42)
    
    path, stats = astar_graph(graph, 'A', 'E')
    
    assert len(path) > 0
    assert path[0] == 'A'
    assert path[-1] == 'E'
    assert stats.path_cost > 0


def test_graph_same_start_goal():
    """Test when start equals goal."""
    graph = Graph(num_nodes=5, width=800, height=600, seed=42)
    
    path, stats = bfs_graph(graph, 'A', 'A')
    
    assert len(path) == 1
    assert path[0] == 'A'


def test_graph_blocked_target():
    """Test when target is blocked."""
    graph = Graph(num_nodes=5, width=800, height=600, seed=42)
    
    graph.block_node('E')
    path, stats = bfs_graph(graph, 'A', 'E')
    
    assert len(path) == 0  # No path to blocked node


def test_graph_topologies():
    """Test different graph topologies."""
    for topology in ['mesh', 'grid', 'ring']:
        graph = Graph(num_nodes=10, width=800, height=600, seed=42, topology=topology)
        assert len(graph.nodes) == 10
        
        # Check that all nodes have positions
        for node in graph.nodes.values():
            assert node.pos[0] >= 0
            assert node.pos[1] >= 0

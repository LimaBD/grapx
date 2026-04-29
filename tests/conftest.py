"""
Shared test fixtures and configuration.
"""

import pytest

import grapx as gx


@pytest.fixture
def simple_graph():
    """Undirected triangle: 1-2-3-1"""
    G = gx.Graph()
    G.add_edges_from([(1, 2), (2, 3), (3, 1)])
    return G


@pytest.fixture
def simple_digraph():
    """Directed chain: A → B → C with A → C shortcut"""
    G = gx.DiGraph()
    G.add_edge("A", "B", weight=1.0)
    G.add_edge("B", "C", weight=1.0)
    G.add_edge("A", "C", weight=10.0)
    return G


@pytest.fixture
def weighted_graph():
    """Undirected weighted graph for shortest-path tests"""
    G = gx.Graph()
    G.add_edge(1, 2, weight=1.0)
    G.add_edge(2, 3, weight=1.0)
    G.add_edge(1, 3, weight=5.0)
    G.add_edge(3, 4, weight=1.0)
    return G


@pytest.fixture
def disconnected_graph():
    """Graph with two components: {1,2,3} and {10,11}"""
    G = gx.Graph()
    G.add_edges_from([(1, 2), (2, 3)])
    G.add_edge(10, 11)
    return G

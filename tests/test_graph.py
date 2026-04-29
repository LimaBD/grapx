"""
Tests for core Graph and DiGraph operations.
"""

import pytest

import grapx as gx
from grapx.exception import GrapxError, NodeNotFound


class TestGraphBasics:
    def test_empty_graph(self):
        G = gx.Graph()
        assert len(G) == 0
        assert G.number_of_nodes() == 0
        assert G.number_of_edges() == 0

    def test_add_node(self):
        G = gx.Graph()
        G.add_node(1)
        assert 1 in G
        assert G.number_of_nodes() == 1

    def test_add_node_with_attrs(self):
        G = gx.Graph()
        G.add_node("Alice", age=30, city="NYC")
        assert G.nodes["Alice"]["age"] == 30
        assert G.nodes["Alice"]["city"] == "NYC"

    def test_add_nodes_from(self):
        G = gx.Graph()
        G.add_nodes_from([1, 2, 3])
        assert G.number_of_nodes() == 3

    def test_add_nodes_from_with_attrs(self):
        G = gx.Graph()
        G.add_nodes_from([(1, {"color": "red"}), (2, {"color": "blue"})])
        assert G.nodes[1]["color"] == "red"
        assert G.nodes[2]["color"] == "blue"

    def test_add_edge(self):
        G = gx.Graph()
        G.add_edge(1, 2)
        assert G.has_edge(1, 2)
        assert G.has_edge(2, 1)  # undirected
        assert G.number_of_edges() == 1
        assert G.number_of_nodes() == 2

    def test_add_edge_creates_nodes(self):
        G = gx.Graph()
        G.add_edge("X", "Y")
        assert "X" in G
        assert "Y" in G

    def test_add_edge_with_weight(self):
        G = gx.Graph()
        G.add_edge(1, 2, weight=3.14)
        data = G.get_edge_data(1, 2)
        assert pytest.approx(data["weight"], rel=1e-6) == 3.14

    def test_add_edge_with_multiple_attrs(self):
        G = gx.Graph()
        G.add_edge("A", "B", weight=2.0, color="red", label="AB")
        d = G.get_edge_data("A", "B")
        assert d["color"] == "red"
        assert d["label"] == "AB"

    def test_add_edges_from(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4)])
        assert G.number_of_edges() == 3
        assert G.number_of_nodes() == 4

    def test_add_edges_from_with_data(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2, {"weight": 1.0}), (2, 3, {"weight": 2.0})])
        assert G.get_edge_data(1, 2)["weight"] == 1.0
        assert G.get_edge_data(2, 3)["weight"] == 2.0

    def test_remove_edge(self):
        G = gx.Graph()
        G.add_edge(1, 2)
        G.remove_edge(1, 2)
        assert not G.has_edge(1, 2)
        assert G.number_of_edges() == 0

    def test_remove_nonexistent_edge_raises(self):
        G = gx.Graph()
        G.add_edge(1, 2)
        with pytest.raises(GrapxError):
            G.remove_edge(1, 99)

    def test_remove_node(self):
        G = gx.Graph()
        G.add_edge(1, 2)
        G.remove_node(1)
        assert 1 not in G
        assert G.number_of_nodes() == 1

    def test_remove_nonexistent_node_raises(self):
        G = gx.Graph()
        with pytest.raises(NodeNotFound):
            G.remove_node(99)

    def test_neighbors(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (1, 3), (1, 4)])
        assert set(G.neighbors(1)) == {2, 3, 4}

    def test_neighbors_missing_node_raises(self):
        G = gx.Graph()
        with pytest.raises(NodeNotFound):
            list(G.neighbors(999))

    def test_degree(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (1, 3)])
        assert G.degree[1] == 2
        assert G.degree[2] == 1

    def test_degree_view_iter(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (2, 3)])
        degrees = dict(G.degree)
        assert degrees[1] == 1
        assert degrees[2] == 2
        assert degrees[3] == 1

    def test_contains(self):
        G = gx.Graph()
        G.add_nodes_from([1, 2, 3])
        assert 1 in G
        assert 99 not in G

    def test_len(self):
        G = gx.Graph()
        G.add_nodes_from([1, 2, 3])
        assert len(G) == 3

    def test_iter(self):
        G = gx.Graph()
        G.add_nodes_from([10, 20, 30])
        assert set(G) == {10, 20, 30}

    def test_repr(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (2, 3)])
        r = repr(G)
        assert "Graph" in r
        assert "2" in r  # nodes count

    def test_is_directed(self):
        assert not gx.Graph().is_directed()
        assert gx.DiGraph().is_directed()

    def test_is_multigraph(self):
        assert not gx.Graph().is_multigraph()

    def test_copy(self):
        G = gx.Graph()
        G.add_edge(1, 2, weight=5.0)
        H = G.copy()
        assert H.has_edge(1, 2)
        assert H.get_edge_data(1, 2)["weight"] == 5.0

    def test_subgraph(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4)])
        H = G.subgraph([1, 2, 3])
        assert H.has_edge(1, 2)
        assert H.has_edge(2, 3)
        assert not H.has_edge(3, 4)

    def test_add_star(self):
        G = gx.Graph()
        G.add_star([0, 1, 2, 3])
        assert G.has_edge(0, 1)
        assert G.has_edge(0, 2)
        assert G.has_edge(0, 3)
        assert G.degree[0] == 3

    def test_add_path(self):
        G = gx.Graph()
        G.add_path([1, 2, 3, 4])
        assert G.has_edge(1, 2)
        assert G.has_edge(2, 3)
        assert G.has_edge(3, 4)
        assert not G.has_edge(1, 4)

    def test_add_cycle(self):
        G = gx.Graph()
        G.add_cycle([1, 2, 3])
        assert G.has_edge(1, 2)
        assert G.has_edge(2, 3)
        assert G.has_edge(3, 1)

    def test_size(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2, {"weight": 2.0}), (2, 3, {"weight": 3.0})])
        assert G.size() == 2
        assert G.size(weight="weight") == 5.0

    def test_edges_view_iter(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (3, 4)])
        edge_set = set(frozenset(e) for e in G.edges)
        assert frozenset({1, 2}) in edge_set
        assert frozenset({3, 4}) in edge_set

    def test_edges_data(self):
        G = gx.Graph()
        G.add_edge("A", "B", weight=9.0)
        edges = list(G.edges(data=True))
        assert len(edges) == 1
        u, v, d = edges[0]
        assert d["weight"] == 9.0

    def test_nodes_data(self):
        G = gx.Graph()
        G.add_node(1, color="blue")
        result = dict(G.nodes(data="color"))
        assert result[1] == "blue"

    def test_adj_view(self):
        G = gx.Graph()
        G.add_edge(1, 2, weight=7.0)
        adj = G.adj[1]
        assert 2 in adj
        assert adj[2]["weight"] == 7.0

    def test_graph_attrs(self):
        G = gx.Graph(name="test", directed=False)
        assert G.graph["name"] == "test"

    def test_hashable_node_types(self):
        G = gx.Graph()
        G.add_node("string")
        G.add_node(42)
        G.add_node((1, 2))
        G.add_edge("string", 42)
        assert G.has_edge("string", 42)

    def test_large_graph_no_oom(self):
        G = gx.Graph()
        for i in range(10_000):
            G.add_edge(i, (i + 1) % 10_000)
        assert G.number_of_nodes() == 10_000
        assert G.number_of_edges() == 10_000


class TestDiGraphBasics:
    def test_directed_edges(self):
        G = gx.DiGraph()
        G.add_edge("A", "B")
        assert G.has_edge("A", "B")
        assert not G.has_edge("B", "A")

    def test_successors(self):
        G = gx.DiGraph()
        G.add_edges_from([("A", "B"), ("A", "C")])
        assert set(G.successors("A")) == {"B", "C"}

    def test_predecessors(self):
        G = gx.DiGraph()
        G.add_edges_from([("A", "C"), ("B", "C")])
        assert set(G.predecessors("C")) == {"A", "B"}

    def test_in_out_degree(self):
        G = gx.DiGraph()
        G.add_edges_from([(1, 2), (1, 3), (3, 2)])
        assert G.in_degree[2] == 2
        assert G.out_degree[1] == 2

    def test_reverse(self):
        G = gx.DiGraph()
        G.add_edge(1, 2)
        R = G.reverse()
        assert R.has_edge(2, 1)
        assert not R.has_edge(1, 2)

    def test_to_undirected(self):
        G = gx.DiGraph()
        G.add_edge(1, 2)
        U = G.to_undirected()
        assert not U.is_directed()
        assert U.has_edge(1, 2)
        assert U.has_edge(2, 1)

    def test_neighbors_equals_successors(self):
        G = gx.DiGraph()
        G.add_edges_from([(1, 2), (1, 3)])
        assert set(G.neighbors(1)) == set(G.successors(1))

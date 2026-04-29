"""
Tests for all graph algorithms.
"""

import pytest

import grapx as gx
from grapx.exception import NetworkXNoPath, NodeNotFound


class TestShortestPaths:
    def test_simple_path(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4)])
        path = gx.shortest_path(G, 1, 4)
        assert path == [1, 2, 3, 4]

    def test_weighted_path(self):
        G = gx.Graph()
        G.add_edge(1, 2, weight=1.0)
        G.add_edge(2, 3, weight=1.0)
        G.add_edge(1, 3, weight=5.0)
        path = gx.shortest_path(G, 1, 3, weight="weight")
        assert path == [1, 2, 3]

    def test_same_source_target(self):
        G = gx.Graph()
        G.add_node(1)
        path = gx.shortest_path(G, 1, 1)
        assert path == [1]

    def test_no_path_raises(self):
        G = gx.Graph()
        G.add_node(1)
        G.add_node(2)
        with pytest.raises(NetworkXNoPath):
            gx.shortest_path(G, 1, 2)

    def test_missing_node_raises(self):
        G = gx.Graph()
        G.add_node(1)
        with pytest.raises(NodeNotFound):
            gx.shortest_path(G, 1, 999)

    def test_shortest_path_length(self):
        G = gx.Graph()
        G.add_edge(1, 2, weight=2.5)
        G.add_edge(2, 3, weight=1.5)
        length = gx.shortest_path_length(G, 1, 3, weight="weight")
        assert pytest.approx(length) == 4.0

    def test_has_path_true(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (2, 3)])
        assert gx.has_path(G, 1, 3)

    def test_has_path_false(self):
        G = gx.Graph()
        G.add_node(1)
        G.add_node(99)
        assert not gx.has_path(G, 1, 99)


class TestPageRank:
    def test_pagerank_sums_to_one(self):
        G = gx.DiGraph()
        G.add_edges_from([("A", "B"), ("B", "C"), ("C", "A"), ("A", "C")])
        pr = gx.pagerank(G, alpha=0.85)
        assert set(pr.keys()) == {"A", "B", "C"}
        assert abs(sum(pr.values()) - 1.0) < 1e-4

    def test_pagerank_hub_node(self):
        G = gx.DiGraph()
        # C receives links from everyone → highest PageRank
        for src in ["A", "B", "D", "E"]:
            G.add_edge(src, "C")
        pr = gx.pagerank(G)
        assert max(pr, key=pr.get) == "C"

    def test_pagerank_empty_graph(self):
        G = gx.DiGraph()
        pr = gx.pagerank(G)
        assert pr == {}

    def test_pagerank_single_node(self):
        G = gx.DiGraph()
        G.add_node("solo")
        pr = gx.pagerank(G)
        assert pytest.approx(pr.get("solo", 0.0), abs=1e-4) == 1.0

    def test_pagerank_invalid_alpha_raises(self):
        from pydantic import ValidationError

        G = gx.DiGraph()
        G.add_edge(1, 2)
        with pytest.raises(ValidationError):
            gx.pagerank(G, alpha=1.5)

    def test_pagerank_undirected(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 1)])
        pr = gx.pagerank(G)
        assert set(pr.keys()) == {1, 2, 3}
        # All nodes equivalent → equal scores
        scores = list(pr.values())
        assert max(scores) - min(scores) < 0.01


class TestConnectedComponents:
    def test_connected(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 1)])
        assert gx.is_connected(G)

    def test_disconnected(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (2, 3)])
        G.add_edge(10, 11)
        comps = list(gx.connected_components(G))
        assert len(comps) == 2
        assert {1, 2, 3} in comps
        assert {10, 11} in comps

    def test_number_connected_components(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (3, 4)])
        assert gx.number_connected_components(G) == 2

    def test_empty_graph_connectivity_raises(self):
        G = gx.Graph()
        with pytest.raises(ValueError):
            gx.is_connected(G)

    def test_weakly_connected(self):
        G = gx.DiGraph()
        G.add_edge(1, 2)
        G.add_edge(3, 4)
        wcc = list(gx.weakly_connected_components(G))
        assert len(wcc) == 2

    def test_weakly_connected_single(self):
        G = gx.DiGraph()
        G.add_edges_from([(1, 2), (3, 2)])
        assert gx.is_weakly_connected(G)

    def test_strongly_connected(self):
        G = gx.DiGraph()
        G.add_edges_from([(1, 2), (2, 3), (3, 1)])
        sccs = list(gx.strongly_connected_components(G))
        assert len(sccs) == 1
        assert sccs[0] == {1, 2, 3}

    def test_strongly_not_connected(self):
        G = gx.DiGraph()
        G.add_edges_from([(1, 2), (2, 3)])  # no cycle
        sccs = list(gx.strongly_connected_components(G))
        assert len(sccs) == 3

    def test_is_strongly_connected_false(self):
        G = gx.DiGraph()
        G.add_edges_from([(1, 2), (2, 3)])
        assert not gx.is_strongly_connected(G)


class TestCentrality:
    def test_degree_centrality_star(self):
        G = gx.Graph()
        G.add_star([0, 1, 2, 3, 4])
        dc = gx.degree_centrality(G)
        assert dc[0] == pytest.approx(1.0)
        for i in range(1, 5):
            assert dc[i] == pytest.approx(0.25)

    def test_degree_centrality_single(self):
        G = gx.Graph()
        G.add_node(1)
        dc = gx.degree_centrality(G)
        assert dc[1] == 0.0

    def test_betweenness_centrality_path(self):
        G = gx.Graph()
        G.add_path([1, 2, 3, 4, 5])
        bc = gx.betweenness_centrality(G)
        # Middle node should have highest betweenness
        assert bc[3] > bc[1]
        assert bc[3] > bc[5]

    def test_betweenness_centrality_clique(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (1, 3), (2, 3)])  # triangle
        bc = gx.betweenness_centrality(G)
        # All nodes equivalent in triangle
        assert all(abs(v) < 0.01 for v in bc.values())

    def test_closeness_centrality(self):
        G = gx.Graph()
        G.add_path([1, 2, 3])
        cc = gx.closeness_centrality(G)
        # Middle node should have highest closeness
        assert cc[2] > cc[1]
        assert cc[2] > cc[3]


class TestTraversal:
    def test_bfs_tree_nodes(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (1, 3), (2, 4)])
        T = gx.bfs_tree(G, 1)
        assert 1 in T.nodes()
        assert 4 in T.nodes()

    def test_bfs_tree_is_tree(self):
        G = gx.Graph()
        G.add_path([1, 2, 3, 4, 5])
        T = gx.bfs_tree(G, 1)
        # A BFS tree of a path has n-1 edges
        assert T.number_of_edges() == G.number_of_nodes() - 1

    def test_dfs_tree_nodes(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (1, 3), (2, 4)])
        T = gx.dfs_tree(G, 1)
        assert 1 in T.nodes()
        assert 4 in T.nodes()

    def test_bfs_edges(self):
        G = gx.Graph()
        G.add_edges_from([(1, 2), (1, 3), (2, 4)])
        edges = list(gx.bfs_edges(G, 1))
        # Source should be first side of all edges
        for u, v in edges:
            assert G.has_edge(u, v)

    def test_dfs_edges(self):
        G = gx.Graph()
        G.add_path([1, 2, 3, 4])
        edges = list(gx.dfs_edges(G, 1))
        assert len(edges) == 3

    def test_traversal_missing_source_raises(self):
        G = gx.Graph()
        G.add_node(1)
        with pytest.raises(NodeNotFound):
            gx.bfs_tree(G, 999)

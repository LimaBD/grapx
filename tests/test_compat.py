"""
Compatibility test suite.

These tests verify that grapx behaves identically to the expected
interface, so users can switch from any graph library to grapx
by changing a single import line.

Run with:
    pytest tests/test_compat.py -v
"""

import pytest

import grapx as gx

# ─── Basic graph operations ─────────────────────────────────────────────────


def test_basic_graph():
    G = gx.Graph()
    G.add_edge(1, 2, weight=1.5)
    G.add_edge(2, 3, weight=2.0)
    assert G.has_edge(1, 2)
    assert G.has_edge(2, 1)  # undirected: symmetric
    assert G.number_of_nodes() == 3
    assert G.number_of_edges() == 2


def test_digraph_directed():
    G = gx.DiGraph()
    G.add_edge("A", "B")
    G.add_edge("B", "C")
    assert G.has_edge("A", "B")
    assert not G.has_edge("B", "A")  # directed: asymmetric


def test_add_nodes_from():
    G = gx.Graph()
    G.add_nodes_from([1, 2, 3])
    G.add_nodes_from([(4, {"color": "red"})])
    assert 4 in G
    assert len(G) == 4


def test_add_edges_from():
    G = gx.Graph()
    G.add_edges_from([(1, 2), (2, 3), (3, 4)])
    assert G.number_of_edges() == 3


def test_neighbors():
    G = gx.Graph()
    G.add_edges_from([(1, 2), (1, 3), (1, 4)])
    assert set(G.neighbors(1)) == {2, 3, 4}


def test_pagerank():
    G = gx.DiGraph()
    G.add_edge("A", "B")
    G.add_edge("B", "C")
    G.add_edge("C", "A")
    G.add_edge("A", "C")

    pr = gx.pagerank(G, alpha=0.85)
    assert set(pr.keys()) == {"A", "B", "C"}
    assert abs(sum(pr.values()) - 1.0) < 1e-4


def test_shortest_path():
    G = gx.Graph()
    G.add_edges_from([(1, 2, {"weight": 1}), (2, 3, {"weight": 1}), (1, 3, {"weight": 5})])
    path = gx.shortest_path(G, 1, 3, weight="weight")
    assert path == [1, 2, 3]  # cheapest route


def test_connected_components():
    G = gx.Graph()
    G.add_edges_from([(1, 2), (2, 3)])
    G.add_edge(10, 11)
    comps = list(gx.connected_components(G))
    assert len(comps) == 2
    assert {1, 2, 3} in comps
    assert {10, 11} in comps


def test_is_connected():
    G = gx.Graph()
    G.add_edges_from([(1, 2), (2, 3), (3, 1)])
    assert gx.is_connected(G)


def test_weakly_connected():
    G = gx.DiGraph()
    G.add_edge(1, 2)
    G.add_edge(3, 4)
    wcc = list(gx.weakly_connected_components(G))
    assert len(wcc) == 2


def test_strongly_connected():
    G = gx.DiGraph()
    G.add_edges_from([(1, 2), (2, 3), (3, 1)])
    sccs = list(gx.strongly_connected_components(G))
    assert len(sccs) == 1
    assert sccs[0] == {1, 2, 3}


def test_degree_centrality():
    G = gx.Graph()
    G.add_star([0, 1, 2, 3, 4])
    dc = gx.degree_centrality(G)
    assert dc[0] == pytest.approx(1.0)  # hub node connected to all


def test_bfs():
    G = gx.Graph()
    G.add_edges_from([(1, 2), (1, 3), (2, 4)])
    bfs_nodes = list(gx.bfs_tree(G, 1).nodes())
    assert 1 in bfs_nodes
    assert 4 in bfs_nodes


def test_node_attrs():
    G = gx.Graph()
    G.add_node("Alice", age=30, city="BA")
    assert G.nodes["Alice"]["age"] == 30


def test_edge_attrs():
    G = gx.Graph()
    G.add_edge("A", "B", weight=3.14, color="red")
    data = G.get_edge_data("A", "B")
    assert data["weight"] == pytest.approx(3.14)
    assert data["color"] == "red"


def test_graph_repr():
    G = gx.Graph()
    G.add_edges_from([(1, 2), (2, 3)])
    r = repr(G)
    assert "Graph" in r


def test_contains():
    G = gx.Graph()
    G.add_nodes_from([1, 2, 3])
    assert 1 in G
    assert 99 not in G


def test_has_path():
    G = gx.Graph()
    G.add_edges_from([(1, 2), (2, 3)])
    assert gx.has_path(G, 1, 3)
    assert not gx.has_path(G, 1, 99)


def test_large_graph_basic():
    """Verify no OOM/crash on medium-sized graphs."""
    G = gx.Graph()
    for i in range(10_000):
        G.add_edge(i, (i + 1) % 10_000)
    assert G.number_of_nodes() == 10_000
    assert G.number_of_edges() == 10_000


def test_directed_pagerank_known_result():
    """
    In a two-node graph A ↔ B with equal links, PageRank should be ~0.5 each.
    """
    G = gx.DiGraph()
    G.add_edge("A", "B")
    G.add_edge("B", "A")
    pr = gx.pagerank(G, alpha=0.85)
    assert pr["A"] == pytest.approx(0.5, abs=0.01)
    assert pr["B"] == pytest.approx(0.5, abs=0.01)


def test_single_node_connected():
    G = gx.Graph()
    G.add_node(42)
    comps = list(gx.connected_components(G))
    assert len(comps) == 1
    assert comps[0] == {42}


def test_digraph_in_out_degree():
    G = gx.DiGraph()
    G.add_edges_from([(1, 2), (1, 3), (3, 2)])
    assert G.in_degree[2] == 2
    assert G.out_degree[1] == 2


def test_edge_view_data_param():
    G = gx.Graph()
    G.add_edge(1, 2, weight=99.0)
    edges_w = list(G.edges(data="weight"))
    assert any(w == 99.0 for _, _, w in edges_w)


def test_nodes_data_specific_attr():
    G = gx.Graph()
    G.add_node("x", score=7)
    result = dict(G.nodes(data="score"))
    assert result["x"] == 7


def test_graph_update():
    G = gx.Graph()
    G.add_edge(1, 2)
    H = gx.Graph()
    H.update(G)
    assert H.has_edge(1, 2)


def test_predecessors_digraph():
    G = gx.DiGraph()
    G.add_edges_from([("A", "C"), ("B", "C")])
    assert set(G.predecessors("C")) == {"A", "B"}


def test_bfs_tree_is_digraph():
    G = gx.Graph()
    G.add_path([1, 2, 3])
    T = gx.bfs_tree(G, 1)
    assert T.is_directed()


def test_dfs_tree_coverage():
    G = gx.Graph()
    G.add_path([1, 2, 3, 4, 5])
    T = gx.dfs_tree(G, 1)
    assert set(T.nodes()) == set(G.nodes())


def test_strongly_connected_chain():
    """Chain A→B→C has no cycle → each node is its own SCC."""
    G = gx.DiGraph()
    G.add_edges_from([("A", "B"), ("B", "C")])
    sccs = list(gx.strongly_connected_components(G))
    assert len(sccs) == 3


def test_number_of_edges_directed():
    G = gx.DiGraph()
    G.add_edges_from([(1, 2), (2, 1)])  # two directed edges
    assert G.number_of_edges() == 2


def test_order_equals_len():
    G = gx.Graph()
    G.add_nodes_from([1, 2, 3, 4])
    assert G.order() == len(G) == 4

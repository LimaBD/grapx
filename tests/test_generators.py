"""
Tests for graph generators.
"""

import pytest

import grapx as gx


class TestGenerators:
    def test_complete_graph(self):
        G = gx.complete_graph(5)
        assert G.number_of_nodes() == 5
        assert G.number_of_edges() == 10  # C(5,2) = 10

    def test_path_graph(self):
        G = gx.path_graph(5)
        assert G.number_of_nodes() == 5
        assert G.number_of_edges() == 4

    def test_cycle_graph(self):
        G = gx.cycle_graph(5)
        assert G.number_of_nodes() == 5
        assert G.number_of_edges() == 5
        assert gx.is_connected(G)

    def test_star_graph(self):
        G = gx.star_graph(4)
        assert G.number_of_nodes() == 5  # hub + 4 leaves
        assert G.number_of_edges() == 4
        assert G.degree[0] == 4  # hub

    def test_barabasi_albert(self):
        G = gx.barabasi_albert_graph(100, 2, seed=42)
        assert G.number_of_nodes() == 100
        assert G.number_of_edges() > 0
        assert gx.is_connected(G)

    def test_barabasi_albert_invalid_m(self):
        with pytest.raises(ValueError):
            gx.barabasi_albert_graph(5, 0)

    def test_erdos_renyi_zero_prob(self):
        G = gx.erdos_renyi_graph(10, 0.0, seed=0)
        assert G.number_of_edges() == 0

    def test_erdos_renyi_full_prob(self):
        G = gx.erdos_renyi_graph(5, 1.0, seed=0)
        assert G.number_of_edges() == 10  # complete graph

    def test_erdos_renyi_directed(self):
        G = gx.erdos_renyi_graph(5, 1.0, directed=True, seed=0)
        assert G.is_directed()
        assert G.number_of_edges() == 20  # n*(n-1)

    def test_erdos_renyi_invalid_p(self):
        with pytest.raises(ValueError):
            gx.erdos_renyi_graph(10, 1.5)

    def test_watts_strogatz(self):
        G = gx.watts_strogatz_graph(20, 4, 0.3, seed=42)
        assert G.number_of_nodes() == 20
        assert gx.is_connected(G)

    def test_karate_club_graph(self):
        G = gx.karate_club_graph()
        assert G.number_of_nodes() == 34
        assert G.number_of_edges() == 78
        assert gx.is_connected(G)

    def test_grid_2d_graph(self):
        G = gx.grid_2d_graph(3, 4)
        assert G.number_of_nodes() == 12
        assert G.number_of_edges() == 17  # 3*3 + 2*4
        assert (0, 0) in G
        assert G.has_edge((0, 0), (0, 1))
        assert G.has_edge((0, 0), (1, 0))

    def test_grid_2d_periodic(self):
        G = gx.grid_2d_graph(3, 3, periodic=True)
        # Nodes on edge should connect to wrap-around
        assert G.has_edge((0, 0), (0, 2))

    def test_empty_graph(self):
        G = gx.empty_graph(5)
        assert G.number_of_nodes() == 5
        assert G.number_of_edges() == 0

    def test_petersen_graph(self):
        G = gx.petersen_graph()
        assert G.number_of_nodes() == 10
        assert G.number_of_edges() == 15

    def test_null_graph(self):
        G = gx.null_graph()
        assert len(G) == 0

    def test_trivial_graph(self):
        G = gx.trivial_graph()
        assert len(G) == 1

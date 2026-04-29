"""
grapx
======
High-performance graph computing with a zero-learning-curve Python API
and a Rust core.

Quick start
-----------
>>> import grapx as gx
>>> G = gx.DiGraph()
>>> G.add_edge("Alice", "Bob", weight=1.5)
>>> G.add_edge("Bob", "Carol", weight=2.0)
>>> gx.pagerank(G)
{'Alice': ..., 'Bob': ..., 'Carol': ...}

Migrating from another graph library?  Change one line — the rest of your
code stays exactly the same.
"""

__version__ = "0.1.0"
__author__ = "Bruno Lima"
__email__ = "contact@brunolima.dev"
__license__ = "MIT"

# ─── Graph types ────────────────────────────────────────────────────────────
# ─── Sub-module references (for gx.algorithms.* style access) ───────────────
from grapx import algorithms, generators, readwrite  # noqa: F401
from grapx.algorithms.centrality import (
    betweenness_centrality,
    closeness_centrality,
    degree_centrality,
    in_degree_centrality,
    out_degree_centrality,
)
from grapx.algorithms.components import (
    condensation,
    connected_components,
    is_connected,
    is_strongly_connected,
    is_weakly_connected,
    node_connected_component,
    number_connected_components,
    number_strongly_connected_components,
    number_weakly_connected_components,
    strongly_connected_components,
    weakly_connected_components,
)
from grapx.algorithms.link_analysis import hits, pagerank

# ─── Algorithms ─────────────────────────────────────────────────────────────
from grapx.algorithms.shortest_paths import (
    all_pairs_shortest_path_length,
    has_path,
    shortest_path,
    shortest_path_length,
)
from grapx.algorithms.traversal import (
    bfs_edges,
    bfs_predecessors,
    bfs_successors,
    bfs_tree,
    dfs_edges,
    dfs_preorder_nodes,
    dfs_tree,
)
from grapx.classes.digraph import DiGraph
from grapx.classes.graph import Graph
from grapx.classes.multigraph import MultiDiGraph, MultiGraph

# ─── Exceptions ─────────────────────────────────────────────────────────────
from grapx.exception import (
    GrapxAlgorithmError,
    GrapxError,
    NetworkXError,
    NetworkXNoPath,
    NodeNotFound,
)

# ─── Generators ─────────────────────────────────────────────────────────────
from grapx.generators import (
    barabasi_albert_graph,
    complete_graph,
    cycle_graph,
    empty_graph,
    erdos_renyi_graph,
    grid_2d_graph,
    karate_club_graph,
    null_graph,
    path_graph,
    petersen_graph,
    star_graph,
    trivial_graph,
    watts_strogatz_graph,
)

# ─── I/O ────────────────────────────────────────────────────────────────────
from grapx.readwrite import generate_edgelist, read_edgelist, write_edgelist

__all__ = [
    # graph types
    "Graph",
    "DiGraph",
    "MultiGraph",
    "MultiDiGraph",
    # shortest paths
    "shortest_path",
    "shortest_path_length",
    "has_path",
    "all_pairs_shortest_path_length",
    # link analysis
    "pagerank",
    "hits",
    # components
    "connected_components",
    "number_connected_components",
    "is_connected",
    "node_connected_component",
    "weakly_connected_components",
    "number_weakly_connected_components",
    "is_weakly_connected",
    "strongly_connected_components",
    "number_strongly_connected_components",
    "is_strongly_connected",
    "condensation",
    # centrality
    "degree_centrality",
    "betweenness_centrality",
    "closeness_centrality",
    "in_degree_centrality",
    "out_degree_centrality",
    # traversal
    "bfs_tree",
    "dfs_tree",
    "bfs_edges",
    "dfs_edges",
    "bfs_predecessors",
    "bfs_successors",
    "dfs_preorder_nodes",
    # generators
    "karate_club_graph",
    "barabasi_albert_graph",
    "erdos_renyi_graph",
    "watts_strogatz_graph",
    "complete_graph",
    "path_graph",
    "cycle_graph",
    "star_graph",
    "grid_2d_graph",
    "empty_graph",
    "null_graph",
    "trivial_graph",
    "petersen_graph",
    # I/O
    "read_edgelist",
    "write_edgelist",
    "generate_edgelist",
    # exceptions
    "GrapxError",
    "NetworkXError",
    "NetworkXNoPath",
    "NodeNotFound",
    "GrapxAlgorithmError",
    # sub-modules (available as gx.algorithms, gx.generators, gx.readwrite)
    "algorithms",
    "generators",
    "readwrite",
    # version
    "__version__",
]

"""
grapx.generators.classic
~~~~~~~~~~~~~~~~~~~~~~~~~~
Classic graph generators — no external dependencies required.
"""

from __future__ import annotations

import random
from typing import Optional

from grapx.classes.digraph import DiGraph
from grapx.classes.graph import Graph

# ─── Zachary karate club dataset (hardcoded — classic benchmark) ────────────

_KARATE_EDGES = [
    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8),
    (0, 10), (0, 11), (0, 12), (0, 13), (0, 17), (0, 19), (0, 21), (0, 31),
    (1, 2), (1, 3), (1, 7), (1, 13), (1, 17), (1, 19), (1, 21), (1, 30),
    (2, 3), (2, 7), (2, 8), (2, 9), (2, 13), (2, 27), (2, 28), (2, 32),
    (3, 7), (3, 12), (3, 13),
    (4, 6), (4, 10),
    (5, 6), (5, 10), (5, 16),
    (6, 16),
    (8, 30), (8, 32), (8, 33),
    (9, 33),
    (13, 33),
    (14, 32), (14, 33),
    (15, 32), (15, 33),
    (18, 32), (18, 33),
    (19, 33),
    (20, 32), (20, 33),
    (22, 32), (22, 33),
    (23, 25), (23, 27), (23, 29), (23, 32), (23, 33),
    (24, 25), (24, 27), (24, 31),
    (25, 31),
    (26, 29), (26, 33),
    (27, 33),
    (28, 31), (28, 33),
    (29, 32), (29, 33),
    (30, 32), (30, 33),
    (31, 32), (31, 33),
    (32, 33),
]


def karate_club_graph() -> Graph:
    """
    Return Zachary's karate club social network (34 nodes, 78 edges).

    This is the canonical benchmark graph for community-detection algorithms.
    """
    G = Graph()
    G.add_edges_from(_KARATE_EDGES)
    return G


# ─── Random graph generators ────────────────────────────────────────────────


def barabasi_albert_graph(n: int, m: int, seed: Optional[int] = None) -> Graph:
    """
    Barabási–Albert preferential-attachment graph.

    Produces a scale-free network where new nodes attach to existing nodes
    with probability proportional to their degree.

    Parameters
    ----------
    n : int
        Target number of nodes.
    m : int
        Number of edges to attach per new node.
    seed : int or None
        Random seed for reproducibility.
    """
    if m < 1 or m >= n:
        raise ValueError(f"m must satisfy 1 <= m < n, got m={m}, n={n}")

    rng = random.Random(seed)
    G = Graph()

    # Seed graph: complete graph on m nodes
    initial = list(range(m))
    G.add_edges_from((i, j) for i in initial for j in range(i + 1, m))

    # Repeated nodes list for O(1) preferential attachment sampling
    repeated_nodes = [v for v, d in G.degree for _ in range(d)]

    for new_node in range(m, n):
        targets: set = set()
        while len(targets) < m:
            targets.add(rng.choice(repeated_nodes))
        for t in targets:
            G.add_edge(new_node, t)
        repeated_nodes.extend(targets)
        repeated_nodes.extend([new_node] * m)

    return G


def erdos_renyi_graph(
    n: int, p: float, seed: Optional[int] = None, directed: bool = False
) -> Graph:
    """
    Erdős–Rényi G(n, p) random graph.

    Each possible edge is included independently with probability *p*.

    Parameters
    ----------
    n : int
        Number of nodes.
    p : float
        Probability of each edge existing  (0 ≤ p ≤ 1).
    seed : int or None
        Random seed.
    directed : bool
        If ``True``, return a ``DiGraph``.
    """
    if not (0.0 <= p <= 1.0):
        raise ValueError(f"p must be in [0, 1], got {p}")

    rng = random.Random(seed)
    G: Graph = DiGraph() if directed else Graph()
    G.add_nodes_from(range(n))

    pairs = (
        ((u, v) for u in range(n) for v in range(n) if u != v)
        if directed
        else ((u, v) for u in range(n) for v in range(u + 1, n))
    )
    for u, v in pairs:
        if rng.random() < p:
            G.add_edge(u, v)

    return G


def watts_strogatz_graph(n: int, k: int, p: float, seed: Optional[int] = None) -> Graph:
    """
    Watts–Strogatz small-world graph.

    Start with a ring lattice of *n* nodes each connected to *k* nearest
    neighbours.  Then rewire each edge with probability *p*.

    Parameters
    ----------
    n : int
        Number of nodes.
    k : int
        Each node is initially connected to *k* nearest neighbours (k must be even).
    p : float
        Rewiring probability.
    seed : int or None
        Random seed.
    """
    if k % 2 != 0:
        raise ValueError("k must be even")
    if not (0.0 <= p <= 1.0):
        raise ValueError(f"p must be in [0, 1], got {p}")

    rng = random.Random(seed)
    G = Graph()
    G.add_nodes_from(range(n))

    # Ring lattice
    for j in range(1, k // 2 + 1):
        for i in range(n):
            G.add_edge(i, (i + j) % n)

    # Rewire
    for j in range(1, k // 2 + 1):
        for u in range(n):
            if rng.random() < p:
                v = (u + j) % n
                # Choose new target, avoiding self-loops and duplicates
                candidates = [w for w in range(n) if w != u and not G.has_edge(u, w)]
                if candidates:
                    w = rng.choice(candidates)
                    G.remove_edge(u, v)
                    G.add_edge(u, w)

    return G


# ─── Classic deterministic generators ───────────────────────────────────────


def complete_graph(n: int, create_using=None) -> Graph:
    """Complete graph K_n."""
    G: Graph = create_using() if create_using else Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from((i, j) for i in range(n) for j in range(i + 1, n))
    return G


def path_graph(n: int, create_using=None) -> Graph:
    """Path graph P_n (a chain of *n* nodes)."""
    G: Graph = create_using() if create_using else Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from((i, i + 1) for i in range(n - 1))
    return G


def cycle_graph(n: int, create_using=None) -> Graph:
    """Cycle graph C_n."""
    G: Graph = create_using() if create_using else Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from((i, (i + 1) % n) for i in range(n))
    return G


def star_graph(n: int, create_using=None) -> Graph:
    """
    Star graph S_n.

    Node 0 is the hub connected to nodes 1 … n.
    The total node count is n + 1.
    """
    G: Graph = create_using() if create_using else Graph()
    G.add_nodes_from(range(n + 1))
    G.add_edges_from((0, i) for i in range(1, n + 1))
    return G


def grid_2d_graph(m: int, n: int, periodic: bool = False, create_using=None) -> Graph:
    """
    2D grid graph.

    Nodes are ``(i, j)`` tuples for ``0 ≤ i < m``, ``0 ≤ j < n``.

    Parameters
    ----------
    m, n : int
        Grid dimensions.
    periodic : bool
        If ``True``, add wrap-around edges (torus topology).
    """
    G: Graph = create_using() if create_using else Graph()
    G.add_nodes_from((i, j) for i in range(m) for j in range(n))
    G.add_edges_from(((i, j), (i, j + 1)) for i in range(m) for j in range(n - 1))
    G.add_edges_from(((i, j), (i + 1, j)) for i in range(m - 1) for j in range(n))
    if periodic:
        G.add_edges_from(((i, 0), (i, n - 1)) for i in range(m))
        G.add_edges_from(((0, j), (m - 1, j)) for j in range(n))
    return G


def empty_graph(n: int = 0, create_using=None) -> Graph:
    """Graph with *n* nodes and no edges."""
    G: Graph = create_using() if create_using else Graph()
    G.add_nodes_from(range(n))
    return G


def null_graph() -> Graph:
    """The null graph — zero nodes, zero edges."""
    return Graph()


def trivial_graph() -> Graph:
    """The trivial graph — one node, no edges."""
    G = Graph()
    G.add_node(0)
    return G


def petersen_graph() -> Graph:
    """Return the Petersen graph (10 nodes, 15 edges)."""
    edges = [
        (0, 1), (0, 4), (0, 5), (1, 2), (1, 6), (2, 3), (2, 7),
        (3, 4), (3, 8), (4, 9), (5, 7), (5, 8), (6, 8), (6, 9), (7, 9),
    ]
    G = Graph()
    G.add_edges_from(edges)
    return G


__all__ = [
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
]

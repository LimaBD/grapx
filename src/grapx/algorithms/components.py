"""
grapx.algorithms.components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Connected / weakly-connected / strongly-connected component algorithms,
all backed by the Rust core.
"""

from __future__ import annotations

from typing import Generator


def connected_components(G) -> Generator[set, None, None]:
    """
    Yield sets of nodes, one per connected component of *G* (undirected).

    The computation runs in Rust; only the node-index → Python-node translation
    happens in Python.
    """
    for comp in G._rust.connected_components():
        component = {
            G._idx_to_node[i]
            for i in comp
            if i < len(G._idx_to_node)
            and G._idx_to_node[i] is not None
            and G._idx_to_node[i] in G._node
        }
        if component:
            yield component


def number_connected_components(G) -> int:
    """Return the number of connected components."""
    return sum(1 for _ in connected_components(G))


def is_connected(G) -> bool:
    """Return ``True`` if *G* is connected (single component)."""
    if len(G) == 0:
        raise ValueError("Connectivity is undefined for the empty graph")
    return number_connected_components(G) == 1


def node_connected_component(G, n) -> set:
    """Return the set of nodes in the connected component containing *n*."""
    for comp in connected_components(G):
        if n in comp:
            return comp
    from grapx.exception import NodeNotFound
    raise NodeNotFound(f"Node {n!r} not in graph")


# ─── Directed-graph variants ─────────────────────────────────────────────────


def weakly_connected_components(G) -> Generator[set, None, None]:
    """
    Yield weakly-connected components of directed graph *G*.

    A weakly-connected component is a set of nodes connected when edge
    directions are ignored.
    """
    for comp in G._rust.weakly_connected_components():
        component = {
            G._idx_to_node[i]
            for i in comp
            if i < len(G._idx_to_node)
            and G._idx_to_node[i] is not None
            and G._idx_to_node[i] in G._node
        }
        if component:
            yield component


def number_weakly_connected_components(G) -> int:
    return sum(1 for _ in weakly_connected_components(G))


def is_weakly_connected(G) -> bool:
    if len(G) == 0:
        raise ValueError("Connectivity is undefined for the empty graph")
    return number_weakly_connected_components(G) == 1


def strongly_connected_components(G) -> Generator[set, None, None]:
    """
    Yield strongly-connected components of directed graph *G* (Kosaraju).
    """
    for scc in G._rust.strongly_connected_components():
        component = {
            G._idx_to_node[i]
            for i in scc
            if i < len(G._idx_to_node)
            and G._idx_to_node[i] is not None
            and G._idx_to_node[i] in G._node
        }
        if component:
            yield component


def number_strongly_connected_components(G) -> int:
    return sum(1 for _ in strongly_connected_components(G))


def is_strongly_connected(G) -> bool:
    if len(G) == 0:
        raise ValueError("Connectivity is undefined for the empty graph")
    return number_strongly_connected_components(G) == 1


def condensation(G):
    """
    Return the condensation of *G* — a DAG of SCCs.
    Each node in the result is a frozenset of original nodes.
    """
    from grapx.classes.digraph import DiGraph as _DiGraph
    mapping = {}
    C = _DiGraph()
    for i, scc in enumerate(strongly_connected_components(G)):
        C.add_node(i, members=frozenset(scc))
        for n in scc:
            mapping[n] = i
    for u, v in G.edges():
        cu, cv = mapping.get(u), mapping.get(v)
        if cu is not None and cv is not None and cu != cv:
            C.add_edge(cu, cv)
    return C


__all__ = [
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
]

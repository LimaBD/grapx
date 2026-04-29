"""
grapx.algorithms.traversal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
BFS and DFS traversal algorithms backed by the Rust core.
"""

from __future__ import annotations

from grapx.classes.digraph import DiGraph
from grapx.classes.graph import Graph
from grapx.exception import NodeNotFound


def bfs_tree(G, source, reverse: bool = False, depth_limit=None) -> Graph:
    """
    Return a directed BFS tree rooted at *source*.

    The returned graph is a ``DiGraph`` whose edges represent the BFS
    discovery tree.

    Parameters
    ----------
    G : Graph or DiGraph
    source : node
        Root of the BFS tree.
    reverse : bool
        If ``True`` and *G* is directed, traverse predecessors instead.
    depth_limit : int or None
        Limit on BFS depth (currently not enforced in v0.1 Rust code).

    Returns
    -------
    DiGraph
    """
    if source not in G:
        raise NodeNotFound(f"Source node {source!r} not in graph")

    T = DiGraph()
    T.add_node(source)

    src_idx = G._node_to_idx[source]
    tree_edges = G._rust.bfs_edges(src_idx)

    for u_idx, v_idx in tree_edges:
        u = G._idx_to_node[u_idx] if u_idx < len(G._idx_to_node) else None
        v = G._idx_to_node[v_idx] if v_idx < len(G._idx_to_node) else None
        if u is not None and v is not None:
            T.add_edge(u, v)

    return T


def dfs_tree(G, source, depth_limit=None) -> DiGraph:
    """
    Return a directed DFS tree rooted at *source*.
    """
    if source not in G:
        raise NodeNotFound(f"Source node {source!r} not in graph")

    T = DiGraph()
    T.add_node(source)

    src_idx = G._node_to_idx[source]
    tree_edges = G._rust.dfs_edges(src_idx)

    for u_idx, v_idx in tree_edges:
        u = G._idx_to_node[u_idx] if u_idx < len(G._idx_to_node) else None
        v = G._idx_to_node[v_idx] if v_idx < len(G._idx_to_node) else None
        if u is not None and v is not None:
            T.add_edge(u, v)

    return T


def bfs_edges(G, source, reverse: bool = False, depth_limit=None, sort_neighbors=None):
    """
    Iterate over edges in a BFS from *source*.

    Yields ``(u, v)`` tuples representing the discovery tree edges.
    """
    if source not in G:
        raise NodeNotFound(f"Source node {source!r} not in graph")

    src_idx = G._node_to_idx[source]
    for u_idx, v_idx in G._rust.bfs_edges(src_idx):
        u = G._idx_to_node[u_idx] if u_idx < len(G._idx_to_node) else None
        v = G._idx_to_node[v_idx] if v_idx < len(G._idx_to_node) else None
        if u is not None and v is not None:
            yield (u, v)


def dfs_edges(G, source=None, depth_limit=None):
    """
    Iterate over edges in a DFS.

    Yields ``(u, v)`` tuples.
    """
    if source is None:
        source = next(iter(G))

    if source not in G:
        raise NodeNotFound(f"Source node {source!r} not in graph")

    src_idx = G._node_to_idx[source]
    for u_idx, v_idx in G._rust.dfs_edges(src_idx):
        u = G._idx_to_node[u_idx] if u_idx < len(G._idx_to_node) else None
        v = G._idx_to_node[v_idx] if v_idx < len(G._idx_to_node) else None
        if u is not None and v is not None:
            yield (u, v)


def bfs_predecessors(G, source, depth_limit=None):
    """Yield ``(node, predecessor)`` in BFS order from *source*."""
    for u, v in bfs_edges(G, source, depth_limit=depth_limit):
        yield (v, u)


def bfs_successors(G, source, depth_limit=None):
    """Yield ``(node, [successors])`` in BFS order from *source*."""
    parent = None
    children = []
    for u, v in bfs_edges(G, source, depth_limit=depth_limit):
        if u == parent:
            children.append(v)
        else:
            if parent is not None:
                yield (parent, children)
            parent = u
            children = [v]
    if parent is not None:
        yield (parent, children)


def dfs_preorder_nodes(G, source=None, depth_limit=None):
    """Yield nodes in DFS pre-order starting from *source*."""
    if source is None:
        source = next(iter(G))
    yield source
    for _u, v in dfs_edges(G, source=source, depth_limit=depth_limit):
        yield v


__all__ = [
    "bfs_tree",
    "dfs_tree",
    "bfs_edges",
    "dfs_edges",
    "bfs_predecessors",
    "bfs_successors",
    "dfs_preorder_nodes",
]

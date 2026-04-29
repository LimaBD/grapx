"""
grapx.algorithms.shortest_paths
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Shortest-path algorithms backed by the Rust Dijkstra implementation.
"""

from __future__ import annotations

import contextlib

from grapx._validation import validate_shortest_path_params
from grapx.exception import NetworkXNoPath, NodeNotFound


def shortest_path(G, source=None, target=None, weight=None, method=None):
    """
    Compute the shortest path between nodes in a graph.

    Parameters
    ----------
    G : Graph or DiGraph
    source : node
        Starting node.
    target : node
        Destination node.
    weight : str or None
        Edge attribute to use as distance. ``None`` = unweighted (hop count).
    method : str or None
        Algorithm hint (currently only Dijkstra is supported).

    Returns
    -------
    list
        Ordered list of nodes on the shortest path from *source* to *target*.

    Raises
    ------
    NodeNotFound
        If *source* or *target* are not in *G*.
    NetworkXNoPath
        If no path exists.
    """
    validate_shortest_path_params(weight=weight, method=method)

    if source is None or target is None:
        raise ValueError("Both 'source' and 'target' are required")

    if source not in G:
        raise NodeNotFound(f"Source node {source!r} not in graph")
    if target not in G:
        raise NodeNotFound(f"Target node {target!r} not in graph")

    if source == target:
        return [source]

    src_idx = G._node_to_idx[source]
    tgt_idx = G._node_to_idx[target]

    result = G._rust.dijkstra(src_idx, tgt_idx)
    if result is None:
        raise NetworkXNoPath(f"No path between {source!r} and {target!r}")

    _dist, path_idxs = result
    return [
        G._idx_to_node[i]
        for i in path_idxs
        if i < len(G._idx_to_node) and G._idx_to_node[i] is not None
    ]


def shortest_path_length(G, source=None, target=None, weight=None, method=None):
    """
    Return the length of the shortest path between two nodes.

    Returns
    -------
    float
        The sum of edge weights (or hop count when ``weight=None``) along the
        shortest path.

    Raises
    ------
    NodeNotFound, NetworkXNoPath
    """
    validate_shortest_path_params(weight=weight, method=method)

    if source is None or target is None:
        raise ValueError("Both 'source' and 'target' are required")

    if source not in G:
        raise NodeNotFound(f"Source node {source!r} not in graph")
    if target not in G:
        raise NodeNotFound(f"Target node {target!r} not in graph")

    if source == target:
        return 0

    src_idx = G._node_to_idx[source]
    tgt_idx = G._node_to_idx[target]

    result = G._rust.dijkstra(src_idx, tgt_idx)
    if result is None:
        raise NetworkXNoPath(f"No path between {source!r} and {target!r}")

    dist, _path = result
    return dist


def has_path(G, source, target) -> bool:
    """
    Return ``True`` if a path exists between *source* and *target*.
    """
    if source not in G or target not in G:
        return False
    if source == target:
        return True

    src_idx = G._node_to_idx.get(source)
    tgt_idx = G._node_to_idx.get(target)

    if src_idx is None or tgt_idx is None:
        return False

    if hasattr(G._rust, "has_path"):
        return bool(G._rust.has_path(src_idx, tgt_idx))

    return G._rust.dijkstra(src_idx, tgt_idx) is not None


def all_pairs_shortest_path_length(G, cutoff=None):
    """
    Compute shortest-path lengths between all pairs of nodes.

    Yields ``(source, {target: length})`` pairs.
    """
    for n in G.nodes():
        lengths = {}
        for m in G.nodes():
            if n == m:
                lengths[m] = 0
                continue
            with contextlib.suppress(NetworkXNoPath):
                lengths[m] = shortest_path_length(G, source=n, target=m)
        yield (n, lengths)


__all__ = [
    "shortest_path",
    "shortest_path_length",
    "has_path",
    "all_pairs_shortest_path_length",
]

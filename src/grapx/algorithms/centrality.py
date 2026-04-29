"""
grapx.algorithms.centrality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Centrality measures.

- ``degree_centrality`` — Rust-parallel (fast)
- ``betweenness_centrality`` — Python Brandes O(VE) (Rust in v0.2)
- ``closeness_centrality`` — Python BFS O(V(V+E)) (Rust in v0.2)
"""

from __future__ import annotations

import collections

from grapx._validation import validate_centrality_params


def degree_centrality(G) -> dict:
    """
    Compute degree centrality for all nodes.

    Defined as ``deg(v) / (n - 1)`` where *n* is the number of nodes.
    Computation runs in parallel inside the Rust core.

    Returns
    -------
    dict
        ``{node: centrality}`` values in [0, 1].
    """
    n = len(G)
    if n <= 1:
        return {v: 0.0 for v in G}

    raw = G._rust.degree_centrality()
    return {
        G._idx_to_node[idx]: score
        for idx, score in raw
        if idx < len(G._idx_to_node)
        and G._idx_to_node[idx] is not None
        and G._idx_to_node[idx] in G._node
    }


def betweenness_centrality(
    G,
    normalized: bool = True,
    weight: str | None = None,
    endpoints: bool = False,
) -> dict:
    """
    Compute betweenness centrality using Brandes' O(VE) algorithm.

    Parameters
    ----------
    G : Graph or DiGraph
    normalized : bool
        Normalize by ``2 / ((n-1)(n-2))`` for undirected graphs.
    weight : str or None
        Edge attribute for weighted shortest paths (currently ignored —
        unweighted BFS used in v0.1).
    endpoints : bool
        Include endpoints in path counts.

    Returns
    -------
    dict
        ``{node: betweenness}`` values.
    """
    validate_centrality_params(normalized=normalized, weight=weight, endpoints=endpoints)

    betweenness: dict = dict.fromkeys(G, 0.0)
    nodes = list(G.nodes())

    for s in nodes:
        # Brandes' algorithm — BFS variant (unweighted)
        S: list = []
        P: dict = {w: [] for w in nodes}
        sigma: dict = dict.fromkeys(nodes, 0.0)
        sigma[s] = 1.0
        d: dict = dict.fromkeys(nodes, -1)
        d[s] = 0
        Q: collections.deque = collections.deque([s])

        while Q:
            v = Q.popleft()
            S.append(v)
            dv = d[v]
            sv = sigma[v]
            for w in G.neighbors(v):
                if d[w] < 0:
                    Q.append(w)
                    d[w] = dv + 1
                if d[w] == dv + 1:
                    sigma[w] += sv
                    P[w].append(v)

        if endpoints:
            for w in nodes:
                if w != s:
                    betweenness[w] += sigma.get(w, 0.0) / sigma[s] if sigma[s] else 0.0

        delta: dict = dict.fromkeys(nodes, 0.0)
        while S:
            w = S.pop()
            for v in P[w]:
                if sigma[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                betweenness[w] += delta[w]

    if normalized:
        n = len(nodes)
        if n > 2:
            scale = 2.0 / ((n - 1) * (n - 2)) if not G.is_directed() else 1.0 / ((n - 1) * (n - 2))
            betweenness = {v: b * scale for v, b in betweenness.items()}

    return betweenness


def closeness_centrality(G, u=None, distance: str | None = None, wf_improved: bool = True) -> dict:
    """
    Compute closeness centrality for all nodes (or a single node *u*).

    ``closeness(v) = (n - 1) / sum_distances(v)`` (normalized by reachable nodes).

    Returns
    -------
    dict or float
        When *u* is given, returns a single float. Otherwise a dict.
    """
    from grapx.algorithms.shortest_paths import NetworkXNoPath, shortest_path_length

    def _closeness(G, node):
        n = len(G)
        total = 0.0
        reachable = 0
        for target in G.nodes():
            if target == node:
                continue
            try:
                d = shortest_path_length(G, source=node, target=target)
                total += d
                reachable += 1
            except NetworkXNoPath:
                pass
        if reachable == 0:
            return 0.0
        if wf_improved and reachable < n - 1:
            # Wasserman-Faust improved formula
            return (reachable / (n - 1)) * (reachable / total)
        return reachable / total

    if u is not None:
        return _closeness(G, u)

    return {v: _closeness(G, v) for v in G.nodes()}


def in_degree_centrality(G) -> dict:
    """In-degree centrality for directed graph nodes."""
    n = len(G)
    if n <= 1:
        return {v: 0.0 for v in G}
    norm = n - 1
    return {v: G.in_degree[v] / norm for v in G.nodes()}


def out_degree_centrality(G) -> dict:
    """Out-degree centrality for directed graph nodes."""
    n = len(G)
    if n <= 1:
        return {v: 0.0 for v in G}
    norm = n - 1
    return {v: G.out_degree[v] / norm for v in G.nodes()}


__all__ = [
    "degree_centrality",
    "betweenness_centrality",
    "closeness_centrality",
    "in_degree_centrality",
    "out_degree_centrality",
]

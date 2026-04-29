"""
grapx.algorithms.link_analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Link-analysis algorithms: PageRank, HITS.
PageRank runs in Rust with Rayon parallelism — typically 50–120× faster than
pure-Python implementations.
"""

from __future__ import annotations

from grapx._validation import validate_pagerank_params

try:
    from grapx._core import pagerank_digraph as _pr_digraph
    from grapx._core import pagerank_graph as _pr_graph
except ImportError as _err:  # pragma: no cover
    raise ImportError(
        "grapx requires the compiled Rust extension. Run: maturin develop"
    ) from _err


def pagerank(
    G,
    alpha: float = 0.85,
    personalization=None,
    max_iter: int = 100,
    tol: float = 1.0e-6,
    nstart=None,
    weight: str | None = "weight",
    dangling=None,
) -> dict:
    """
    Compute the PageRank of each node in *G*.

    The computation runs entirely in Rust using Rayon parallel iteration.

    Parameters
    ----------
    G : Graph or DiGraph
    alpha : float
        Damping factor (default 0.85).  Must be in [0, 1].
    max_iter : int
        Maximum power-iteration steps (default 100).
    tol : float
        Convergence tolerance (default 1e-6).
    weight : str or None
        Edge attribute used as weight (default ``"weight"``). When an edge
        has no such attribute, weight 1.0 is assumed.

    Returns
    -------
    dict
        Mapping ``{node: pagerank_score}`` — scores sum to 1.

    Notes
    -----
    ``personalization``, ``nstart``, and ``dangling`` parameters are accepted
    for API compatibility but currently ignored.  Full support is planned for
    v0.2.
    """
    params = validate_pagerank_params(
        alpha=alpha, max_iter=max_iter, tol=tol, weight=weight
    )

    if len(G) == 0:
        return {}

    is_digraph = G.is_directed()
    rust_fn = _pr_digraph if is_digraph else _pr_graph

    raw: list = rust_fn(G._rust, params.alpha, params.max_iter, params.tol)

    return {
        G._idx_to_node[idx]: score
        for idx, score in raw
        if idx < len(G._idx_to_node) and G._idx_to_node[idx] is not None
        and G._idx_to_node[idx] in G._node
    }


def hits(G, max_iter: int = 100, tol: float = 1.0e-8, nstart=None, normalized: bool = True):
    """
    HITS algorithm — returns (hub_scores, authority_scores).

    Implemented in pure Python (Rust acceleration in v0.2).
    """
    if len(G) == 0:
        return {}, {}

    nodes = list(G.nodes())
    n = len(nodes)

    # Initialize
    hub = {v: 1.0 / n for v in nodes}
    auth = {v: 1.0 / n for v in nodes}

    for _ in range(max_iter):
        last_auth = dict(auth)
        dict(hub)

        # Update authority: auth[v] = sum of hub[u] for u → v
        for v in nodes:
            auth[v] = sum(hub[u] for u in G.predecessors(v)) if G.is_directed() else sum(hub[u] for u in G.neighbors(v))

        # Update hub: hub[u] = sum of auth[v] for u → v
        for u in nodes:
            hub[u] = sum(auth[v] for v in (G.successors(u) if G.is_directed() else G.neighbors(u)))

        # Normalize
        auth_sum = sum(auth.values()) or 1.0
        hub_sum = sum(hub.values()) or 1.0
        auth = {v: s / auth_sum for v, s in auth.items()}
        hub = {v: s / hub_sum for v, s in hub.items()}

        # Convergence
        err = sum(abs(auth[v] - last_auth[v]) for v in nodes)
        if err < tol:
            break

    if normalized:
        auth_norm = sum(auth.values()) or 1.0
        hub_norm = sum(hub.values()) or 1.0
        auth = {v: s / auth_norm for v, s in auth.items()}
        hub = {v: s / hub_norm for v, s in hub.items()}

    return hub, auth


__all__ = ["pagerank", "hits"]

"""
grapx.classes.digraph
~~~~~~~~~~~~~~~~~~~~~~
Directed graph class with Rust-accelerated algorithms.
"""

from __future__ import annotations

from typing import Generator, Hashable

try:
    from grapx._core import RustDiGraph as _RustDiGraph
except ImportError as _err:  # pragma: no cover
    raise ImportError(
        "grapx requires the compiled Rust extension. Run: maturin develop"
    ) from _err

from grapx.classes.graph import Graph, _AdjView, _EdgeView


class DiGraph(Graph):
    """
    Directed graph supporting arbitrary hashable nodes.

    Edges have a direction: (u → v) ≠ (v → u).

    Example
    -------
    >>> import grapx as gx
    >>> G = gx.DiGraph()
    >>> G.add_edge("Alice", "Bob")
    >>> G.add_edge("Bob", "Carol")
    >>> G.has_edge("Alice", "Bob")
    True
    >>> G.has_edge("Bob", "Alice")
    False
    """

    def __init__(self, incoming_graph_data=None, **attr):
        # Bypass Graph.__init__ to use RustDiGraph instead of RustGraph
        self._rust = _RustDiGraph()
        self._node_to_idx: dict = {}
        self._idx_to_node: list = []
        self._node: dict = {}
        self._edge_data: dict = {}
        self.graph: dict = {}
        self.graph.update(attr)

        if incoming_graph_data is not None:
            self._init_from_data(incoming_graph_data)

    # Directed edges are keyed by ordered tuple (u, v) ≠ (v, u)
    def _edge_key(self, u, v):
        return (u, v)

    def add_edge(self, u_of_edge: Hashable, v_of_edge: Hashable, **attr) -> None:
        u, v = u_of_edge, v_of_edge
        u_idx = self._get_or_add_idx(u)
        v_idx = self._get_or_add_idx(v)
        weight = float(attr.get("weight", 1.0))
        self._rust.add_edge(u_idx, v_idx, weight)
        self._edge_data[(u, v)] = dict(attr)

    def remove_edge(self, u: Hashable, v: Hashable) -> None:
        if (u, v) not in self._edge_data:
            from grapx.exception import GrapxError
            raise GrapxError(f"Edge ({u!r}, {v!r}) not in graph")
        del self._edge_data[(u, v)]
        self._rust.remove_edge(self._node_to_idx[u], self._node_to_idx[v])

    def has_edge(self, u: Hashable, v: Hashable) -> bool:
        return (u, v) in self._edge_data

    def get_edge_data(self, u, v, default=None):
        return self._edge_data.get((u, v), default)

    # ─── Directed traversal ─────────────────────────────────────────────────

    def successors(self, n: Hashable) -> Generator:
        self._require_node(n)
        idx = self._node_to_idx[n]
        for i in self._rust.successors(idx):
            node = self._idx_to_node[i] if i < len(self._idx_to_node) else None
            if node is not None and node in self._node:
                yield node

    def predecessors(self, n: Hashable) -> Generator:
        self._require_node(n)
        idx = self._node_to_idx[n]
        for i in self._rust.predecessors(idx):
            node = self._idx_to_node[i] if i < len(self._idx_to_node) else None
            if node is not None and node in self._node:
                yield node

    # In a DiGraph, neighbors == successors (networkx convention)
    def neighbors(self, n: Hashable) -> Generator:
        return self.successors(n)

    # ─── Degree views ────────────────────────────────────────────────────────

    @property
    def in_degree(self) -> _InDegreeView:
        return _InDegreeView(self)

    @property
    def out_degree(self) -> _OutDegreeView:
        return _OutDegreeView(self)

    @property
    def degree(self) -> _DiDegreeView:
        return _DiDegreeView(self)

    # ─── Edge iteration ──────────────────────────────────────────────────────

    @property
    def edges(self) -> _DiEdgeView:
        return _DiEdgeView(self)

    @property
    def out_edges(self) -> _DiEdgeView:
        return self.edges

    # ─── Adjacency ───────────────────────────────────────────────────────────

    @property
    def pred(self) -> _PredView:
        return _PredView(self)

    @property
    def succ(self) -> _AdjView:
        return _AdjView(self)

    def __getitem__(self, n):
        return self.adj[n]

    # ─── Conversion helpers ──────────────────────────────────────────────────

    def reverse(self, copy: bool = True) -> DiGraph:
        R = DiGraph()
        R.add_nodes_from(self.nodes(data=True))
        R.add_edges_from((v, u, dict(d)) for u, v, d in self.edges(data=True))
        return R

    def to_undirected(self, reciprocal: bool = False) -> Graph:
        from grapx.classes.graph import Graph as _Graph
        G = _Graph()
        G.add_nodes_from(self.nodes(data=True))
        if reciprocal:
            G.add_edges_from(
                (u, v, d)
                for u, v, d in self.edges(data=True)
                if self.has_edge(v, u)
            )
        else:
            G.add_edges_from(self.edges(data=True))
        return G

    def to_directed(self) -> DiGraph:
        return self.copy()

    def is_directed(self) -> bool:
        return True

    def is_multigraph(self) -> bool:
        return False

    # ─── Adjacency view for directed ─────────────────────────────────────────

    @property
    def adj(self):  # type: ignore[override]
        return _DiAdjView(self)


class _DiEdgeView(_EdgeView):
    """Edge view for directed graphs — respects edge direction."""

    def __iter__(self):
        return iter(self._G._edge_data.keys())

    def __call__(self, data=False, default=None, nbunch=None):
        for (u, v), attrs in self._G._edge_data.items():
            if nbunch is not None and u not in nbunch:
                continue
            if data is True:
                yield (u, v, dict(attrs))
            elif data:
                yield (u, v, attrs.get(data, default))
            else:
                yield (u, v)

    def __getitem__(self, edge):
        u, v = edge
        if (u, v) not in self._G._edge_data:
            raise KeyError(f"Edge ({u!r}, {v!r}) not in graph")
        return self._G._edge_data[(u, v)]


class _DiAdjView:
    """Adjacency view for directed graph — follows outgoing edges."""

    __slots__ = ("_G",)

    def __init__(self, G):
        self._G = G

    def __getitem__(self, n):
        if n not in self._G._node:
            from grapx.exception import NodeNotFound
            raise NodeNotFound(n)
        idx = self._G._node_to_idx[n]
        result = {}
        for ni in self._G._rust.successors(idx):
            neighbor = (
                self._G._idx_to_node[ni]
                if ni < len(self._G._idx_to_node)
                else None
            )
            if neighbor is not None and neighbor in self._G._node:
                result[neighbor] = self._G._edge_data.get((n, neighbor), {})
        return result

    def __iter__(self):
        return iter(self._G._node)

    def __len__(self):
        return len(self._G._node)

    def __contains__(self, n):
        return n in self._G._node

    def items(self):
        for n in self._G._node:
            yield (n, self[n])


class _PredView:
    """Predecessor adjacency view for directed graph."""

    __slots__ = ("_G",)

    def __init__(self, G):
        self._G = G

    def __getitem__(self, n):
        if n not in self._G._node:
            from grapx.exception import NodeNotFound
            raise NodeNotFound(n)
        idx = self._G._node_to_idx[n]
        result = {}
        for ni in self._G._rust.predecessors(idx):
            neighbor = (
                self._G._idx_to_node[ni]
                if ni < len(self._G._idx_to_node)
                else None
            )
            if neighbor is not None and neighbor in self._G._node:
                result[neighbor] = self._G._edge_data.get((neighbor, n), {})
        return result

    def __iter__(self):
        return iter(self._G._node)


class _InDegreeView:
    __slots__ = ("_G",)

    def __init__(self, G):
        self._G = G

    def __iter__(self):
        for n, idx in self._G._node_to_idx.items():
            if n in self._G._node:
                yield (n, self._G._rust.in_degree(idx))

    def __getitem__(self, n):
        return self._G._rust.in_degree(self._G._node_to_idx[n])

    def __call__(self, nbunch=None, weight=None):
        if nbunch is None:
            return iter(self)
        if nbunch in self._G._node:
            return self[nbunch]
        return ((n, self[n]) for n in nbunch if n in self._G._node)


class _OutDegreeView:
    __slots__ = ("_G",)

    def __init__(self, G):
        self._G = G

    def __iter__(self):
        for n, idx in self._G._node_to_idx.items():
            if n in self._G._node:
                yield (n, self._G._rust.out_degree(idx))

    def __getitem__(self, n):
        return self._G._rust.out_degree(self._G._node_to_idx[n])

    def __call__(self, nbunch=None, weight=None):
        if nbunch is None:
            return iter(self)
        if nbunch in self._G._node:
            return self[nbunch]
        return ((n, self[n]) for n in nbunch if n in self._G._node)


class _DiDegreeView:
    __slots__ = ("_G",)

    def __init__(self, G):
        self._G = G

    def __iter__(self):
        for n, idx in self._G._node_to_idx.items():
            if n in self._G._node:
                yield (
                    n,
                    self._G._rust.in_degree(idx) + self._G._rust.out_degree(idx),
                )

    def __getitem__(self, n):
        idx = self._G._node_to_idx[n]
        return self._G._rust.in_degree(idx) + self._G._rust.out_degree(idx)

    def __call__(self, nbunch=None, weight=None):
        if nbunch is None:
            return iter(self)
        if nbunch in self._G._node:
            return self[nbunch]
        return ((n, self[n]) for n in nbunch if n in self._G._node)

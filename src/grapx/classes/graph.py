"""
grapx.classes.graph
~~~~~~~~~~~~~~~~~~~~
Undirected graph class with Rust-accelerated algorithms.
"""

from __future__ import annotations

import contextlib
from typing import Any, Generator, Hashable, Iterator

try:
    from grapx._core import RustGraph as _RustGraph
except ImportError as _err:  # pragma: no cover
    raise ImportError(
        "grapx requires the compiled Rust extension. Run: maturin develop"
    ) from _err


class Graph:
    """
    Undirected graph supporting arbitrary hashable nodes.

    Node and edge attributes are stored in plain Python dicts.
    The graph structure and all heavy algorithms (BFS, DFS, Dijkstra, PageRank,
    connected components, centrality) execute inside the Rust core.

    Example
    -------
    >>> import grapx as gx
    >>> G = gx.Graph()
    >>> G.add_edge("Alice", "Bob", weight=1.5)
    >>> G.add_edge("Bob", "Carol", weight=2.0)
    >>> list(gx.connected_components(G))
    [{'Alice', 'Bob', 'Carol'}]
    """

    def __init__(self, incoming_graph_data=None, **attr):
        self._rust = _RustGraph()

        # Bidirectional node ↔ Rust-index mapping
        self._node_to_idx: dict[Any, int] = {}
        self._idx_to_node: list = []  # index → Python node (None if deleted)

        # Node attributes: {node: {attr_name: attr_value}}
        self._node: dict[Any, dict] = {}

        # Edge attributes: {frozenset({u, v}): {attr_name: attr_value}}
        self._edge_data: dict[Any, dict] = {}

        # Graph-level attributes
        self.graph: dict = {}
        self.graph.update(attr)

        if incoming_graph_data is not None:
            self._init_from_data(incoming_graph_data)

    # ─── Internal helpers ────────────────────────────────────────────────────

    def _get_or_add_idx(self, node: Hashable) -> int:
        """Return the Rust index for a node, creating it if needed."""
        if node not in self._node_to_idx:
            idx = int(self._rust.add_node())
            self._node_to_idx[node] = idx
            # Extend list to accommodate this index
            while len(self._idx_to_node) <= idx:
                self._idx_to_node.append(None)
            self._idx_to_node[idx] = node
            self._node[node] = {}
        return self._node_to_idx[node]

    def _edge_key(self, u, v):
        return frozenset((u, v))

    def _require_node(self, n):
        if n not in self._node:
            from grapx.exception import NodeNotFound
            raise NodeNotFound(f"Node {n!r} not found in graph")

    # ─── Node operations ────────────────────────────────────────────────────

    def add_node(self, node_for_adding: Hashable, **attr) -> None:
        self._get_or_add_idx(node_for_adding)
        self._node[node_for_adding].update(attr)

    def add_nodes_from(self, nodes_for_adding, **attr) -> None:
        for n in nodes_for_adding:
            if isinstance(n, tuple) and len(n) == 2 and isinstance(n[1], dict):
                node, node_attr = n
                self._get_or_add_idx(node)
                self._node[node].update(attr)
                self._node[node].update(node_attr)
            else:
                self._get_or_add_idx(n)
                self._node[n].update(attr)

    def remove_node(self, n: Hashable) -> None:
        if n not in self._node:
            from grapx.exception import NodeNotFound
            raise NodeNotFound(f"Node {n!r} not in graph")

        idx = self._node_to_idx[n]

        # Remove all edges incident to this node from Python data
        to_delete = [k for k in self._edge_data if n in k]
        for k in to_delete:
            del self._edge_data[k]

        # Remove from Rust
        self._rust.remove_node(idx)

        # Remove from Python mappings
        self._idx_to_node[idx] = None
        del self._node_to_idx[n]
        del self._node[n]

    def has_node(self, n: Hashable) -> bool:
        return n in self._node

    def __contains__(self, n: Hashable) -> bool:
        return n in self._node

    def __iter__(self) -> Iterator:
        return iter(self._node)

    def __len__(self) -> int:
        return len(self._node)

    @property
    def nodes(self) -> _NodeView:
        return _NodeView(self)

    def number_of_nodes(self) -> int:
        return len(self._node)

    def order(self) -> int:
        return self.number_of_nodes()

    # ─── Edge operations ────────────────────────────────────────────────────

    def add_edge(self, u_of_edge: Hashable, v_of_edge: Hashable, **attr) -> None:
        u, v = u_of_edge, v_of_edge
        u_idx = self._get_or_add_idx(u)
        v_idx = self._get_or_add_idx(v)

        weight = float(attr.get("weight", 1.0))
        self._rust.add_edge(u_idx, v_idx, weight)
        self._edge_data[self._edge_key(u, v)] = dict(attr)

    def add_edges_from(self, ebunch_to_add, **attr) -> None:
        for e in ebunch_to_add:
            if len(e) == 2:
                u, v = e
                edge_attr = dict(attr)
            elif len(e) == 3:
                u, v, d = e
                edge_attr = {**attr, **(d if isinstance(d, dict) else {})}
            else:
                raise ValueError(f"Edge tuple must have 2 or 3 elements, got {len(e)}")
            self.add_edge(u, v, **edge_attr)

    def remove_edge(self, u: Hashable, v: Hashable) -> None:
        if not self.has_edge(u, v):
            from grapx.exception import GrapxError
            raise GrapxError(f"Edge ({u!r}, {v!r}) not in graph")
        key = self._edge_key(u, v)
        self._edge_data.pop(key, None)
        u_idx = self._node_to_idx[u]
        v_idx = self._node_to_idx[v]
        self._rust.remove_edge(u_idx, v_idx)

    def remove_edges_from(self, ebunch) -> None:
        for e in ebunch:
            with contextlib.suppress(Exception):
                self.remove_edge(*e[:2])

    def has_edge(self, u: Hashable, v: Hashable) -> bool:
        return self._edge_key(u, v) in self._edge_data

    def get_edge_data(self, u: Hashable, v: Hashable, default=None):
        key = self._edge_key(u, v)
        return self._edge_data.get(key, default)

    def number_of_edges(self, u=None, v=None) -> int:
        if u is None:
            return len(self._edge_data)
        return 1 if self.has_edge(u, v) else 0

    def size(self, weight=None) -> int | float:
        if weight is None:
            return len(self._edge_data)
        return sum(
            d.get(weight, 1) for d in self._edge_data.values()
        )

    @property
    def edges(self) -> _EdgeView:
        return _EdgeView(self)

    # ─── Adjacency & neighbors ──────────────────────────────────────────────

    def neighbors(self, n: Hashable) -> Generator:
        self._require_node(n)
        idx = self._node_to_idx[n]
        for i in self._rust.neighbors(idx):
            node = self._idx_to_node[i] if i < len(self._idx_to_node) else None
            if node is not None and node in self._node:
                yield node

    @property
    def degree(self) -> _DegreeView:
        return _DegreeView(self)

    @property
    def adj(self) -> _AdjView:
        return _AdjView(self)

    def __getitem__(self, n):
        return self.adj[n]

    # ─── Graph-level helpers ────────────────────────────────────────────────

    def copy(self) -> Graph:
        G = self.__class__()
        G.add_nodes_from(self.nodes(data=True))
        G.add_edges_from(self.edges(data=True))
        G.graph.update(self.graph)
        return G

    def subgraph(self, nodes) -> Graph:
        nodes_set = set(nodes)
        G = self.__class__()
        G.add_nodes_from((n, d) for n, d in self.nodes(data=True) if n in nodes_set)
        G.add_edges_from(
            (u, v, d)
            for u, v, d in self.edges(data=True)
            if u in nodes_set and v in nodes_set
        )
        return G

    def to_directed(self) -> DiGraph:  # noqa: F821
        from grapx.classes.digraph import DiGraph
        G = DiGraph()
        G.add_nodes_from(self.nodes(data=True))
        G.add_edges_from(self.edges(data=True))
        return G

    def to_undirected(self) -> Graph:
        return self.copy()

    def is_directed(self) -> bool:
        return False

    def is_multigraph(self) -> bool:
        return False

    def add_star(self, nodes_for_adding, **attr) -> None:
        nlist = list(nodes_for_adding)
        if not nlist:
            return
        v = nlist[0]
        self.add_node(v)
        self.add_edges_from((v, u) for u in nlist[1:])
        for u in nlist[1:]:
            self._edge_data[self._edge_key(v, u)].update(attr)

    def add_path(self, nodes_for_adding, **attr) -> None:
        nlist = list(nodes_for_adding)
        self.add_edges_from(zip(nlist[:-1], nlist[1:]), **attr)

    def add_cycle(self, nodes_for_adding, **attr) -> None:
        nlist = list(nodes_for_adding)
        if nlist:
            self.add_path(nlist + [nlist[0]], **attr)

    def clear(self) -> None:
        self._rust = _RustGraph()
        self._node_to_idx.clear()
        self._idx_to_node.clear()
        self._node.clear()
        self._edge_data.clear()
        self.graph.clear()

    def update(self, edges=None, nodes=None) -> None:
        if edges is not None:
            if hasattr(edges, "nodes"):
                self.add_nodes_from(edges.nodes(data=True))
                self.add_edges_from(edges.edges(data=True))
            else:
                self.add_edges_from(edges)
        if nodes is not None:
            self.add_nodes_from(nodes)

    def nbunch_iter(self, nbunch=None):
        if nbunch is None:
            return iter(self._node)
        if nbunch in self._node:
            return iter([nbunch])
        return (n for n in nbunch if n in self._node)

    def _init_from_data(self, data) -> None:
        if hasattr(data, "edges") and hasattr(data, "nodes"):
            self.add_nodes_from(n for n in data.nodes() if n not in self)
            self.add_edges_from(data.edges(data=True))
        elif isinstance(data, dict):
            for u, neighbors in data.items():
                for v, attrs in neighbors.items():
                    self.add_edge(u, v, **(attrs if isinstance(attrs, dict) else {}))

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__} with "
            f"{self.number_of_nodes()} nodes and "
            f"{self.number_of_edges()} edges"
        )

    def __str__(self) -> str:
        return self.__repr__()


# ─── View classes ────────────────────────────────────────────────────────────


class _NodeView:
    __slots__ = ("_G",)

    def __init__(self, G: Graph):
        self._G = G

    def __iter__(self) -> Iterator:
        return iter(self._G._node)

    def __len__(self) -> int:
        return len(self._G._node)

    def __contains__(self, n) -> bool:
        return n in self._G._node

    def __call__(self, data=False, default=None):
        if not data:
            return iter(self._G._node)
        if data is True:
            return ((n, dict(attrs)) for n, attrs in self._G._node.items())
        # data is a string: return specific attribute
        return (
            (n, attrs.get(data, default)) for n, attrs in self._G._node.items()
        )

    def __getitem__(self, n):
        return self._G._node[n]

    def __setitem__(self, n, attr):
        if n not in self._G._node:
            self._G.add_node(n)
        self._G._node[n].update(attr)

    def data(self, data=True, default=None):
        return self(data=data, default=default)

    def items(self):
        return self._G._node.items()

    def keys(self):
        return self._G._node.keys()


class _EdgeView:
    __slots__ = ("_G",)

    def __init__(self, G: Graph):
        self._G = G

    def __iter__(self) -> Iterator[tuple]:
        for key in self._G._edge_data:
            nodes = list(key)
            if len(nodes) == 2:
                yield (nodes[0], nodes[1])
            else:
                yield (nodes[0], nodes[0])

    def __len__(self) -> int:
        return len(self._G._edge_data)

    def __contains__(self, edge) -> bool:
        u, v = edge[0], edge[1]
        return self._G.has_edge(u, v)

    def __call__(self, data=False, default=None, nbunch=None):
        for key, attrs in self._G._edge_data.items():
            nodes = list(key)
            u = nodes[0] if len(nodes) >= 1 else None
            v = nodes[1] if len(nodes) >= 2 else nodes[0]

            if nbunch is not None and u not in nbunch and v not in nbunch:
                continue

            if data is True:
                yield (u, v, dict(attrs))
            elif data:
                yield (u, v, attrs.get(data, default))
            else:
                yield (u, v)

    def __getitem__(self, edge):
        u, v = edge
        key = self._G._edge_key(u, v)
        if key not in self._G._edge_data:
            raise KeyError(f"Edge ({u!r}, {v!r}) not in graph")
        return self._G._edge_data[key]

    def data(self, data=True, default=None):
        return self(data=data, default=default)


class _DegreeView:
    __slots__ = ("_G",)

    def __init__(self, G: Graph):
        self._G = G

    def __iter__(self):
        for n, idx in self._G._node_to_idx.items():
            if n in self._G._node:
                yield (n, self._G._rust.degree(idx))

    def __len__(self) -> int:
        return len(self._G._node)

    def __getitem__(self, n):
        if n not in self._G._node:
            from grapx.exception import NodeNotFound
            raise NodeNotFound(n)
        return self._G._rust.degree(self._G._node_to_idx[n])

    def __call__(self, nbunch=None, weight=None):
        if nbunch is None:
            return iter(self)
        if nbunch in self._G._node:
            return self[nbunch]
        return ((n, self[n]) for n in nbunch if n in self._G._node)


class _AdjView:
    __slots__ = ("_G",)

    def __init__(self, G: Graph):
        self._G = G

    def __getitem__(self, n):
        if n not in self._G._node:
            from grapx.exception import NodeNotFound
            raise NodeNotFound(n)
        idx = self._G._node_to_idx[n]
        result = {}
        for ni in self._G._rust.neighbors(idx):
            neighbor = (
                self._G._idx_to_node[ni]
                if ni < len(self._G._idx_to_node)
                else None
            )
            if neighbor is not None and neighbor in self._G._node:
                key = self._G._edge_key(n, neighbor)
                result[neighbor] = self._G._edge_data.get(key, {})
        return result

    def __iter__(self):
        return iter(self._G._node)

    def __len__(self) -> int:
        return len(self._G._node)

    def __contains__(self, n) -> bool:
        return n in self._G._node

    def items(self):
        for n in self._G._node:
            yield (n, self[n])


# Import needed for to_directed()

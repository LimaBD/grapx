# grapx API Reference

Complete reference for every public class, method, and function in grapx.

> **Quick navigation**
> [Graph Classes](#graph-classes) · [Algorithms](#algorithms) · [Generators](#generators) · [I/O](#io) · [Exceptions](#exceptions)

---

## Graph Classes

### `gx.Graph`

An undirected, simple graph. Nodes can be any hashable Python object. Edge attributes
(weights, labels, metadata) are stored in plain Python dicts.

The entire graph topology lives in a Rust `StableGraph`, so BFS, Dijkstra, PageRank,
and component algorithms all run in compiled code — no Python loops in the hot path.

```python
import grapx as gx

G = gx.Graph()
G = gx.Graph({"A": ["B", "C"], "B": ["C"]})   # from adjacency dict
```

#### Constructor

```python
Graph(incoming_graph_data=None, **attr)
```

| Parameter | Type | Description |
|---|---|---|
| `incoming_graph_data` | dict or None | Optional adjacency dict `{node: [neighbors]}` to populate from |
| `**attr` | any | Graph-level attributes stored in `G.graph` dict |

---

#### Adding Nodes

```python
G.add_node(node_for_adding, **attr)
```
Add a single node. Extra keyword arguments become node attributes.

```python
G.add_node(1)
G.add_node("Alice", age=30, team="engineering")
G.add_node((0, 0), color="red")   # tuples are valid node IDs
```

---

```python
G.add_nodes_from(nodes_for_adding, **attr)
```
Add multiple nodes at once. Each element can be a bare node or a `(node, attr_dict)` tuple.
Extra `**attr` are applied to **all** nodes in the iterable.

```python
G.add_nodes_from([1, 2, 3])
G.add_nodes_from([(1, {"color": "red"}), (2, {"color": "blue"})])
G.add_nodes_from(range(100), weight=0.0)   # bulk default attrs
```

---

#### Removing Nodes

```python
G.remove_node(n)
```
Remove node `n` and all edges incident to it. Raises `NodeNotFound` if not present.

```python
G.remove_nodes_from(nodes)
```
Remove all nodes in the iterable. Silently skips nodes not in the graph.

---

#### Adding Edges

```python
G.add_edge(u_of_edge, v_of_edge, **attr)
```
Add an undirected edge between `u` and `v`. Both nodes are created automatically if absent.
Extra keyword arguments become edge attributes. For a `Graph`, adding the same edge twice
**updates** the attributes rather than creating a duplicate.

```python
G.add_edge(1, 2)
G.add_edge("Alice", "Bob", weight=1.5, relation="colleague")
G.add_edge(1, 2, weight=3.0)   # updates weight if edge already exists
```

---

```python
G.add_edges_from(ebunch_to_add, **attr)
```
Add multiple edges at once. Each element can be a `(u, v)` tuple or a
`(u, v, attr_dict)` triple. Extra `**attr` are applied to all edges.

```python
G.add_edges_from([(1, 2), (2, 3), (3, 1)])
G.add_edges_from([(1, 2, {"weight": 1.0}), (2, 3, {"weight": 2.0})])
G.add_edges_from(path_edges, color="blue")   # bulk default attrs
```

---

#### Removing Edges

```python
G.remove_edge(u, v)
```
Remove the edge between `u` and `v`. Raises `KeyError` if the edge does not exist.

```python
G.remove_edges_from(ebunch)
```
Remove all edges in the iterable. Silently skips missing edges.

---

#### Querying

```python
G.has_node(n)         # → bool
G.has_edge(u, v)      # → bool
n in G                # same as has_node(n)
len(G)                # number of nodes
G.number_of_nodes()   # same as len(G)
G.order()             # alias for number_of_nodes()
G.number_of_edges()   # total edge count
G.size(weight=None)   # sum of edge weights (or edge count when weight=None)
```

```python
G.get_edge_data(u, v, default=None)
```
Return the attribute dict for edge `(u, v)`, or `default` if the edge does not exist.

```python
G.degree[n]             # degree of node n
G.nodes[n]              # attribute dict for node n (read/write)
G.nodes(data=True)      # iterator over (node, attr_dict)
G.edges(data=False)     # iterator over (u, v) or (u, v, attr_dict)
G.neighbors(n)          # iterator of neighbour nodes
G.adj[n]                # dict-like {neighbour: edge_attr_dict}
```

---

#### Graph-level Operations

```python
G.copy()          # → Graph — deep copy
G.subgraph(nodes) # → Graph — induced subgraph (read-only view)
G.to_directed()   # → DiGraph
G.to_undirected() # → Graph (copy)
G.clear()         # remove all nodes and edges

G.add_star([0, 1, 2, 3])   # hub at node 0, spokes to 1-3
G.add_path([1, 2, 3, 4])   # chain 1-2-3-4
G.add_cycle([1, 2, 3, 4])  # cycle 1-2-3-4-1

G.update(edges=other_graph)  # merge another graph or edge list
```

---

#### Special attributes

```python
G.graph           # dict — graph-level attributes set at construction time
G.is_directed()   # → False
G.is_multigraph() # → False
```

---

### `gx.DiGraph`

A directed graph. Inherits all `Graph` methods and adds directed-specific properties.

```python
G = gx.DiGraph()
G.add_edge("Alice", "Bob")   # Alice → Bob
G.has_edge("Bob", "Alice")   # False — direction matters
```

#### Directed-specific methods

```python
G.successors(n)    # iterator of nodes that n points *to*
G.predecessors(n)  # iterator of nodes that point *to* n
G.neighbors(n)     # alias for successors(n)

G.reverse(copy=True)               # → DiGraph — all edges reversed
G.to_undirected(reciprocal=False)  # → Graph
```

`reciprocal=True` keeps only edges where both `(u, v)` and `(v, u)` exist.

#### Directed-specific properties

```python
G.in_degree[n]    # number of incoming edges to n
G.out_degree[n]   # number of outgoing edges from n
G.degree[n]       # in_degree[n] + out_degree[n]
G.pred[n]         # dict-like {predecessor: edge_attr_dict}
G.succ[n]         # dict-like {successor: edge_attr_dict}
G.adj[n]          # alias for succ[n]
G.out_edges       # alias for edges
```

#### Example — directed degree analysis

```python
import grapx as gx

G = gx.DiGraph()
G.add_edges_from([
    ("A", "B"), ("A", "C"), ("B", "C"), ("C", "A"),
])

for node in G.nodes():
    print(f"{node}: in={G.in_degree[node]}  out={G.out_degree[node]}")
# A: in=1  out=2
# B: in=1  out=1
# C: in=2  out=1
```

---

### `gx.MultiGraph` / `gx.MultiDiGraph`

Multigraph classes (parallel edges between the same pair of nodes). These are available in
v0.1 as aliases for `Graph` and `DiGraph` respectively — full parallel-edge tracking
is planned for v0.2.

```python
G = gx.MultiGraph()
G.is_multigraph()   # → True
```

---

## Algorithms

All algorithm functions accept either a `Graph` or `DiGraph` unless noted otherwise.
They are imported at the top level: `import grapx as gx`.

---

### PageRank

```python
gx.pagerank(
    G,
    alpha=0.85,
    personalization=None,
    max_iter=100,
    tol=1e-6,
    nstart=None,
    weight="weight",
    dangling=None,
) -> dict
```

Compute the PageRank centrality of every node. The entire computation runs in Rust with
Rayon thread-level parallelism — consistently 80–120× faster than pure-Python implementations.

| Parameter | Default | Description |
|---|---|---|
| `G` | — | Undirected `Graph` or directed `DiGraph` |
| `alpha` | `0.85` | Damping factor — probability of following an edge. Must be in `[0, 1]`. |
| `max_iter` | `100` | Maximum power-iteration rounds |
| `tol` | `1e-6` | L1 convergence tolerance |
| `weight` | `"weight"` | Edge attribute used as edge weight. Pass `None` for unweighted (uniform 1.0) |
| `personalization` | `None` | *v0.2* — accepted for API compatibility, currently ignored |
| `nstart` | `None` | *v0.2* — accepted for API compatibility, currently ignored |
| `dangling` | `None` | *v0.2* — accepted for API compatibility, currently ignored |

**Returns:** `dict` mapping each node to its PageRank score. Scores sum to 1.0.

**Raises:** `pydantic.ValidationError` if `alpha` is outside `[0, 1]` or `max_iter < 1`.

```python
import grapx as gx

G = gx.DiGraph()
G.add_edges_from([
    ("home", "about"),
    ("home", "blog"),
    ("blog", "home"),
    ("blog", "post1"),
    ("post1", "home"),
])

pr = gx.pagerank(G)
# Sort by importance
top = sorted(pr, key=pr.get, reverse=True)
print(top)  # ['home', 'blog', 'post1', 'about']

# Custom damping — lower alpha = more uniform scores
pr_low = gx.pagerank(G, alpha=0.5)

# Weighted edges — pass attribute name
G.add_edge("home", "contact", weight=5.0)
pr_weighted = gx.pagerank(G, weight="weight")
```

---

### HITS (Hyperlink-Induced Topic Search)

```python
gx.hits(
    G,
    max_iter=100,
    tol=1e-8,
    nstart=None,
    normalized=True,
) -> tuple[dict, dict]
```

Compute hub and authority scores for every node.
- **Authority score:** how much valuable information a node contains (pointed to by good hubs)
- **Hub score:** how well a node points to authoritative sources

**Returns:** `(hub_scores, authority_scores)` — each is a `dict` mapping node → float.

```python
hub, auth = gx.hits(G)
best_authorities = sorted(auth, key=auth.get, reverse=True)[:5]
best_hubs = sorted(hub, key=hub.get, reverse=True)[:5]
```

---

### Shortest Paths

#### `gx.shortest_path`

```python
gx.shortest_path(
    G,
    source,
    target,
    weight=None,
    method=None,
) -> list
```

Return an ordered list of nodes forming the shortest path from `source` to `target`.
Uses Dijkstra's algorithm (implemented in Rust) for weighted graphs and BFS for unweighted.

| Parameter | Default | Description |
|---|---|---|
| `G` | — | Graph or DiGraph |
| `source` | — | Starting node (must be in G) |
| `target` | — | Destination node (must be in G) |
| `weight` | `None` | Edge attribute to use as distance. `None` = hop count (BFS) |
| `method` | `None` | Algorithm hint. `"dijkstra"` is the only supported value in v0.1 |

**Returns:** `list` of nodes, starting with `source` and ending with `target`.

**Raises:**
- `NodeNotFound` — if `source` or `target` is not in the graph
- `NetworkXNoPath` — if no path exists between the two nodes

```python
import grapx as gx

G = gx.Graph()
G.add_edge("A", "B", weight=1.0)
G.add_edge("B", "C", weight=2.0)
G.add_edge("A", "C", weight=10.0)

# Hop-count shortest path (BFS)
print(gx.shortest_path(G, "A", "C"))           # ["A", "C"]

# Weight-aware shortest path (Dijkstra)
print(gx.shortest_path(G, "A", "C", weight="weight"))  # ["A", "B", "C"]

# Directed graph
D = gx.DiGraph()
D.add_edges_from([("X", "Y"), ("Y", "Z")])
print(gx.shortest_path(D, "X", "Z"))           # ["X", "Y", "Z"]

# No path → raises NetworkXNoPath
try:
    gx.shortest_path(G, "A", "isolated")
except gx.NetworkXNoPath:
    print("No path!")
```

---

#### `gx.shortest_path_length`

```python
gx.shortest_path_length(
    G,
    source,
    target,
    weight=None,
    method=None,
) -> float
```

Return the total cost of the shortest path.
With `weight=None` this is the hop count (integer). With a weight attribute it is
the sum of edge weights along the path.

```python
gx.shortest_path_length(G, "A", "C")                   # 1 (hops)
gx.shortest_path_length(G, "A", "C", weight="weight")  # 3.0
```

---

#### `gx.has_path`

```python
gx.has_path(G, source, target) -> bool
```

Return `True` if any path exists between `source` and `target`, `False` otherwise.
Much faster than catching `NetworkXNoPath` in a try/except block.

```python
if gx.has_path(G, "A", "D"):
    path = gx.shortest_path(G, "A", "D")
```

---

#### `gx.all_pairs_shortest_path_length`

```python
gx.all_pairs_shortest_path_length(G, cutoff=None) -> Generator
```

Compute the shortest-path length between **every** pair of nodes.
Yields `(source, {target: length})` tuples. Memory-efficient — results are streamed,
not stored all at once.

| Parameter | Default | Description |
|---|---|---|
| `cutoff` | `None` | Ignore paths longer than this hop count |

```python
# Build a distance matrix
distances = dict(gx.all_pairs_shortest_path_length(G))
print(distances["A"]["C"])   # 1

# With a cutoff (only paths of ≤ 2 hops)
short_distances = dict(gx.all_pairs_shortest_path_length(G, cutoff=2))
```

---

### Connected Components

These functions work differently for undirected and directed graphs:

| Function | Graph type | Meaning |
|---|---|---|
| `connected_components` | `Graph` | Groups reachable ignoring direction |
| `weakly_connected_components` | `DiGraph` | Connected when edge directions are ignored |
| `strongly_connected_components` | `DiGraph` | Each node can reach every other (Kosaraju) |

#### Undirected components

```python
gx.connected_components(G)           # → Generator[set]
gx.number_connected_components(G)    # → int
gx.is_connected(G)                   # → bool
gx.node_connected_component(G, n)    # → set — component containing n
```

```python
import grapx as gx

G = gx.Graph()
G.add_edges_from([(1, 2), (2, 3)])   # component 1
G.add_edge(4, 5)                     # component 2
G.add_node(6)                        # isolated node → component 3

print(gx.number_connected_components(G))  # 3
for comp in gx.connected_components(G):
    print(sorted(comp))
# [1, 2, 3]
# [4, 5]
# [6]

print(gx.node_connected_component(G, 2))  # {1, 2, 3}
```

---

#### Directed components

```python
gx.weakly_connected_components(G)            # → Generator[set]
gx.number_weakly_connected_components(G)     # → int
gx.is_weakly_connected(G)                   # → bool

gx.strongly_connected_components(G)          # → Generator[set]
gx.number_strongly_connected_components(G)   # → int
gx.is_strongly_connected(G)                 # → bool
```

```python
import grapx as gx

G = gx.DiGraph()
G.add_edges_from([(1, 2), (2, 3), (3, 1)])   # cycle — 1 SCC
G.add_edges_from([(4, 5)])                    # separate WCC

print(gx.number_weakly_connected_components(G))    # 2
print(gx.number_strongly_connected_components(G))  # 3
# SCCs: {1,2,3}, {4}, {5}
```

---

#### `gx.condensation`

```python
gx.condensation(G) -> DiGraph
```

Return the **condensation** of a directed graph: a DAG where each node represents one SCC
of the original graph. Useful for understanding high-level flow structure.

Nodes in the result are `frozenset` objects containing the original node IDs.

```python
dag = gx.condensation(G)
for scc in dag.nodes():
    print(set(scc))
```

---

### Centrality

#### `gx.degree_centrality`

```python
gx.degree_centrality(G) -> dict
```

Compute degree centrality for every node: `deg(v) / (n - 1)`. Values are in `[0, 1]`.
The computation runs in parallel inside Rust — essentially free even for million-node graphs.

```python
dc = gx.degree_centrality(G)
most_connected = max(dc, key=dc.get)
```

For directed graphs, degree centrality uses total degree (in + out).
Use `in_degree_centrality` / `out_degree_centrality` for directed-specific measures.

---

#### `gx.in_degree_centrality` / `gx.out_degree_centrality`

```python
gx.in_degree_centrality(G)   # → dict  (DiGraph only)
gx.out_degree_centrality(G)  # → dict  (DiGraph only)
```

```python
# Find the biggest "influencers" (most out-edges) and "hubs" (most in-edges)
out_c = gx.out_degree_centrality(G)
in_c  = gx.in_degree_centrality(G)

top_influencer = max(out_c, key=out_c.get)
top_hub        = max(in_c,  key=in_c.get)
```

---

#### `gx.betweenness_centrality`

```python
gx.betweenness_centrality(
    G,
    normalized=True,
    weight=None,
    endpoints=False,
) -> dict
```

Measure how often a node appears on shortest paths between other nodes.
Nodes with high betweenness are "bridges" or "brokers" in the network.
Uses Brandes' `O(VE)` algorithm.

| Parameter | Default | Description |
|---|---|---|
| `normalized` | `True` | Divide by `2/((n-1)(n-2))` for undirected, `1/((n-1)(n-2))` for directed |
| `weight` | `None` | Edge weight attribute. `None` = unweighted BFS (v0.1) |
| `endpoints` | `False` | Include source/target nodes in path counts |

```python
bc = gx.betweenness_centrality(G)
bridges = [n for n, c in bc.items() if c > 0.1]
```

---

#### `gx.closeness_centrality`

```python
gx.closeness_centrality(
    G,
    u=None,
    distance=None,
    wf_improved=True,
) -> dict | float
```

Nodes with high closeness centrality can reach all others quickly.
`closeness(v) = (reachable - 1) / sum_of_distances(v)`.

Pass `u=node` to get the score for a single node (returns `float` instead of `dict`).

| Parameter | Default | Description |
|---|---|---|
| `u` | `None` | Single node to compute (returns float). If None, returns dict for all nodes |
| `distance` | `None` | Edge attribute to use as distance |
| `wf_improved` | `True` | Apply Wasserman–Faust correction for disconnected graphs |

```python
cc = gx.closeness_centrality(G)
most_central = max(cc, key=cc.get)

# Single node
score = gx.closeness_centrality(G, u="Alice")   # float
```

---

### Traversal

All traversal functions work on both `Graph` and `DiGraph`.
For directed graphs, traversal naturally follows edge direction.

#### `gx.bfs_tree` / `gx.dfs_tree`

```python
gx.bfs_tree(G, source, reverse=False, depth_limit=None) -> DiGraph
gx.dfs_tree(G, source, depth_limit=None)               -> DiGraph
```

Return a directed tree rooted at `source` showing the traversal discovery order.
Each edge `(u, v)` means `v` was discovered from `u`.

```python
T = gx.bfs_tree(G, "Alice")
print(list(T.edges()))   # [(Alice, Bob), (Alice, Carol), ...]
```

`reverse=True` traverses predecessors instead of successors (on DiGraph).

---

#### `gx.bfs_edges` / `gx.dfs_edges`

```python
gx.bfs_edges(G, source, reverse=False, depth_limit=None) -> Generator
gx.dfs_edges(G, source=None, depth_limit=None)           -> Generator
```

Yield `(u, v)` edge tuples in breadth-first / depth-first discovery order.

```python
# Collect all nodes reachable from "root" in BFS order
visited = ["root"]
for parent, child in gx.bfs_edges(G, "root"):
    visited.append(child)

# Depth-limited search
for u, v in gx.bfs_edges(G, "root", depth_limit=3):
    print(f"{u} → {v}")
```

---

#### `gx.bfs_predecessors` / `gx.bfs_successors`

```python
gx.bfs_predecessors(G, source, depth_limit=None) -> Generator
gx.bfs_successors(G, source, depth_limit=None)   -> Generator
```

`bfs_predecessors` yields `(node, predecessor)` in BFS order.
`bfs_successors` yields `(node, [list_of_successors])` in BFS order.

```python
# Reconstruct parent mapping
parent = dict(gx.bfs_predecessors(G, "root"))

# Layer-by-layer expansion
for node, children in gx.bfs_successors(G, "root"):
    print(f"{node} → {children}")
```

---

#### `gx.dfs_preorder_nodes`

```python
gx.dfs_preorder_nodes(G, source=None, depth_limit=None) -> Generator
```

Yield nodes in DFS pre-order (a node is visited before its descendants).

```python
order = list(gx.dfs_preorder_nodes(G, source="A"))
```

---

## Generators

All generators return a `Graph` (undirected) unless otherwise noted.
`create_using` accepts any graph constructor (e.g. `gx.DiGraph`).

### Random / Social network models

```python
gx.barabasi_albert_graph(n, m, seed=None) -> Graph
```
Scale-free network via preferential attachment. Each new node connects to `m`
existing nodes with probability proportional to their current degree.
Produces heavy-tailed ("power law") degree distributions typical of the web,
citation networks, and social platforms.

```python
G = gx.barabasi_albert_graph(n=1000, m=3, seed=42)
```

---

```python
gx.erdos_renyi_graph(n, p, seed=None, directed=False) -> Graph | DiGraph
```
Classic random graph. Each of the `n*(n-1)/2` possible edges is included
independently with probability `p`.

```python
G = gx.erdos_renyi_graph(n=500, p=0.05, seed=42)
D = gx.erdos_renyi_graph(n=100, p=0.1, directed=True)
```

---

```python
gx.watts_strogatz_graph(n, k, p, seed=None) -> Graph
```
Small-world graph: start with a ring lattice where every node connects to its
`k` nearest neighbours, then rewire each edge with probability `p`.
Models social networks (short average path length, high clustering).

```python
G = gx.watts_strogatz_graph(n=1000, k=6, p=0.1, seed=42)
```

---

### Classic / deterministic graphs

```python
gx.complete_graph(n, create_using=None) -> Graph
```
K_n — every node connects to every other node. Edge count = n*(n-1)/2.

```python
gx.path_graph(n, create_using=None) -> Graph
```
P_n — linear chain: `0 — 1 — 2 — … — n-1`.

```python
gx.cycle_graph(n, create_using=None) -> Graph
```
C_n — like `path_graph` but with an extra edge connecting the last node back to the first.

```python
gx.star_graph(n, create_using=None) -> Graph
```
S_n — node `0` is the hub, connected to nodes `1` through `n`. Total nodes = `n + 1`.

```python
gx.grid_2d_graph(m, n, periodic=False, create_using=None) -> Graph
```
2D grid. Nodes are `(row, col)` tuples for `0 ≤ row < m`, `0 ≤ col < n`.
`periodic=True` wraps around to create a torus.

```python
gx.karate_club_graph() -> Graph
```
Zachary's 1977 karate club social network — 34 nodes, 78 edges. The canonical
community-detection benchmark. Two groups emerge from PageRank + degree centrality.

```python
gx.petersen_graph() -> Graph
```
The Petersen graph — 10 nodes, 15 edges. A classic graph-theory example.

```python
gx.empty_graph(n=0) -> Graph    # n nodes, 0 edges
gx.null_graph()     -> Graph    # 0 nodes, 0 edges
gx.trivial_graph()  -> Graph    # 1 node,  0 edges
```

---

## I/O

### `gx.read_edgelist`

```python
gx.read_edgelist(
    path,
    comments="#",
    delimiter=None,
    create_using=None,
    nodetype=None,
    data=True,
    encoding="utf-8",
) -> Graph | DiGraph
```

Parse a plain-text edge list file. Each non-comment line should contain
two node identifiers separated by `delimiter` (default: any whitespace),
optionally followed by numeric or string attributes.

| Parameter | Default | Description |
|---|---|---|
| `path` | — | File path string or any file-like object |
| `comments` | `"#"` | Lines starting with this character are skipped |
| `delimiter` | `None` | Column separator. `None` = any whitespace |
| `create_using` | `None` | Graph constructor to use. Default: `gx.Graph` |
| `nodetype` | `None` | Callable to convert node strings, e.g. `int`, `float`, `str` |
| `data` | `True` | `True` = parse extra columns as `{"weight": ..., "attr2": ...}` |
| `encoding` | `"utf-8"` | File encoding |

**Edge list file format:**
```
# comment lines are ignored
Alice Bob 1.5
Bob Carol 2.0
Carol Alice 0.5
```

```python
import grapx as gx

# Basic read
G = gx.read_edgelist("edges.txt")

# Integer node IDs, directed graph
G = gx.read_edgelist(
    "edges.txt",
    nodetype=int,
    create_using=gx.DiGraph,
)

# From a file-like object (e.g. io.StringIO)
import io
data = "1 2\n2 3\n3 1\n"
G = gx.read_edgelist(io.StringIO(data), nodetype=int)
```

---

### `gx.write_edgelist`

```python
gx.write_edgelist(
    G,
    path,
    comments="#",
    delimiter=" ",
    data=True,
    encoding="utf-8",
) -> None
```

Write a graph to an edge list file. Each edge is written as one line.

| Parameter | Default | Description |
|---|---|---|
| `G` | — | Graph or DiGraph to write |
| `path` | — | File path string or file-like object |
| `comments` | `"#"` | Prefix for header comment lines |
| `delimiter` | `" "` | Column separator |
| `data` | `True` | `True` = include all edge attributes. `["weight"]` = only those keys |
| `encoding` | `"utf-8"` | File encoding |

```python
G = gx.karate_club_graph()
gx.write_edgelist(G, "karate.txt")

# Only write the weight attribute
gx.write_edgelist(G, "weighted.txt", data=["weight"])

# Tab-separated, no attributes
gx.write_edgelist(G, "bare.tsv", delimiter="\t", data=False)
```

---

### `gx.generate_edgelist`

```python
gx.generate_edgelist(G, delimiter=" ", data=True) -> Generator
```

Like `write_edgelist` but yields lines as strings instead of writing to disk.
Useful for streaming, in-memory serialization, or piping to another format.

```python
lines = list(gx.generate_edgelist(G))

# Stream to a compressed file
import gzip
with gzip.open("graph.txt.gz", "wt") as f:
    for line in gx.generate_edgelist(G):
        f.write(line + "\n")
```

---

## Exceptions

All exceptions live in `grapx.exception` and are re-exported from the top-level package.

| Exception | When raised |
|---|---|
| `gx.GrapxError` | Base class for all grapx exceptions |
| `gx.NodeNotFound` | A referenced node is not in the graph |
| `gx.NetworkXNoPath` | No path exists between two nodes |
| `gx.NetworkXError` | Compatibility alias for `GrapxError` |
| `gx.GrapxAlgorithmError` | An algorithm encountered an invalid state |

```python
import grapx as gx

G = gx.Graph()
G.add_edge(1, 2)

try:
    path = gx.shortest_path(G, 1, 99)
except gx.NodeNotFound as e:
    print(f"Node missing: {e}")
except gx.NetworkXNoPath:
    print("No path exists")

try:
    G.remove_node(999)
except gx.NodeNotFound:
    pass   # silent skip is fine
```

Pydantic `ValidationError` is raised for invalid algorithm parameters
(wrong types, out-of-range values). Import it from `pydantic` if you need to catch it:

```python
from pydantic import ValidationError
try:
    gx.pagerank(G, alpha=2.0)
except ValidationError as e:
    print(e)   # clear message: alpha must be ≤ 1
```

# grapx Cookbook

Practical recipes for common graph tasks. Copy, paste, adapt.

> **See also:** [API Reference](api-reference.md)

---

## Table of Contents

1. [Building graphs from data](#building-graphs-from-data)
2. [Node and edge attributes](#node-and-edge-attributes)
3. [Finding important nodes](#finding-important-nodes)
4. [Shortest paths and routing](#shortest-paths-and-routing)
5. [Community detection and clusters](#community-detection-and-clusters)
6. [Traversal patterns](#traversal-patterns)
7. [Filtering and subgraphs](#filtering-and-subgraphs)
8. [Directed graph patterns](#directed-graph-patterns)
9. [Large graph performance tips](#large-graph-performance-tips)
10. [I/O patterns](#io-patterns)
11. [NetworkX migration](#networkx-migration)

---

## Building graphs from data

### From a list of tuples

```python
import grapx as gx

edges = [("Alice", "Bob"), ("Bob", "Carol"), ("Carol", "Alice")]
G = gx.Graph()
G.add_edges_from(edges)
```

### From a Pandas DataFrame

```python
import pandas as pd
import grapx as gx

df = pd.DataFrame({
    "source": ["Alice", "Bob",   "Carol"],
    "target": ["Bob",   "Carol", "Alice"],
    "weight": [1.5,     2.0,     0.5],
})

G = gx.DiGraph()
for _, row in df.iterrows():
    G.add_edge(row["source"], row["target"], weight=row["weight"])

# Or more efficiently using add_edges_from with a generator:
G = gx.DiGraph()
G.add_edges_from(
    (row.source, row.target, {"weight": row.weight})
    for row in df.itertuples()
)
```

### From a CSV file directly

```python
import grapx as gx

# edges.csv:
# source,target,weight
# Alice,Bob,1.5
# Bob,Carol,2.0

G = gx.read_edgelist("edges.csv", delimiter=",", nodetype=str)
```

### From a Python dict (adjacency list)

```python
import grapx as gx

adj = {
    "Alice": ["Bob", "Carol"],
    "Bob":   ["Carol"],
    "Carol": [],
}

G = gx.Graph(adj)   # pass adjacency dict to constructor
```

### From a set of integer IDs (bulk)

```python
import grapx as gx

# All pairs within each group form cliques
groups = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]

G = gx.Graph()
for group in groups:
    for i, a in enumerate(group):
        for b in group[i + 1:]:
            G.add_edge(a, b)
```

### Copying and merging graphs

```python
# Deep copy
G2 = G.copy()

# Merge G2 into G (all nodes and edges from G2 are added to G)
G.update(G2)

# Create a new graph that is the union
G_union = gx.Graph()
G_union.update(G1)
G_union.update(G2)
```

---

## Node and edge attributes

### Set attributes at creation time

```python
G.add_node("Alice", age=30, team="engineering", score=0.0)
G.add_edge("Alice", "Bob", weight=1.5, since=2020, active=True)
```

### Update attributes after the fact

```python
# Node attributes
G.nodes["Alice"]["score"] = 0.95
G.nodes["Alice"].update({"rank": 1, "verified": True})

# Edge attributes
G["Alice"]["Bob"]["weight"] = 2.0
G.edges[("Alice", "Bob")]["label"] = "colleague"
```

### Read attributes

```python
# All attributes for a node
print(G.nodes["Alice"])        # {"age": 30, "team": "engineering", ...}

# Specific attribute
print(G.nodes["Alice"]["age"]) # 30

# Edge data
print(G.get_edge_data("Alice", "Bob"))          # {"weight": 1.5, ...}
print(G.get_edge_data("Alice", "Bob", default={}))  # safe — returns {} if missing
```

### Iterate nodes/edges with attributes

```python
# Nodes
for node, data in G.nodes(data=True):
    print(node, data)

# Edges
for u, v, data in G.edges(data=True):
    print(u, v, data.get("weight", 1.0))

# Filter by attribute
engineers = [n for n, d in G.nodes(data=True) if d.get("team") == "engineering"]
heavy = [(u, v) for u, v, d in G.edges(data=True) if d.get("weight", 0) > 1.0]
```

### Store computed scores back on nodes

```python
pr = gx.pagerank(G)
for node, score in pr.items():
    G.nodes[node]["pagerank"] = score

# Now every node carries its PageRank score as an attribute
top5 = sorted(G.nodes(data=True), key=lambda x: -x[1].get("pagerank", 0))[:5]
```

---

## Finding important nodes

### Top-N by PageRank (most "authoritative")

```python
pr = gx.pagerank(G, alpha=0.85)
top10 = sorted(pr, key=pr.get, reverse=True)[:10]
print(top10)
```

### Hub vs Authority nodes (HITS)

```python
hub, auth = gx.hits(G)

# Good hubs — they link to many authorities
top_hubs = sorted(hub, key=hub.get, reverse=True)[:5]

# Good authorities — they are linked to by many hubs
top_authorities = sorted(auth, key=auth.get, reverse=True)[:5]
```

### Most connected nodes (degree centrality)

```python
dc = gx.degree_centrality(G)

# Most connected
top_connectors = sorted(dc, key=dc.get, reverse=True)[:5]

# In a directed graph, distinguish influencers vs listeners
out_c = gx.out_degree_centrality(G)  # many outgoing → influencers
in_c  = gx.in_degree_centrality(G)   # many incoming → influential / popular
```

### Bottleneck / broker nodes (betweenness centrality)

Nodes with high betweenness sit on many shortest paths — removing them would
fragment the network.

```python
bc = gx.betweenness_centrality(G, normalized=True)
bottlenecks = sorted(bc, key=bc.get, reverse=True)[:5]
```

### Most "reachable" nodes (closeness centrality)

```python
cc = gx.closeness_centrality(G)
most_central = sorted(cc, key=cc.get, reverse=True)[:5]
```

### Combine multiple centrality measures

```python
import grapx as gx

G = gx.karate_club_graph()

pr = gx.pagerank(G)
dc = gx.degree_centrality(G)
bc = gx.betweenness_centrality(G)

# Composite score (simple mean of normalised ranks)
nodes = list(G.nodes())
scores = {}
for n in nodes:
    scores[n] = (pr[n] + dc[n] + bc[n]) / 3.0

top = sorted(scores, key=scores.get, reverse=True)[:5]
```

---

## Shortest paths and routing

### Basic shortest path (hop count)

```python
path = gx.shortest_path(G, "A", "Z")
print(" → ".join(str(n) for n in path))
```

### Weighted shortest path (Dijkstra)

```python
path = gx.shortest_path(G, "A", "Z", weight="weight")
dist = gx.shortest_path_length(G, "A", "Z", weight="weight")
print(f"Path: {path}, Total cost: {dist:.2f}")
```

### Safe path lookup (no exception)

```python
if gx.has_path(G, source, target):
    path = gx.shortest_path(G, source, target)
else:
    path = None
```

### All shortest path lengths from one source

```python
# BFS distances from "root" to all reachable nodes
all_lengths = dict(gx.all_pairs_shortest_path_length(G))
distances_from_root = all_lengths.get("root", {})

# Eccentricity (max distance from "root")
eccentricity = max(distances_from_root.values(), default=0)
```

### Find all bottleneck paths (betweenness)

```python
# Nodes that appear most often on shortest paths between all pairs
bc = gx.betweenness_centrality(G)
# High betweenness → critical routing points
critical = [n for n, c in bc.items() if c > 0.2]
```

### Detect unreachable nodes

```python
source = "hub"
unreachable = [n for n in G.nodes() if not gx.has_path(G, source, n)]
print(f"{len(unreachable)} nodes can't be reached from {source}")
```

---

## Community detection and clusters

### Get all clusters (connected components)

```python
# Undirected
components = list(gx.connected_components(G))
largest = max(components, key=len)
print(f"Largest component: {len(largest)} nodes")

# Sort by size descending
components.sort(key=len, reverse=True)
for i, comp in enumerate(components[:5]):
    print(f"  Component {i+1}: {len(comp)} nodes")
```

### Check if the graph is fully connected

```python
if not gx.is_connected(G):
    n = gx.number_connected_components(G)
    print(f"Graph has {n} disconnected components")
```

### Find the component for a specific node

```python
comp = gx.node_connected_component(G, "Alice")
print(f"Alice's cluster: {sorted(comp)}")
```

### Analyse weakly vs strongly connected (directed)

```python
D = gx.DiGraph()
D.add_edges_from([("A", "B"), ("B", "C"), ("C", "A"), ("D", "E")])

# WCC treats edges as undirected
print(gx.number_weakly_connected_components(D))   # 2 (ABC group, DE group)

# SCC requires mutual reachability
print(gx.number_strongly_connected_components(D)) # 3 (ABC is one SCC, D and E each separate)

for scc in gx.strongly_connected_components(D):
    print(sorted(scc))
```

### Condense a directed graph to its SCC DAG

```python
dag = gx.condensation(G)
print(f"Condensation has {dag.number_of_nodes()} super-nodes")

# Each node is a frozenset of original nodes
for scc in dag.nodes():
    if len(scc) > 1:
        print(f"Mutual cycle: {set(scc)}")
```

---

## Traversal patterns

### BFS level-by-level exploration

```python
# Reconstruct BFS layers
from collections import defaultdict

layers = defaultdict(list)
parent = dict(gx.bfs_predecessors(G, source="root"))
for node in gx.dfs_preorder_nodes(G, source="root"):
    depth = 0
    n = node
    while n in parent:
        n = parent[n]
        depth += 1
    layers[depth].append(node)

for depth, nodes in sorted(layers.items()):
    print(f"Depth {depth}: {nodes}")
```

### Collect all nodes reachable within N hops

```python
def reachable_within(G, source, max_hops):
    reachable = {source}
    for u, v in gx.bfs_edges(G, source, depth_limit=max_hops):
        reachable.add(v)
    return reachable

nearby = reachable_within(G, "Alice", max_hops=2)
```

### Build a BFS tree and inspect it

```python
T = gx.bfs_tree(G, "root")
print(f"BFS tree has {T.number_of_nodes()} nodes and {T.number_of_edges()} edges")

# T is a DiGraph — root is the only node with in_degree=0
root = [n for n in T.nodes() if T.in_degree[n] == 0][0]
leaves = [n for n in T.nodes() if T.out_degree[n] == 0]
```

### DFS for cycle detection (undirected)

```python
def has_cycle(G):
    visited = set()
    for start in G.nodes():
        if start in visited:
            continue
        stack = [(start, None)]
        local = set()
        while stack:
            node, parent = stack.pop()
            if node in local:
                return True
            local.add(node)
            visited.add(node)
            for nb in G.neighbors(node):
                if nb != parent:
                    stack.append((nb, node))
    return False
```

---

## Filtering and subgraphs

### Induced subgraph on a subset of nodes

```python
# Subgraph of the 10 highest-PageRank nodes
pr = gx.pagerank(G)
top10_nodes = sorted(pr, key=pr.get, reverse=True)[:10]
sub = G.subgraph(top10_nodes)
print(sub.number_of_nodes(), sub.number_of_edges())
```

### Remove low-weight edges before analysis

```python
# Work on a copy so the original is unchanged
G2 = G.copy()
low_weight = [(u, v) for u, v, d in G2.edges(data=True) if d.get("weight", 1.0) < 0.5]
G2.remove_edges_from(low_weight)
```

### Keep only the largest connected component

```python
components = list(gx.connected_components(G))
largest_nodes = max(components, key=len)
G_main = G.subgraph(largest_nodes).copy()  # .copy() makes it a standalone graph
```

### Filter nodes by attribute

```python
# Subgraph of only "verified" nodes
verified = [n for n, d in G.nodes(data=True) if d.get("verified")]
sub = G.subgraph(verified)
```

### Ego graph (1-hop neighbourhood)

```python
def ego_graph(G, node):
    """Return the subgraph of node and all its direct neighbours."""
    neighbors = set(G.neighbors(node)) | {node}
    return G.subgraph(neighbors).copy()

ego = ego_graph(G, "Alice")
```

---

## Directed graph patterns

### Convert undirected → directed

```python
D = G.to_directed()   # adds both (u,v) and (v,u) for every edge in G
```

### Convert directed → undirected

```python
# Keep all edges (even one-directional ones)
U = D.to_undirected(reciprocal=False)

# Keep only mutually-connected pairs
U_mutual = D.to_undirected(reciprocal=True)
```

### Reverse all edges (transpose)

```python
R = D.reverse()   # every (u→v) becomes (v→u)
```

### Find source nodes (no incoming edges)

```python
sources = [n for n in D.nodes() if D.in_degree[n] == 0]
```

### Find sink nodes (no outgoing edges)

```python
sinks = [n for n in D.nodes() if D.out_degree[n] == 0]
```

### Topological sort (DAG processing order)

grapx does not implement topological sort directly, but you can derive it
from a DFS post-order traversal:

```python
def topological_sort(G):
    """Yield nodes in topological order (for DAGs only)."""
    visited = set()
    order = []

    def dfs(node):
        visited.add(node)
        for successor in G.successors(node):
            if successor not in visited:
                dfs(successor)
        order.append(node)

    for node in G.nodes():
        if node not in visited:
            dfs(node)

    return reversed(order)

for node in topological_sort(dag):
    print(node)
```

---

## Large graph performance tips

### Pre-allocate nodes and edges

```python
# Slightly faster than adding nodes one at a time when count is known
G.add_nodes_from(range(1_000_000))
G.add_edges_from(edge_generator)   # generators avoid holding all edges in memory
```

### Use integer node IDs for maximum performance

```python
# Internally grapx maps Python objects to u32 indices.
# Using int nodes avoids hashing overhead for complex objects.
G = gx.Graph()
G.add_edges_from(zip(sources_array, targets_array))   # fast bulk load
```

### Avoid repeated attribute lookups in tight loops

```python
# Slow — attribute lookup inside loop
for n in G.nodes():
    score = G.nodes[n].get("score", 0.0)

# Fast — materialise once
node_scores = {n: d.get("score", 0.0) for n, d in G.nodes(data=True)}
for n in G.nodes():
    score = node_scores[n]
```

### Stream edge lists for very large files

```python
# Don't read the whole file at once — use the generator form
G = gx.Graph()
with open("huge_graph.txt") as f:
    for line in f:
        if line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            G.add_edge(parts[0], parts[1])
```

### Use `generate_edgelist` for streaming output

```python
import gzip
import grapx as gx

G = gx.barabasi_albert_graph(1_000_000, 3)

# Stream directly to compressed file — never holds full text in memory
with gzip.open("graph.txt.gz", "wt") as f:
    for line in gx.generate_edgelist(G, data=False):
        f.write(line + "\n")
```

### Work on the largest component only

```python
# Discard isolated nodes and tiny fragments before running expensive algorithms
components = list(gx.connected_components(G))
main = max(components, key=len)
G_main = G.subgraph(main).copy()

pr = gx.pagerank(G_main)   # only processes the connected core
```

---

## I/O patterns

### Round-trip to disk

```python
import grapx as gx

G = gx.karate_club_graph()
gx.write_edgelist(G, "karate.txt")
G2 = gx.read_edgelist("karate.txt", nodetype=int)

assert G.number_of_nodes() == G2.number_of_nodes()
assert G.number_of_edges() == G2.number_of_edges()
```

### Preserve edge weights

```python
G = gx.Graph()
G.add_edge(1, 2, weight=3.14)
G.add_edge(2, 3, weight=2.71)

gx.write_edgelist(G, "weighted.txt", data=["weight"])

G2 = gx.read_edgelist("weighted.txt", nodetype=int)
print(G2.get_edge_data(1, 2))   # {"weight": "3.14"}  ← string; parse if needed
```

### Read a directed graph

```python
G = gx.read_edgelist("directed.txt", create_using=gx.DiGraph)
```

### Handle tab-separated files

```python
G = gx.read_edgelist("data.tsv", delimiter="\t", nodetype=int)
```

### Serialise to JSON

grapx does not ship a JSON writer yet, but it is easy to build one:

```python
import json
import grapx as gx

def to_json(G):
    return {
        "nodes": [{"id": n, **data} for n, data in G.nodes(data=True)],
        "edges": [{"source": u, "target": v, **data} for u, v, data in G.edges(data=True)],
        "directed": G.is_directed(),
    }

payload = json.dumps(to_json(G), indent=2)
```

---

## NetworkX migration

grapx is designed to be a drop-in replacement for NetworkX.
In most cases you only need to change one line.

```python
# Before
import networkx as nx
G = nx.DiGraph()

# After
import grapx as gx
G = gx.DiGraph()
```

### API compatibility table

| NetworkX | grapx | Notes |
|---|---|---|
| `G.add_node(n, **attr)` | identical | ✓ |
| `G.add_edge(u, v, **attr)` | identical | ✓ |
| `G.nodes[n]` | identical | ✓ |
| `G.edges(data=True)` | identical | ✓ |
| `nx.pagerank(G)` | `gx.pagerank(G)` | 80–120× faster |
| `nx.shortest_path(G, s, t)` | `gx.shortest_path(G, s, t)` | 100–130× faster |
| `nx.connected_components(G)` | `gx.connected_components(G)` | identical signature |
| `nx.betweenness_centrality(G)` | `gx.betweenness_centrality(G)` | identical |
| `nx.bfs_tree(G, s)` | `gx.bfs_tree(G, s)` | identical |
| `nx.read_edgelist(path)` | `gx.read_edgelist(path)` | identical |
| `G.to_directed()` | identical | ✓ |
| `G.subgraph(nodes)` | identical | ✓ |

### Known differences

| Feature | NetworkX | grapx v0.1 |
|---|---|---|
| Multi-edges (parallel edges) | Full support | Tracked via flag; deduplication planned for v0.2 |
| `personalization` in PageRank | Supported | Accepted but ignored (v0.2) |
| `nstart` in PageRank | Supported | Accepted but ignored (v0.2) |
| GraphML / GML I/O | Supported | v0.2 roadmap |
| Drawing (`nx.draw`)| Supported via matplotlib | Not in scope (use [pyvis](https://pyvis.readthedocs.io/) with grapx data) |

### Visualisation with pyvis

grapx graphs can be visualised with pyvis, D3.js, or any tool that accepts
an edge list:

```python
import grapx as gx
from pyvis.network import Network

G = gx.karate_club_graph()

net = Network(notebook=False)
for u, v in G.edges():
    net.add_edge(str(u), str(v))

net.show("karate.html")
```

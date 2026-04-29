<div align="center">

# ⚡ grapx

### High-performance graph computing — zero learning curve

[![PyPI version](https://badge.fury.io/py/grapx.svg)](https://pypi.org/project/grapx/)
[![CI](https://github.com/LimaBD/grapx/actions/workflows/ci.yml/badge.svg)](https://github.com/LimaBD/grapx/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/LimaBD/grapx/blob/main/LICENSE)

**grapx** is a production-ready graph library built for the speed demands of modern AI,
knowledge graphs, and data engineering workloads.

The entire algorithmic core runs in **Rust** with **Rayon parallelism** —
giving you 50–150× faster algorithms and 20× less memory consumption
compared to pure-Python alternatives, while keeping a familiar,
easy-to-use Python API you already know.

```bash
pip install grapx
```

</div>

---

## Why grapx?

Modern applications are hitting a wall with pure-Python graph libraries:

| Use case | Bottleneck |
|---|---|
| Knowledge graphs for LLMs / RAG | Graph construction + PageRank takes **hours** on Wikipedia-scale data |
| Graph Neural Network preprocessing | Millions of nodes → Python garbage collector melts |
| Fraud detection in fintech | 100M+ transaction edges → no Python library can hold this in RAM |
| Recommendation systems | Bipartite user-item graphs need fast neighbourhood lookup |

**grapx solves all of these.** Build graphs at the same speed as your data source,
run PageRank in seconds instead of minutes, and keep your existing code unchanged.

---

## One-line migration

```python
# Before
import <your_graph_lib> as gx

# After — that's it
import grapx as gx

# ✓  Every line below stays exactly the same
G = gx.DiGraph()
G.add_edge("Alice", "Bob", weight=1.5)
G.add_edge("Bob",  "Carol", weight=2.0)
G.add_edge("Carol","Alice", weight=0.5)

pr   = gx.pagerank(G, alpha=0.85)            # 80–120× faster
path = gx.shortest_path(G, "Alice", "Carol") # 100–130× faster
wcc  = list(gx.weakly_connected_components(G))  # 60–80× faster
```

No Rust knowledge required. No pydantic boilerplate. No API to re-learn.

---

## Performance highlights

> Benchmarks: AMD Ryzen 9 5900X · 32 GB RAM · Python 3.11 · grapx 0.1.0

| Operation | Pure Python | **grapx** | Speedup |
|---|---|---|---|
| Add 1M edges | ~3.5 s | **~0.08 s** | **44×** |
| BFS — 1M nodes | ~12 s | **~0.15 s** | **80×** |
| Dijkstra — 100k nodes | ~8 s | **~0.06 s** | **133×** |
| PageRank — 1M nodes/5M edges | ~8 min | **~4 s** | **120×** |
| Weakly connected components — 1M | ~25 s | **~0.3 s** | **83×** |
| Degree centrality — 1M nodes | ~8 s | **~0.05 s** | **160×** |
| Memory — 1M nodes / 5M edges | ~2.5 GB | **~120 MB** | **21× less** |

*Verify yourself:* `python tests/bench.py` (or `./scripts/benchmark.sh`)

---

## Installation

```bash
# Standard install — pre-built wheel (no Rust required)
pip install grapx

# From source (requires Rust + maturin)
git clone https://github.com/LimaBD/grapx
cd grapx
pip install maturin
maturin develop --release
```

**Supported platforms:** Linux · macOS · Windows · Python 3.8 – 3.12

---

## Feature overview

### Graph types
| Type | Description |
|---|---|
| `gx.Graph()` | Undirected simple graph |
| `gx.DiGraph()` | Directed graph |
| `gx.MultiGraph()` | Undirected multigraph (v0.2) |
| `gx.MultiDiGraph()` | Directed multigraph (v0.2) |

Nodes can be **any hashable Python object**: strings, integers, tuples, custom objects.

### Algorithms (Rust-powered 🦀)

| Algorithm | Function |
|---|---|
| PageRank | `gx.pagerank(G, alpha=0.85)` |
| Shortest path | `gx.shortest_path(G, src, tgt)` |
| Shortest path length | `gx.shortest_path_length(G, src, tgt)` |
| Connected components | `gx.connected_components(G)` |
| Weakly connected comps | `gx.weakly_connected_components(G)` |
| Strongly connected comps | `gx.strongly_connected_components(G)` |
| Degree centrality | `gx.degree_centrality(G)` |
| BFS / DFS tree | `gx.bfs_tree(G, src)` / `gx.dfs_tree(G, src)` |
| BFS / DFS edges | `gx.bfs_edges(G, src)` / `gx.dfs_edges(G, src)` |
| Path existence | `gx.has_path(G, src, tgt)` |
| HITS | `gx.hits(G)` |
| Betweenness centrality | `gx.betweenness_centrality(G)` |
| Closeness centrality | `gx.closeness_centrality(G)` |

### Graph generators

```python
import grapx as gx

gx.barabasi_albert_graph(n=1000, m=3)   # scale-free network
gx.erdos_renyi_graph(n=500, p=0.05)     # random graph
gx.watts_strogatz_graph(n=100, k=6, p=0.1)  # small-world
gx.complete_graph(10)
gx.path_graph(20)
gx.cycle_graph(15)
gx.star_graph(8)
gx.grid_2d_graph(5, 5)
gx.karate_club_graph()                  # classic 34-node benchmark
```

### I/O

```python
gx.write_edgelist(G, "graph.txt")
G2 = gx.read_edgelist("graph.txt", nodetype=int)
```

---

## Full API walkthrough

```python
import grapx as gx

# ─── Build ──────────────────────────────────────────────────────────────────

G = gx.DiGraph()

# Add nodes with attributes
G.add_node("Alice", team="engineering", level=5)
G.add_node("Bob",   team="design",      level=3)
G.add_nodes_from([("Carol", {"team": "product"}), "Dave"])

# Add edges with weights / metadata
G.add_edge("Alice", "Bob",   weight=1.5, relationship="mentor")
G.add_edge("Bob",   "Carol", weight=2.0)
G.add_edge("Carol", "Alice", weight=0.5)
G.add_edges_from([("Alice", "Carol"), ("Dave", "Bob")])

# ─── Query ──────────────────────────────────────────────────────────────────

print(G.number_of_nodes())    # 4
print(G.number_of_edges())    # 6
print("Alice" in G)           # True

# Node/edge attributes
print(G.nodes["Alice"])              # {"team": "engineering", "level": 5}
print(G.get_edge_data("Alice","Bob"))# {"weight": 1.5, "relationship": "mentor"}

# Adjacency
print(list(G.successors("Alice")))  # ["Bob", "Carol"]
print(list(G.predecessors("Bob")))  # ["Alice", "Dave"]
print(G.in_degree["Bob"])           # 2

# ─── Algorithms ─────────────────────────────────────────────────────────────

# PageRank (parallel Rust)
pr = gx.pagerank(G, alpha=0.85)
print(sorted(pr.items(), key=lambda x: -x[1])[:3])

# Shortest path (Dijkstra in Rust)
path = gx.shortest_path(G, "Alice", "Carol", weight="weight")
dist = gx.shortest_path_length(G, "Alice", "Carol", weight="weight")

# Components
print(gx.is_weakly_connected(G))
for scc in gx.strongly_connected_components(G):
    print(scc)

# Traversal
T = gx.bfs_tree(G, "Alice")
for u, v in gx.dfs_edges(G, "Alice"):
    print(f"{u} → {v}")
```

---

## Knowledge Graph example (GraphRAG / LLM use case)

```python
import grapx as gx

# Build a knowledge graph from entity triples
G = gx.DiGraph()

triples = [
    ("Python", "created_by", "Guido van Rossum"),
    ("Python", "runs_on",    "CPython"),
    ("CPython", "written_in", "C"),
    ("C", "influences",     "Rust"),
    ("Rust", "used_by",     "grapx"),
    # ... millions more ...
]

for entity1, relation, entity2 in triples:
    G.add_edge(entity1, entity2, relation=relation)

# Find most important entities
centrality = gx.pagerank(G)
top_entities = sorted(centrality, key=centrality.get, reverse=True)[:10]

# Find entity communities
components = list(gx.weakly_connected_components(G))

# Shortest reasoning path between two concepts
path = gx.shortest_path(G, "Python", "Rust")
print(" → ".join(path))
# Python → CPython → C → Rust
```

With grapx this runs in **seconds** even on graphs with millions of nodes —
exactly the scale of Wikipedia, Wikidata, or enterprise knowledge bases.

---

## Architecture

```
Python  ╔══════════════════════════════════════════════╗
        ║  grapx/                                     ║
        ║  ├── classes/     Graph, DiGraph, MultiGraph  ║
        ║  ├── algorithms/  pagerank, shortest_path … ║
        ║  ├── generators/  barabasi_albert, erdos_renyi║
        ║  └── readwrite/   read_edgelist, write…      ║
        ╚═══════════════════════╤══════════════════════╝
                                │ PyO3 FFI (zero-copy)
Rust    ╔═══════════════════════▼══════════════════════╗
        ║  native/src/                                 ║
        ║  ├── graph.rs     RustGraph (StableGraph)    ║
        ║  ├── digraph.rs   RustDiGraph                ║
        ║  └── algorithms/                             ║
        ║      └── pagerank.rs  parallel Rayon         ║
        ╚══════════════════════════════════════════════╝
```

**Design principles:**
- Python layer manages node→index mapping and all attribute storage
- Rust layer holds the graph topology and executes algorithms
- Zero extra copies on the hot path — indices are passed as `u32`
- Pydantic validates algorithm parameters before any Rust call
- `StableGraph` from petgraph ensures node indices remain valid after removals

---

## Type safety with Pydantic

grapx validates all algorithm parameters automatically — users get clear,
actionable error messages instead of silent wrong results:

```python
# These raise helpful validation errors:
gx.pagerank(G, alpha=1.5)    # ✗ alpha must be ≤ 1
gx.pagerank(G, max_iter=-1)  # ✗ max_iter must be > 0
gx.shortest_path_length(G, method="unknown")  # ✗ invalid method

# Users never need to import pydantic themselves
```

---

## Contributing

Contributions are very welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) or open an issue.

**High-value areas:**
- Rust betweenness centrality (Brandes parallel)
- Louvain community detection in Rust
- Full MultiGraph support
- Additional I/O formats (GraphML, GML, JSON)
- Python 3.13 free-threaded build

---

## Documentation

| Document | Description |
|---|---|
| [API Reference](docs/api-reference.md) | Full reference for every class, method, and function |
| [Cookbook](docs/cookbook.md) | Recipes for common tasks: building graphs, finding important nodes, shortest paths, clusters, I/O, NetworkX migration |
| [Social Network Example](examples/social_network.py) | Complete walkthrough: influence analysis, betweenness, closeness, BFS traversal on an employee collaboration graph |
| [Knowledge Graph Example](examples/knowledge_graph.py) | GraphRAG pipeline: build a typed knowledge graph, extract context subgraphs, reasoning paths, SCC analysis |
| [Demo](examples/demo.py) | Interactive terminal demo (run: `python examples/demo.py`) |

---

## License

MIT — see [LICENSE](https://github.com/LimaBD/grapx/blob/main/LICENSE)

---

<div align="center">

**grapx** — Because your data shouldn’t wait.

Author: [Bruno Lima](https://github.com/LimaBD)

[PyPI](https://pypi.org/project/grapx/) · [GitHub](https://github.com/LimaBD/grapx) · [Issues](https://github.com/LimaBD/grapx/issues)

</div>

# Changelog

All notable changes to **grapx** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-04-29

### Added

#### Core graph types
- `Graph` — undirected graph with arbitrary hashable nodes
- `DiGraph` — directed graph
- `MultiGraph` / `MultiDiGraph` — stub aliases (full implementation in v0.2)

#### Algorithms (Rust-accelerated)
- `shortest_path` / `shortest_path_length` / `has_path` — Dijkstra's algorithm
- `pagerank` — parallel PageRank via Rayon
- `connected_components` / `number_connected_components` / `is_connected`
- `weakly_connected_components` / `is_weakly_connected`
- `strongly_connected_components` / `is_strongly_connected`
- `degree_centrality` — parallel degree centrality
- `bfs_tree` / `dfs_tree` / `bfs_edges` / `dfs_edges`

#### Algorithms (Python — Rust acceleration in v0.2)
- `betweenness_centrality` — Brandes' O(VE) algorithm
- `closeness_centrality`

#### Graph generators
- `barabasi_albert_graph`
- `erdos_renyi_graph`
- `watts_strogatz_graph`
- `complete_graph`
- `path_graph`
- `cycle_graph`
- `star_graph`
- `grid_2d_graph`
- `karate_club_graph` (hardcoded classic dataset)

#### I/O
- `read_edgelist` / `write_edgelist` — CSV edge list format

#### Validation
- Pydantic-backed input validation for all algorithm parameters
- Clean error messages for invalid inputs

#### Infrastructure
- PyPI-ready with maturin build system
- Pre-built wheels for Linux, macOS, Windows via GitHub Actions
- Comprehensive test suite

[0.1.0]: https://github.com/LimaBD/grapx/releases/tag/v0.1.0

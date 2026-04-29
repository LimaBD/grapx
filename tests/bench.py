"""
Benchmark: grapx performance on various graph operations.

Run with:
    python tests/bench.py

Output shows timing for each operation; useful for tuning and regression testing.
"""

import random
import time

# ─── Configuration ───────────────────────────────────────────────────────────

N_NODES = 50_000
N_EDGES = 250_000
SEED = 42

# ─── Driver ──────────────────────────────────────────────────────────────────


def generate_edges(n_nodes=N_NODES, n_edges=N_EDGES, seed=SEED):
    rng = random.Random(seed)
    return [
        (rng.randint(0, n_nodes - 1), rng.randint(0, n_nodes - 1))
        for _ in range(n_edges)
    ]


def bench_library(lib_name: str, lib):
    print(f"\n{'=' * 50}")
    print(f"  {lib_name}")
    print(f"{'=' * 50}")

    edges = generate_edges()
    results: dict = {}

    # 1. Graph construction
    t0 = time.perf_counter()
    G = lib.DiGraph()
    G.add_edges_from(edges)
    results["build"] = time.perf_counter() - t0
    print(f"  {'build':25s}: {results['build']*1000:8.1f} ms  "
          f"({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)")

    # 2. PageRank
    t0 = time.perf_counter()
    lib.pagerank(G, alpha=0.85, max_iter=30)
    results["pagerank"] = time.perf_counter() - t0
    print(f"  {'pagerank':25s}: {results['pagerank']*1000:8.1f} ms")

    # 3. Shortest path
    t0 = time.perf_counter()
    try:
        path = lib.shortest_path(G, 0, N_NODES // 2)
        path_len = len(path)
    except Exception:
        path_len = 0
    results["shortest_path"] = time.perf_counter() - t0
    print(f"  {'shortest_path':25s}: {results['shortest_path']*1000:8.1f} ms"
          f"  (path length: {path_len})")

    # 4. Weakly connected components
    t0 = time.perf_counter()
    wcc = list(lib.weakly_connected_components(G))
    results["wcc"] = time.perf_counter() - t0
    print(f"  {'weakly_conn_components':25s}: {results['wcc']*1000:8.1f} ms"
          f"  ({len(wcc)} components)")

    # 5. Degree centrality
    t0 = time.perf_counter()
    lib.degree_centrality(G)
    results["degree_centrality"] = time.perf_counter() - t0
    print(f"  {'degree_centrality':25s}: {results['degree_centrality']*1000:8.1f} ms")

    return results


def main():
    print(f"\nBenchmark: {N_NODES:,} nodes / {N_EDGES:,} edges")

    import grapx as gx

    r_gx = bench_library("grapx  (Rust core)", gx)

    # Optional: compare against reference implementation if installed
    try:
        import networkx as _nx_ref
        r_ref = bench_library("networkx (pure Python)", _nx_ref)

        print(f"\n{'=' * 50}")
        print("  SPEEDUP SUMMARY  (grapx vs reference)")
        print(f"{'=' * 50}")
        for op in r_gx:
            if r_gx[op] > 0 and op in r_ref:
                speedup = r_ref[op] / r_gx[op]
                bar = "█" * int(speedup)
                print(f"  {op:25s}: {speedup:6.1f}x  {bar}")
    except ImportError:
        print("\n(Install reference implementation to see speedup comparison)")


if __name__ == "__main__":
    main()

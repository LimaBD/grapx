"""
grapx — interactive demo
========================
Run:  python examples/demo.py

Demonstrates a technology knowledge graph with PageRank, shortest paths,
connected components, and BFS traversal — all rendered to the terminal.
"""

import sys
import time

# ── ANSI colours ──────────────────────────────────────────────────────────────
RED  = "\033[31m"   # red
GRN  = "\033[32m"   # green
YLW  = "\033[33m"   # yellow
BLU  = "\033[34m"   # blue
MAG  = "\033[35m"   # magenta
CYN  = "\033[36m"   # cyan
WHT  = "\033[37m"   # white
BD   = "\033[1m"    # bold
DIM  = "\033[2m"    # dim
RST  = "\033[0m"    # reset


def header(title: str) -> None:
    width = 60
    print()
    print(f"{BD}{CYN}{'─' * width}{RST}")
    print(f"{BD}{CYN}  {title}{RST}")
    print(f"{BD}{CYN}{'─' * width}{RST}")


def bar(value: float, max_val: float, width: int = 30, colour: str = GRN) -> str:
    filled = int(round(value / max_val * width))
    return f"{colour}{'█' * filled}{DIM}{'░' * (width - filled)}{RST}"


def pause() -> None:
    print()
    try:
        input(f"  {DIM}[ press Enter to continue ]{RST}")
    except EOFError:
        pass


# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    print(f"\n{BD}{YLW}  ⚡  grapx  —  technology knowledge graph demo{RST}\n")
    time.sleep(0.4)

    import grapx as gx

    print(f"  {GRN}✓{RST}  grapx {gx.__version__} imported  "
          f"{DIM}(Rust core: {gx.__name__}._core){RST}")

    # ── 1. BUILD GRAPH ────────────────────────────────────────────────────────
    header("1 / 6   Building the knowledge graph")

    edges = [
        # Python ecosystem
        ("Python",       "CPython",        "implemented_in"),
        ("Python",       "PyPy",           "implemented_in"),
        ("Python",       "NumPy",          "uses"),
        ("Python",       "Pandas",         "uses"),
        ("Python",       "grapx",          "uses"),
        ("Python",       "PyTorch",        "uses"),
        # Rust ecosystem
        ("Rust",         "grapx",          "powers"),
        ("Rust",         "PyO3",           "enables"),
        ("PyO3",         "grapx",          "builds"),
        ("Rust",         "WebAssembly",    "compiles_to"),
        ("Rust",         "tokio",          "async_runtime"),
        # AI / ML
        ("PyTorch",      "LLM",            "trains"),
        ("NumPy",        "PyTorch",        "underpins"),
        ("Pandas",       "NumPy",          "uses"),
        ("LLM",          "Knowledge Graph","needs"),
        ("Knowledge Graph", "grapx",       "powered_by"),
        ("grapx",        "PageRank",       "implements"),
        ("grapx",        "Dijkstra",       "implements"),
        # C / systems
        ("C",            "Python",         "inspired"),
        ("C",            "Rust",           "influenced"),
        ("CPython",      "C",              "written_in"),
        # Disconnected island (to show components)
        ("Docker",       "Kubernetes",     "orchestrated_by"),
        ("Kubernetes",   "Helm",           "managed_by"),
    ]

    t0 = time.perf_counter()
    G = gx.DiGraph()
    for src, dst, rel in edges:
        G.add_edge(src, dst, relation=rel, weight=1.0)
    elapsed = (time.perf_counter() - t0) * 1000

    nodes = G.number_of_nodes()
    edg   = G.number_of_edges()
    print(f"\n  Nodes : {BD}{nodes}{RST}")
    print(f"  Edges : {BD}{edg}{RST}")
    print(f"  Built in {elapsed:.3f} ms")

    print(f"\n  {DIM}Sample edges:{RST}")
    for src, dst, rel in edges[:6]:
        print(f"    {CYN}{src:20}{RST} ──{YLW}{rel:>20}{RST}──▶  {MAG}{dst}{RST}")
    print(f"    {DIM}… and {edg - 6} more{RST}")

    pause()

    # ── 2. PAGERANK ───────────────────────────────────────────────────────────
    header("2 / 6   PageRank  (α = 0.85)")

    t0 = time.perf_counter()
    pr = gx.pagerank(G, alpha=0.85, max_iter=100)
    elapsed = (time.perf_counter() - t0) * 1000

    ranked = sorted(pr.items(), key=lambda x: -x[1])
    top_n  = 10
    max_pr = ranked[0][1]

    print(f"\n  Top {top_n} most influential nodes  {DIM}({elapsed:.2f} ms){RST}\n")
    colours = [YLW, YLW, YLW, GRN, GRN, GRN, WHT, WHT, WHT, WHT]
    for i, (node, score) in enumerate(ranked[:top_n]):
        b = bar(score, max_pr, width=25, colour=colours[i])
        print(f"  {BD}{i+1:2}.{RST} {node:22} {b}  {DIM}{score:.4f}{RST}")

    pause()

    # ── 3. SHORTEST PATH ─────────────────────────────────────────────────────
    header("3 / 6   Shortest paths")

    pairs = [
        ("C",       "grapx"),
        ("Python",  "PageRank"),
        ("NumPy",   "Knowledge Graph"),
        ("PyTorch", "Dijkstra"),
    ]

    for src, dst in pairs:
        try:
            t0   = time.perf_counter()
            path = gx.shortest_path(G, src, dst)
            ms   = (time.perf_counter() - t0) * 1000
            pretty = f" {DIM}──▶{RST} ".join(
                f"{CYN if i == 0 else (MAG if i == len(path)-1 else WHT)}{n}{RST}"
                for i, n in enumerate(path)
            )
            print(f"\n  {pretty}")
            print(f"  {DIM}  length {len(path)-1} hop(s)  ·  {ms:.3f} ms{RST}")
        except Exception as e:
            print(f"\n  {RED}No path  {src} → {dst}:  {e}{RST}")

    pause()

    # ── 4. CONNECTED COMPONENTS ───────────────────────────────────────────────
    header("4 / 6   Weakly connected components")

    t0     = time.perf_counter()
    comps  = list(gx.weakly_connected_components(G))
    elapsed= (time.perf_counter() - t0) * 1000
    comps.sort(key=len, reverse=True)

    print(f"\n  Found {BD}{len(comps)}{RST} component(s)  {DIM}({elapsed:.3f} ms){RST}\n")
    comp_colours = [GRN, YLW, MAG, CYN, BLU]
    for i, comp in enumerate(comps):
        col   = comp_colours[i % len(comp_colours)]
        nodes_str = ", ".join(sorted(comp))
        print(f"  {col}Component {i+1}{RST}  ({len(comp)} node{'s' if len(comp)>1 else ''})")
        # wrap long node lists
        line, parts = "", sorted(comp)
        lines = []
        for p in parts:
            if len(line) + len(p) + 2 > 55:
                lines.append(line)
                line = p
            else:
                line = (line + ", " + p).lstrip(", ")
        if line:
            lines.append(line)
        for l in lines:
            print(f"    {DIM}{l}{RST}")
        print()

    pause()

    # ── 5. BFS TRAVERSAL ─────────────────────────────────────────────────────
    header("5 / 6   BFS traversal from 'Python'")

    t0   = time.perf_counter()
    tree = gx.bfs_tree(G, "Python")
    ms   = (time.perf_counter() - t0) * 1000

    # Build depth map via BFS edges
    depth = {"Python": 0}
    for u, v in gx.bfs_edges(G, "Python"):
        depth[v] = depth.get(u, 0) + 1

    max_depth = max(depth.values()) if depth else 0
    print(f"\n  BFS from {CYN}Python{RST}  ·  {BD}{len(depth)}{RST} reachable nodes"
          f"  ·  max depth {max_depth}  {DIM}({ms:.3f} ms){RST}\n")

    for d in range(min(max_depth + 1, 5)):
        at_depth = sorted(n for n, dd in depth.items() if dd == d)
        indent   = "    " + "  " * d
        col      = [CYN, YLW, GRN, MAG, WHT][d % 5]
        prefix   = f"depth {d}" if d == 0 else f"      {d}"
        print(f"  {DIM}{prefix}{RST}  {indent}", end="")
        print("  ".join(f"{col}{n}{RST}" for n in at_depth))

    if max_depth >= 5:
        print(f"  {DIM}  … (deeper nodes omitted){RST}")

    pause()

    # ── 6. DEGREE CENTRALITY ─────────────────────────────────────────────────
    header("6 / 6   Degree centrality")

    t0  = time.perf_counter()
    dc  = gx.degree_centrality(G)
    ms  = (time.perf_counter() - t0) * 1000

    top_dc  = sorted(dc.items(), key=lambda x: -x[1])[:8]
    max_dc  = top_dc[0][1]

    print(f"\n  {DIM}({ms:.3f} ms){RST}\n")
    for node, score in top_dc:
        b = bar(score, max_dc, width=25, colour=CYN)
        print(f"  {node:22} {b}  {DIM}{score:.4f}{RST}")

    pause()

    # ── SUMMARY ───────────────────────────────────────────────────────────────
    print(f"\n{BD}{GRN}  ✓  Demo complete!{RST}\n")
    print(f"  {DIM}Algorithms demonstrated:{RST}")
    for algo in ["gx.DiGraph / add_edge", "gx.pagerank(G)",
                 "gx.shortest_path(G, src, dst)",
                 "gx.weakly_connected_components(G)",
                 "gx.bfs_tree / bfs_edges",
                 "gx.degree_centrality(G)"]:
        print(f"    {GRN}•{RST}  {algo}")
    print()
    print(f"  {DIM}Start building:{RST}")
    print(f"    {YLW}import grapx as gx{RST}")
    print(f"    {YLW}G = gx.DiGraph(){RST}")
    print(f"    {YLW}G.add_edge('you', 'fast graph', weight=1.0){RST}")
    print()


if __name__ == "__main__":
    # Disable colours when piped
    if not sys.stdout.isatty():
        for name in ["RED","GRN","YLW","BLU","MAG","CYN","WHT","BD","DIM","RST"]:
            globals()[name] = ""
    main()

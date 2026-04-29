"""
grapx example — Social Network Analysis
========================================
Run:  python examples/social_network.py

Demonstrates a complete social network analysis workflow:
  • Build a social graph from employee data
  • Identify influencers using PageRank and degree centrality
  • Find team clusters using connected components
  • Analyse information flow using BFS and shortest paths
  • Detect bottleneck people using betweenness centrality
  • Export the results to an edge list file
"""

import io
import time

import grapx as gx

# ── Helpers ────────────────────────────────────────────────────────────────────

def section(title: str) -> None:
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}")


def timing(label: str, elapsed_ms: float) -> None:
    print(f"  ⏱  {label}: {elapsed_ms:.2f} ms")


# ── Dataset ────────────────────────────────────────────────────────────────────
# Fictional company with cross-team collaboration edges.
# Each edge (A, B) means "A has collaborated with B".

EMPLOYEES = [
    # (name, team, seniority)
    ("Alice",   "Engineering",  "senior"),
    ("Bob",     "Engineering",  "mid"),
    ("Carol",   "Engineering",  "junior"),
    ("Dave",    "Product",      "senior"),
    ("Eve",     "Product",      "mid"),
    ("Frank",   "Design",       "senior"),
    ("Grace",   "Design",       "junior"),
    ("Heidi",   "Marketing",    "senior"),
    ("Ivan",    "Marketing",    "mid"),
    ("Judy",    "Engineering",  "mid"),
    ("Karl",    "Data Science", "senior"),
    ("Lena",    "Data Science", "mid"),
    ("Mallory", "Data Science", "junior"),
    ("Nick",    "Product",      "junior"),
    ("Olivia",  "Design",       "mid"),
]

COLLABORATIONS = [
    # Within Engineering
    ("Alice", "Bob"),
    ("Alice", "Carol"),
    ("Bob",   "Judy"),
    ("Carol", "Judy"),
    # Engineering ↔ Product (Alice is a bridge)
    ("Alice", "Dave"),
    ("Alice", "Eve"),
    ("Bob",   "Nick"),
    # Product ↔ Design (Dave is a bridge)
    ("Dave",  "Frank"),
    ("Dave",  "Olivia"),
    ("Eve",   "Grace"),
    ("Nick",  "Grace"),
    # Design ↔ Marketing
    ("Frank", "Heidi"),
    ("Olivia","Ivan"),
    # Engineering ↔ Data Science (Karl is a bridge)
    ("Karl",  "Alice"),
    ("Karl",  "Judy"),
    ("Lena",  "Bob"),
    ("Lena",  "Mallory"),
    # Data Science ↔ Product
    ("Karl",  "Dave"),
    ("Lena",  "Eve"),
    # Marketing is relatively isolated
    ("Heidi", "Ivan"),
]

# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n⚡  grapx — Social Network Analysis\n")

    # ── 1. BUILD THE GRAPH ────────────────────────────────────────────────────
    section("1.  Building the collaboration graph")

    G = gx.Graph()

    # Add nodes with metadata
    for name, team, seniority in EMPLOYEES:
        G.add_node(name, team=team, seniority=seniority)

    # Add edges
    t0 = time.perf_counter()
    G.add_edges_from(COLLABORATIONS)
    build_ms = (time.perf_counter() - t0) * 1000

    print(f"\n  Employees (nodes) : {G.number_of_nodes()}")
    print(f"  Collaborations    : {G.number_of_edges()}")
    timing("Graph construction", build_ms)

    # ── 2. IDENTIFY INFLUENCERS ───────────────────────────────────────────────
    section("2.  Identifying influencers")

    t0 = time.perf_counter()
    pr = gx.pagerank(G, alpha=0.85)
    pr_ms = (time.perf_counter() - t0) * 1000

    dc = gx.degree_centrality(G)
    top_pr = sorted(pr, key=pr.get, reverse=True)[:5]

    print(f"\n  Top 5 by PageRank (most influential cross-team connectors):\n")
    for i, name in enumerate(top_pr, 1):
        team = G.nodes[name]["team"]
        connections = G.degree[name]
        print(
            f"    {i}. {name:<10}  team={team:<15} "
            f"| PageRank={pr[name]:.4f}  "
            f"| degree={connections}"
        )

    timing("PageRank", pr_ms)

    # Write PageRank scores back onto the graph
    for name, score in pr.items():
        G.nodes[name]["pagerank"] = round(score, 6)

    # ── 3. BETWEENNESS — FIND BOTTLENECKS ────────────────────────────────────
    section("3.  Betweenness centrality — who are the brokers?")

    t0 = time.perf_counter()
    bc = gx.betweenness_centrality(G, normalized=True)
    bc_ms = (time.perf_counter() - t0) * 1000

    top_bc = sorted(bc, key=bc.get, reverse=True)[:5]

    print(f"\n  Top 5 betweenness ('bottleneck' people — removing them hurts flow):\n")
    for i, name in enumerate(top_bc, 1):
        team = G.nodes[name]["team"]
        print(
            f"    {i}. {name:<10}  team={team:<15} "
            f"| betweenness={bc[name]:.4f}"
        )

    timing("Betweenness centrality", bc_ms)

    # ── 4. TEAM CLUSTERS ─────────────────────────────────────────────────────
    section("4.  Team cluster analysis (connected components)")

    components = sorted(gx.connected_components(G), key=len, reverse=True)
    print(f"\n  Connected components: {len(components)}\n")

    for i, comp in enumerate(components, 1):
        teams_in_comp = {G.nodes[n]["team"] for n in comp}
        print(
            f"  Component {i}: {len(comp)} people — "
            f"teams: {', '.join(sorted(teams_in_comp))}"
        )
        if len(comp) <= 8:
            print(f"    Members: {', '.join(sorted(comp))}")

    # Is the company well-connected?
    if gx.is_connected(G):
        print("\n  ✓  The whole company forms a single connected network.")
    else:
        print(f"\n  ⚠  There are isolated groups — {len(components)} separate clusters.")

    # ── 5. INFORMATION FLOW — SHORTEST PATHS ─────────────────────────────────
    section("5.  Information flow — shortest paths")

    pairs = [
        ("Carol",   "Heidi"),
        ("Mallory", "Grace"),
        ("Ivan",    "Judy"),
        ("Nick",    "Karl"),
    ]

    print()
    for src, tgt in pairs:
        if gx.has_path(G, src, tgt):
            path = gx.shortest_path(G, src, tgt)
            hops = len(path) - 1
            route = " → ".join(path)
            print(f"  {src:8} → {tgt:8}  [{hops} hop(s)]  {route}")
        else:
            print(f"  {src} → {tgt}  [unreachable]")

    # ── 6. NEIGHBOURHOOD EXPLORATION ─────────────────────────────────────────
    section("6.  2-hop neighbourhood of Alice")

    alice_node = "Alice"
    alice_2hop = {alice_node}
    for _, neighbour in gx.bfs_edges(G, alice_node, depth_limit=2):
        alice_2hop.add(neighbour)

    alice_2hop.discard(alice_node)
    print(f"\n  People reachable from Alice within 2 hops: {len(alice_2hop)}")
    teams = {}
    for n in alice_2hop:
        t = G.nodes[n]["team"]
        teams.setdefault(t, []).append(n)

    for team, members in sorted(teams.items()):
        print(f"    {team:<18} {', '.join(sorted(members))}")

    # ── 7. CLOSENESS CENTRALITY ───────────────────────────────────────────────
    section("7.  Closeness centrality — who can spread info fastest?")

    cc = gx.closeness_centrality(G)
    top_cc = sorted(cc, key=cc.get, reverse=True)[:5]

    print(f"\n  Top 5 by closeness centrality:\n")
    for i, name in enumerate(top_cc, 1):
        team = G.nodes[name]["team"]
        print(
            f"    {i}. {name:<10}  team={team:<15} "
            f"| closeness={cc[name]:.4f}"
        )

    # ── 8. EXPORT ─────────────────────────────────────────────────────────────
    section("8.  Exporting graph to edge list")

    buf = io.StringIO()
    gx.write_edgelist(G, buf, data=False)
    lines = buf.getvalue().strip().splitlines()
    print(f"\n  Edge list ({len(lines)} lines, first 5 shown):")
    for line in lines[:5]:
        print(f"    {line}")
    print(f"    ...")

    print("\n  (Use gx.write_edgelist(G, 'team.txt') to save to disk.)")

    # ── SUMMARY ───────────────────────────────────────────────────────────────
    section("Summary")

    top_influencer = top_pr[0]
    top_broker     = top_bc[0]
    top_central    = top_cc[0]

    print(f"""
  Graph: {G.number_of_nodes()} employees · {G.number_of_edges()} collaborations

  Most influential (PageRank)      : {top_influencer}
  Biggest bottleneck (betweenness) : {top_broker}
  Fastest info spreader (closeness): {top_central}
""")


if __name__ == "__main__":
    main()

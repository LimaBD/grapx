"""
grapx example — Knowledge Graph / GraphRAG
===========================================
Run:  python examples/knowledge_graph.py

Demonstrates how to build and query a knowledge graph — the kind of structure
that powers RAG (Retrieval-Augmented Generation) pipelines, semantic search,
and LLM reasoning.

The example models a technology domain: languages, frameworks, companies,
and concepts — all connected by typed relationships.

Topics covered:
  • Building a directed typed-edge knowledge graph
  • PageRank to find the most important entities
  • Shortest-path reasoning ("how is concept A related to B?")
  • Subgraph extraction for focused context windows (GraphRAG)
  • Weakly-connected-component analysis to find isolated knowledge islands
  • Condensation to reveal high-level domain structure
  • Serialising triples to an edge list for downstream tools
"""

import io
import time

import grapx as gx

# ── Helpers ────────────────────────────────────────────────────────────────────

def section(title: str) -> None:
    print(f"\n{'═' * 65}")
    print(f"  {title}")
    print(f"{'═' * 65}")


def timing(label: str, elapsed_ms: float) -> None:
    print(f"  ⏱  {label}: {elapsed_ms:.3f} ms")


# ── Knowledge graph triples ─────────────────────────────────────────────────
# Format: (subject, object, relation)
# Relations are stored as edge attributes — the graph topology only tracks
# which entities are related; the relation type lives in Python dict attrs.

TRIPLES = [
    # ── Languages ────────────────────────────────────────────────────────────
    ("Python",       "Guido van Rossum",  "created_by"),
    ("Python",       "CPython",           "implemented_as"),
    ("Python",       "PyPy",              "alternative_impl"),
    ("Python",       "GIL",               "limited_by"),
    ("Python",       "C",                 "FFI_with"),
    ("Rust",         "Mozilla",           "created_by"),
    ("Rust",         "Memory Safety",     "guarantees"),
    ("Rust",         "WebAssembly",       "compiles_to"),
    ("Rust",         "C",                 "interops_with"),
    ("C",            "Unix",              "built"),
    ("C",            "Linux",             "influenced"),
    ("Java",         "JVM",               "runs_on"),
    ("Java",         "Oracle",            "owned_by"),
    ("JavaScript",   "Node.js",           "runs_on"),
    ("TypeScript",   "JavaScript",        "compiles_to"),
    ("TypeScript",   "Microsoft",         "created_by"),
    # ── Frameworks / Libraries ────────────────────────────────────────────────
    ("PyTorch",      "Python",            "uses"),
    ("PyTorch",      "CUDA",              "accelerated_by"),
    ("PyTorch",      "Meta",              "developed_by"),
    ("TensorFlow",   "Python",            "uses"),
    ("TensorFlow",   "Google",            "developed_by"),
    ("TensorFlow",   "CUDA",              "accelerated_by"),
    ("NumPy",        "Python",            "used_in"),
    ("Pandas",       "NumPy",             "built_on"),
    ("Pandas",       "Python",            "used_in"),
    ("grapx",        "Python",            "used_in"),
    ("grapx",        "Rust",              "powered_by"),
    ("grapx",        "PyO3",              "uses"),
    ("PyO3",         "Rust",              "enables"),
    ("PyO3",         "Python",            "bridges"),
    ("FastAPI",      "Python",            "used_in"),
    ("FastAPI",      "Pydantic",          "uses"),
    ("Pydantic",     "Python",            "used_in"),
    ("Django",       "Python",            "used_in"),
    ("React",        "JavaScript",        "uses"),
    ("Next.js",      "React",             "extends"),
    ("Next.js",      "Node.js",           "requires"),
    # ── AI / ML Concepts ──────────────────────────────────────────────────────
    ("LLM",          "Transformer",       "based_on"),
    ("LLM",          "PyTorch",           "trained_with"),
    ("LLM",          "Knowledge Graph",   "enhanced_by"),
    ("GPT-4",        "LLM",               "instance_of"),
    ("GPT-4",        "OpenAI",            "developed_by"),
    ("Llama",        "LLM",               "instance_of"),
    ("Llama",        "Meta",              "developed_by"),
    ("RAG",          "LLM",               "augments"),
    ("RAG",          "Knowledge Graph",   "queries"),
    ("RAG",          "Vector Database",   "uses"),
    ("GraphRAG",     "RAG",               "extends"),
    ("GraphRAG",     "grapx",             "can_use"),
    ("Knowledge Graph", "grapx",          "implemented_with"),
    ("Transformer",  "Attention",         "uses"),
    ("Attention",    "NumPy",             "computed_with"),
    # ── Infrastructure ────────────────────────────────────────────────────────
    ("Docker",       "Linux",             "relies_on"),
    ("Kubernetes",   "Docker",            "orchestrates"),
    ("AWS",          "Kubernetes",        "hosts"),
    ("CUDA",         "NVIDIA",            "made_by"),
    ("Linux",        "C",                 "written_in"),
    ("Node.js",      "V8",                "uses"),
    ("V8",           "C++",               "written_in"),
    ("C++",          "C",                 "descended_from"),
    # ── Companies ─────────────────────────────────────────────────────────────
    ("Google",       "TensorFlow",        "open_sourced"),
    ("Google",       "Kubernetes",        "created"),
    ("Meta",         "PyTorch",           "open_sourced"),
    ("Meta",         "Llama",             "released"),
    ("OpenAI",       "GPT-4",             "released"),
    ("Microsoft",    "TypeScript",        "open_sourced"),
    ("Microsoft",    "Azure",             "operates"),
    ("Azure",        "Kubernetes",        "hosts"),
    # Isolated concepts (will show as a separate component)
    ("Haskell",      "Functional Programming", "embodies"),
    ("Erlang",       "Functional Programming", "embodies"),
    ("Elixir",       "Erlang",            "built_on"),
]


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n⚡  grapx — Knowledge Graph / GraphRAG Example\n")

    # ── 1. BUILD THE KNOWLEDGE GRAPH ─────────────────────────────────────────
    section("1.  Building the knowledge graph")

    t0 = time.perf_counter()
    G = gx.DiGraph()

    entity_types: dict[str, str] = {}

    for subj, obj, relation in TRIPLES:
        G.add_edge(subj, obj, relation=relation)

    build_ms = (time.perf_counter() - t0) * 1000

    print(f"\n  Entities (nodes) : {G.number_of_nodes()}")
    print(f"  Relations (edges): {G.number_of_edges()}")
    print(f"  Relation types   : {len({d['relation'] for _, _, d in G.edges(data=True)})}")
    timing("Build time", build_ms)

    print("\n  Sample triples:")
    for subj, obj, data in list(G.edges(data=True))[:6]:
        print(f"    ({subj})  ──[{data['relation']}]──▶  ({obj})")

    # ── 2. FIND THE MOST IMPORTANT ENTITIES ──────────────────────────────────
    section("2.  PageRank — most important entities")

    t0 = time.perf_counter()
    pr = gx.pagerank(G, alpha=0.85)
    pr_ms = (time.perf_counter() - t0) * 1000

    top12 = sorted(pr, key=pr.get, reverse=True)[:12]

    print(f"\n  Top 12 entities by PageRank:\n")
    for i, entity in enumerate(top12, 1):
        in_deg  = G.in_degree[entity]
        out_deg = G.out_degree[entity]
        print(
            f"    {i:2}. {entity:<28}  "
            f"PR={pr[entity]:.4f}  "
            f"in={in_deg:2}  out={out_deg:2}"
        )

    timing("PageRank", pr_ms)

    # ── 3. REASONING — RELATIONSHIP PATHS ────────────────────────────────────
    section("3.  Reasoning paths — how are concepts connected?")

    queries = [
        ("Python",    "Memory Safety"),
        ("GraphRAG",  "CUDA"),
        ("GPT-4",     "Python"),
        ("Kubernetes","Rust"),
        ("Elixir",    "Python"),   # across disconnected component!
    ]

    print()
    for src, tgt in queries:
        if not G.has_node(src) or not G.has_node(tgt):
            print(f"  {src} → {tgt}: entity not in graph")
            continue

        if gx.has_path(G, src, tgt):
            path = gx.shortest_path(G, src, tgt)

            # Reconstruct the chain with relation labels
            chain_parts = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                rel = G.get_edge_data(u, v, {}).get("relation", "?")
                chain_parts.append(f"({u}) ──[{rel}]──▶")
            chain_parts.append(f"({path[-1]})")
            chain = " ".join(chain_parts)

            print(f"  Query: {src} → {tgt}  [{len(path)-1} hop(s)]")
            print(f"    {chain}\n")
        else:
            print(f"  {src} → {tgt}: no directed path\n")

    # ── 4. SUBGRAPH EXTRACTION — GraphRAG CONTEXT WINDOW ─────────────────────
    section("4.  GraphRAG — extract context subgraph for 'LLM'")

    focus = "LLM"
    # Collect all nodes within 2 hops of the focus entity
    context_nodes = {focus}
    for _, nb in gx.bfs_edges(G, focus, depth_limit=2):
        context_nodes.add(nb)

    # Also add 1-hop predecessors (what points *to* LLM)
    context_nodes.update(G.predecessors(focus))

    sub = G.subgraph(context_nodes)

    print(f"\n  Focus entity  : {focus}")
    print(f"  Context nodes : {sub.number_of_nodes()}")
    print(f"  Context edges : {sub.number_of_edges()}")
    print(f"\n  Entities in context window:")
    for entity in sorted(context_nodes):
        print(f"    • {entity}")

    print(f"\n  PageRank within context subgraph (most central to {focus}):")
    sub_pr = gx.pagerank(sub, alpha=0.85)
    top5_sub = sorted(sub_pr, key=sub_pr.get, reverse=True)[:5]
    for entity in top5_sub:
        print(f"    {entity:<28}  PR={sub_pr[entity]:.4f}")

    # ── 5. CONNECTED COMPONENTS — KNOWLEDGE ISLANDS ──────────────────────────
    section("5.  Knowledge islands (weakly connected components)")

    wccs = sorted(gx.weakly_connected_components(G), key=len, reverse=True)

    print(f"\n  Weakly connected components: {len(wccs)}\n")
    for i, wcc in enumerate(wccs, 1):
        sample = sorted(wcc)[:5]
        sample_str = ", ".join(sample)
        if len(wcc) > 5:
            sample_str += f", … (+{len(wcc)-5} more)"
        print(f"  Island {i}: {len(wcc):3} entities  →  {sample_str}")

    # ── 6. DOMAIN STRUCTURE — SCC CONDENSATION ───────────────────────────────
    section("6.  Domain structure — strongly connected components")

    sccs = sorted(gx.strongly_connected_components(G), key=len, reverse=True)

    mutual_cycles = [s for s in sccs if len(s) > 1]
    print(f"\n  Total SCCs       : {len(sccs)}")
    print(f"  Mutual cycles    : {len(mutual_cycles)}")

    if mutual_cycles:
        print("\n  Entities with mutual relationships (cycles):")
        for scc in mutual_cycles:
            print(f"    {sorted(scc)}")
    else:
        print("\n  The graph is a DAG — no mutual dependency cycles.")

    # ── 7. EXPORT TRIPLES ─────────────────────────────────────────────────────
    section("7.  Export to edge list")

    buf = io.StringIO()
    gx.write_edgelist(G, buf, data=["relation"])
    lines = buf.getvalue().strip().splitlines()

    print(f"\n  Edge list ({len(lines)} lines; first 8 shown):")
    for line in lines[:8]:
        print(f"    {line}")
    print("    ...")

    print("\n  Tip: gx.read_edgelist('kg.txt', create_using=gx.DiGraph)")
    print("       to reload the knowledge graph from disk.\n")

    # ── SUMMARY ───────────────────────────────────────────────────────────────
    section("Summary")

    most_authoritative = top12[0]
    largest_context_pr = top5_sub[0]

    print(f"""
  Knowledge graph : {G.number_of_nodes()} entities · {G.number_of_edges()} relations

  Most authoritative entity (PageRank)   : {most_authoritative}
  Most relevant in LLM context (sub-PR)  : {largest_context_pr}
  Knowledge islands (WCCs)               : {len(wccs)}
  Mutual dependency cycles (SCCs > 1)    : {len(mutual_cycles)}

  This kind of structure powers GraphRAG pipelines:
  query → extract N-hop subgraph → feed entities + edges as LLM context
  → generated answer is grounded in graph-derived knowledge.
""")


if __name__ == "__main__":
    main()

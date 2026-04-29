"""
grapx.classes.multigraph
~~~~~~~~~~~~~~~~~~~~~~~~~
MultiGraph and MultiDiGraph — stubs that alias Graph/DiGraph in v0.1.
Full parallel-edge support scheduled for v0.2.
"""

from grapx.classes.digraph import DiGraph
from grapx.classes.graph import Graph


class MultiGraph(Graph):
    """Undirected multigraph (parallel edges not yet tracked — v0.1 alias)."""

    def is_multigraph(self) -> bool:
        return True


class MultiDiGraph(DiGraph):
    """Directed multigraph (parallel edges not yet tracked — v0.1 alias)."""

    def is_multigraph(self) -> bool:
        return True


__all__ = ["MultiGraph", "MultiDiGraph"]

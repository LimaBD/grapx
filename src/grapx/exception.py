"""
grapx.exception
~~~~~~~~~~~~~~~~
Exception hierarchy for grapx.
"""


class GrapxError(Exception):
    """Base exception class for grapx."""


# Alias for code that catches networkx exceptions by name
NetworkXError = GrapxError


class NetworkXNoPath(GrapxError):
    """Exception raised when no path exists between nodes."""


class NodeNotFound(GrapxError):
    """Exception raised when a requested node is not in the graph."""


class GrapxAlgorithmError(GrapxError):
    """Exception raised when an algorithm cannot complete."""


__all__ = [
    "GrapxError",
    "NetworkXError",
    "NetworkXNoPath",
    "NodeNotFound",
    "GrapxAlgorithmError",
]

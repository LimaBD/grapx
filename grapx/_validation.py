"""
grapx._validation
~~~~~~~~~~~~~~~~~~
Pydantic-backed parameter validation for grapx algorithms.

Users never interact with this module directly — it enforces type safety
and provides clear error messages when invalid parameters are passed.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class _BaseConfig(BaseModel):
    model_config = {"extra": "ignore", "arbitrary_types_allowed": True}


class PageRankParams(_BaseConfig):
    """Validation model for pagerank() parameters."""

    alpha: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Damping factor — probability of following an edge (0 < alpha ≤ 1)",
    )
    max_iter: int = Field(
        default=100,
        gt=0,
        description="Maximum number of power-iteration steps",
    )
    tol: float = Field(
        default=1.0e-6,
        gt=0.0,
        description="L1 convergence tolerance",
    )
    weight: Optional[str] = Field(
        default="weight",
        description="Edge attribute to use as weight (None = unweighted)",
    )


class ShortestPathParams(_BaseConfig):
    """Validation model for shortest_path() / shortest_path_length() parameters."""

    weight: Optional[str] = Field(
        default=None,
        description="Edge attribute to use as distance (None = hop count)",
    )
    method: Optional[str] = Field(
        default=None,
        description="Algorithm hint ('dijkstra' only in v0.1)",
    )

    @field_validator("method")
    @classmethod
    def method_check(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("dijkstra", "bellman-ford"):
            raise ValueError(
                f"method must be 'dijkstra' or 'bellman-ford', got {v!r}"
            )
        return v


class CentralityParams(_BaseConfig):
    """Validation model for centrality functions."""

    normalized: bool = Field(
        default=True,
        description="Whether to normalize values to [0, 1]",
    )
    weight: Optional[str] = Field(
        default=None,
        description="Edge attribute to use as weight",
    )
    endpoints: bool = Field(
        default=False,
        description="Include endpoints in betweenness counts",
    )


class EdgeWeightValidator(_BaseConfig):
    """Validates a single edge weight value."""

    weight: float = Field(description="Numeric edge weight")

    @field_validator("weight")
    @classmethod
    def must_be_finite(cls, v: float) -> float:
        import math
        if math.isnan(v) or math.isinf(v):
            raise ValueError(
                f"Edge weight must be a finite number, got {v!r}"
            )
        return v


def validate_pagerank_params(alpha, max_iter, tol, weight) -> PageRankParams:
    return PageRankParams(alpha=alpha, max_iter=max_iter, tol=tol, weight=weight)


def validate_shortest_path_params(weight, method) -> ShortestPathParams:
    return ShortestPathParams(weight=weight, method=method)


def validate_centrality_params(normalized, weight="weight", endpoints=False) -> CentralityParams:
    return CentralityParams(normalized=normalized, weight=weight, endpoints=endpoints)


__all__ = [
    "PageRankParams",
    "ShortestPathParams",
    "CentralityParams",
    "EdgeWeightValidator",
    "validate_pagerank_params",
    "validate_shortest_path_params",
    "validate_centrality_params",
]

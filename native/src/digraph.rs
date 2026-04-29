use petgraph::stable_graph::{NodeIndex, StableGraph};
use petgraph::visit::{Bfs, Dfs, EdgeRef, IntoEdgeReferences};
use petgraph::Directed;
use petgraph::Direction;
use pyo3::prelude::*;
use rayon::prelude::*;

use crate::graph::dijkstra_path;

/// Directed graph backed by petgraph StableGraph.
#[pyclass]
pub struct RustDiGraph {
    pub inner: StableGraph<u32, f64, Directed>,
}

impl Default for RustDiGraph {
    fn default() -> Self {
        Self::new()
    }
}

#[pymethods]
impl RustDiGraph {
    #[new]
    pub fn new() -> Self {
        RustDiGraph {
            inner: StableGraph::new(),
        }
    }

    pub fn add_node(&mut self) -> u32 {
        self.inner.add_node(0).index() as u32
    }

    pub fn remove_node(&mut self, idx: u32) {
        self.inner.remove_node(NodeIndex::new(idx as usize));
    }

    pub fn add_edge(&mut self, u: u32, v: u32, weight: f64) {
        let u_ni = NodeIndex::new(u as usize);
        let v_ni = NodeIndex::new(v as usize);
        if let Some(ei) = self.inner.find_edge(u_ni, v_ni) {
            // Update existing edge weight
            if let Some(w) = self.inner.edge_weight_mut(ei) {
                *w = weight;
            }
        } else {
            self.inner.add_edge(u_ni, v_ni, weight);
        }
    }

    pub fn remove_edge(&mut self, u: u32, v: u32) {
        let u_ni = NodeIndex::new(u as usize);
        let v_ni = NodeIndex::new(v as usize);
        if let Some(ei) = self.inner.find_edge(u_ni, v_ni) {
            self.inner.remove_edge(ei);
        }
    }

    pub fn has_node(&self, idx: u32) -> bool {
        self.inner.contains_node(NodeIndex::new(idx as usize))
    }

    pub fn has_edge(&self, u: u32, v: u32) -> bool {
        self.inner
            .find_edge(NodeIndex::new(u as usize), NodeIndex::new(v as usize))
            .is_some()
    }

    pub fn node_count(&self) -> usize {
        self.inner.node_count()
    }

    pub fn edge_count(&self) -> usize {
        self.inner.edge_count()
    }

    /// Outgoing neighbors (successors).
    pub fn successors(&self, idx: u32) -> Vec<u32> {
        self.inner
            .neighbors_directed(NodeIndex::new(idx as usize), Direction::Outgoing)
            .map(|n| n.index() as u32)
            .collect()
    }

    /// Incoming neighbors (predecessors).
    pub fn predecessors(&self, idx: u32) -> Vec<u32> {
        self.inner
            .neighbors_directed(NodeIndex::new(idx as usize), Direction::Incoming)
            .map(|n| n.index() as u32)
            .collect()
    }

    pub fn in_degree(&self, idx: u32) -> usize {
        self.inner
            .edges_directed(NodeIndex::new(idx as usize), Direction::Incoming)
            .count()
    }

    pub fn out_degree(&self, idx: u32) -> usize {
        self.inner
            .edges_directed(NodeIndex::new(idx as usize), Direction::Outgoing)
            .count()
    }

    /// Return all edges as (source, target, weight) tuples.
    pub fn edges(&self) -> Vec<(u32, u32, f64)> {
        self.inner
            .edge_references()
            .map(|e| {
                (
                    e.source().index() as u32,
                    e.target().index() as u32,
                    *e.weight(),
                )
            })
            .collect()
    }

    pub fn node_indices(&self) -> Vec<u32> {
        self.inner
            .node_indices()
            .map(|n| n.index() as u32)
            .collect()
    }

    pub fn bfs(&self, start: u32) -> Vec<u32> {
        let mut bfs = Bfs::new(&self.inner, NodeIndex::new(start as usize));
        let mut result = Vec::new();
        while let Some(node) = bfs.next(&self.inner) {
            result.push(node.index() as u32);
        }
        result
    }

    pub fn bfs_edges(&self, start: u32) -> Vec<(u32, u32)> {
        use std::collections::{HashSet, VecDeque};
        let start_ni = NodeIndex::new(start as usize);
        let mut visited: HashSet<usize> = HashSet::new();
        visited.insert(start as usize);
        let mut queue: VecDeque<NodeIndex> = VecDeque::new();
        queue.push_back(start_ni);
        let mut edges = Vec::new();
        while let Some(u) = queue.pop_front() {
            for v in self.inner.neighbors_directed(u, Direction::Outgoing) {
                if !visited.contains(&v.index()) {
                    visited.insert(v.index());
                    edges.push((u.index() as u32, v.index() as u32));
                    queue.push_back(v);
                }
            }
        }
        edges
    }

    pub fn dfs(&self, start: u32) -> Vec<u32> {
        let mut dfs = Dfs::new(&self.inner, NodeIndex::new(start as usize));
        let mut result = Vec::new();
        while let Some(node) = dfs.next(&self.inner) {
            result.push(node.index() as u32);
        }
        result
    }

    pub fn dfs_edges(&self, start: u32) -> Vec<(u32, u32)> {
        use std::collections::HashSet;
        let start_ni = NodeIndex::new(start as usize);
        let mut visited: HashSet<usize> = HashSet::new();
        visited.insert(start as usize);
        let mut stack: Vec<(NodeIndex, Option<NodeIndex>)> = vec![(start_ni, None)];
        let mut edges = Vec::new();
        while let Some((u, parent)) = stack.pop() {
            if let Some(p) = parent {
                edges.push((p.index() as u32, u.index() as u32));
            }
            for v in self.inner.neighbors_directed(u, Direction::Outgoing) {
                if !visited.contains(&v.index()) {
                    visited.insert(v.index());
                    stack.push((v, Some(u)));
                }
            }
        }
        edges
    }

    /// Dijkstra on directed graph (follows edge direction).
    pub fn dijkstra(&self, start: u32, end: u32) -> Option<(f64, Vec<u32>)> {
        dijkstra_path(&self.inner, start, end, true)
    }

    /// Strongly connected components (Kosaraju's algorithm).
    pub fn strongly_connected_components(&self) -> Vec<Vec<u32>> {
        let sccs = petgraph::algo::kosaraju_scc(&self.inner);
        sccs.into_iter()
            .map(|scc| scc.iter().map(|n| n.index() as u32).collect())
            .collect()
    }

    /// Weakly connected components (treat edges as undirected via DFS).
    pub fn weakly_connected_components(&self) -> Vec<Vec<u32>> {
        let mut seen: std::collections::HashSet<usize> = std::collections::HashSet::new();
        let mut components: Vec<Vec<u32>> = Vec::new();

        for start in self.inner.node_indices() {
            if seen.contains(&start.index()) {
                continue;
            }
            let mut component: Vec<u32> = Vec::new();
            let mut stack = vec![start];
            seen.insert(start.index());

            while let Some(node) = stack.pop() {
                component.push(node.index() as u32);
                // Follow edges in both directions
                for neighbor in self.inner.neighbors_directed(node, Direction::Outgoing) {
                    if !seen.contains(&neighbor.index()) {
                        seen.insert(neighbor.index());
                        stack.push(neighbor);
                    }
                }
                for neighbor in self.inner.neighbors_directed(node, Direction::Incoming) {
                    if !seen.contains(&neighbor.index()) {
                        seen.insert(neighbor.index());
                        stack.push(neighbor);
                    }
                }
            }
            components.push(component);
        }
        components
    }

    /// Check if a directed path exists from start to end (BFS).
    pub fn has_path(&self, start: u32, end: u32) -> bool {
        use std::collections::{HashSet, VecDeque};
        let start_ni = NodeIndex::new(start as usize);
        let end_ni = NodeIndex::new(end as usize);
        if !self.inner.contains_node(start_ni) || !self.inner.contains_node(end_ni) {
            return false;
        }
        if start_ni == end_ni {
            return true;
        }
        let mut visited: HashSet<usize> = HashSet::new();
        let mut queue: VecDeque<NodeIndex> = VecDeque::new();
        queue.push_back(start_ni);
        visited.insert(start as usize);
        while let Some(node) = queue.pop_front() {
            for neighbor in self.inner.neighbors_directed(node, Direction::Outgoing) {
                if neighbor == end_ni {
                    return true;
                }
                if !visited.contains(&neighbor.index()) {
                    visited.insert(neighbor.index());
                    queue.push_back(neighbor);
                }
            }
        }
        false
    }

    /// Degree centrality (out-degree based) — runs in parallel via Rayon.
    pub fn degree_centrality(&self) -> Vec<(u32, f64)> {
        let n = self.inner.node_count();
        if n <= 1 {
            return self
                .inner
                .node_indices()
                .map(|ni| (ni.index() as u32, 0.0))
                .collect();
        }
        let normalizer = (n - 1) as f64;
        let nodes: Vec<NodeIndex> = self.inner.node_indices().collect();

        nodes
            .par_iter()
            .map(|&node| {
                let deg = (self.inner.edges_directed(node, Direction::Outgoing).count()
                    + self.inner.edges_directed(node, Direction::Incoming).count())
                    as f64;
                (node.index() as u32, deg / normalizer)
            })
            .collect()
    }
}

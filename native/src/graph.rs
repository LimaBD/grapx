use petgraph::stable_graph::{NodeIndex, StableGraph};
use petgraph::visit::{Bfs, Dfs, EdgeRef, IntoEdgeReferences};
use petgraph::Undirected;
use pyo3::prelude::*;
use rayon::prelude::*;

/// Undirected graph backed by petgraph StableGraph.
/// Nodes are identified by u32 indices managed on the Python side.
/// Edges carry f64 weights; all other attributes live in Python dicts.
#[pyclass]
pub struct RustGraph {
    pub inner: StableGraph<u32, f64, Undirected>,
}

impl Default for RustGraph {
    fn default() -> Self {
        Self::new()
    }
}

#[pymethods]
impl RustGraph {
    #[new]
    pub fn new() -> Self {
        RustGraph {
            inner: StableGraph::<u32, f64, Undirected>::with_capacity(0, 0),
        }
    }

    /// Add a node and return its stable index (u32).
    pub fn add_node(&mut self) -> u32 {
        self.inner.add_node(0).index() as u32
    }

    /// Remove a node by its stable index.
    pub fn remove_node(&mut self, idx: u32) {
        self.inner.remove_node(NodeIndex::new(idx as usize));
    }

    /// Add an undirected edge. If weight is not needed pass 1.0.
    pub fn add_edge(&mut self, u: u32, v: u32, weight: f64) {
        let u_ni = NodeIndex::new(u as usize);
        let v_ni = NodeIndex::new(v as usize);
        // Avoid duplicate edges (simple graph)
        if self.inner.find_edge(u_ni, v_ni).is_none() {
            self.inner.add_edge(u_ni, v_ni, weight);
        } else {
            // Update weight of existing edge
            if let Some(ei) = self.inner.find_edge(u_ni, v_ni) {
                if let Some(w) = self.inner.edge_weight_mut(ei) {
                    *w = weight;
                }
            }
        }
    }

    /// Remove an edge between two nodes.
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

    /// Return neighbor indices for a given node.
    pub fn neighbors(&self, idx: u32) -> Vec<u32> {
        self.inner
            .neighbors(NodeIndex::new(idx as usize))
            .map(|n| n.index() as u32)
            .collect()
    }

    /// Degree of a node (number of adjacent edges).
    pub fn degree(&self, idx: u32) -> usize {
        self.inner.edges(NodeIndex::new(idx as usize)).count()
    }

    /// Return all edges as (u, v, weight) tuples.
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

    /// All node indices currently in the graph.
    pub fn node_indices(&self) -> Vec<u32> {
        self.inner
            .node_indices()
            .map(|n| n.index() as u32)
            .collect()
    }

    /// BFS starting from `start`; returns nodes in visit order.
    pub fn bfs(&self, start: u32) -> Vec<u32> {
        let mut bfs = Bfs::new(&self.inner, NodeIndex::new(start as usize));
        let mut result = Vec::new();
        while let Some(node) = bfs.next(&self.inner) {
            result.push(node.index() as u32);
        }
        result
    }

    /// BFS edges: returns (predecessor, node) pairs.
    pub fn bfs_edges(&self, start: u32) -> Vec<(u32, u32)> {
        use std::collections::{HashSet, VecDeque};
        let start_ni = NodeIndex::new(start as usize);
        let mut visited: HashSet<usize> = HashSet::new();
        visited.insert(start as usize);
        let mut queue: VecDeque<NodeIndex> = VecDeque::new();
        queue.push_back(start_ni);
        let mut edges = Vec::new();
        while let Some(u) = queue.pop_front() {
            for v in self.inner.neighbors(u) {
                if !visited.contains(&v.index()) {
                    visited.insert(v.index());
                    edges.push((u.index() as u32, v.index() as u32));
                    queue.push_back(v);
                }
            }
        }
        edges
    }

    /// DFS starting from `start`; returns nodes in visit order.
    pub fn dfs(&self, start: u32) -> Vec<u32> {
        let mut dfs = Dfs::new(&self.inner, NodeIndex::new(start as usize));
        let mut result = Vec::new();
        while let Some(node) = dfs.next(&self.inner) {
            result.push(node.index() as u32);
        }
        result
    }

    /// DFS edges: returns (predecessor, node) pairs.
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
            for v in self.inner.neighbors(u) {
                if !visited.contains(&v.index()) {
                    visited.insert(v.index());
                    stack.push((v, Some(u)));
                }
            }
        }
        edges
    }

    /// Dijkstra shortest path. Returns `None` if no path exists.
    /// Output: (total_distance, path_as_node_indices)
    pub fn dijkstra(&self, start: u32, end: u32) -> Option<(f64, Vec<u32>)> {
        dijkstra_path(&self.inner, start, end, false)
    }

    /// Connected components — each inner Vec is a set of node indices.
    pub fn connected_components(&self) -> Vec<Vec<u32>> {
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
                for neighbor in self.inner.neighbors(node) {
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

    /// Degree centrality for all nodes — runs in parallel via Rayon.
    /// Returns Vec of (node_index, centrality_score).
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
                let deg = self.inner.edges(node).count() as f64;
                (node.index() as u32, deg / normalizer)
            })
            .collect()
    }
}

// ─── Dijkstra implementation shared by both graph and digraph ────────────────

/// Generic Dijkstra that works for both undirected and directed petgraph graphs.
/// `directed = true` means only follow outgoing edges.
pub fn dijkstra_path<Ty>(
    graph: &StableGraph<u32, f64, Ty>,
    start: u32,
    end: u32,
    _directed: bool,
) -> Option<(f64, Vec<u32>)>
where
    Ty: petgraph::EdgeType,
{
    use std::cmp::Ordering;
    use std::collections::{BinaryHeap, HashMap};

    #[derive(PartialEq)]
    struct State {
        cost: f64,
        node: NodeIndex,
    }

    impl Eq for State {}

    impl Ord for State {
        fn cmp(&self, other: &Self) -> Ordering {
            other
                .cost
                .partial_cmp(&self.cost)
                .unwrap_or(Ordering::Equal)
                .then_with(|| other.node.index().cmp(&self.node.index()))
        }
    }

    impl PartialOrd for State {
        fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
            Some(self.cmp(other))
        }
    }

    let start_ni = NodeIndex::new(start as usize);
    let end_ni = NodeIndex::new(end as usize);

    // Verify nodes exist
    if !graph.contains_node(start_ni) || !graph.contains_node(end_ni) {
        return None;
    }

    let mut dist: HashMap<NodeIndex, f64> = HashMap::new();
    let mut prev: HashMap<NodeIndex, NodeIndex> = HashMap::new();
    let mut heap: BinaryHeap<State> = BinaryHeap::new();

    dist.insert(start_ni, 0.0);
    heap.push(State {
        cost: 0.0,
        node: start_ni,
    });

    while let Some(State { cost, node: u }) = heap.pop() {
        if u == end_ni {
            // Reconstruct path
            let mut path = Vec::new();
            let mut current = end_ni;
            loop {
                path.push(current.index() as u32);
                if current == start_ni {
                    break;
                }
                match prev.get(&current) {
                    Some(&p) => current = p,
                    None => return None,
                }
            }
            path.reverse();
            return Some((cost, path));
        }

        if dist.get(&u).is_none_or(|&d| cost > d + 1e-10) {
            continue;
        }

        for edge in graph.edges(u) {
            let v = edge.target();
            let w = *edge.weight();
            let new_cost = cost + w;

            if new_cost < *dist.get(&v).unwrap_or(&f64::INFINITY) {
                dist.insert(v, new_cost);
                prev.insert(v, u);
                heap.push(State {
                    cost: new_cost,
                    node: v,
                });
            }
        }
    }

    None
}

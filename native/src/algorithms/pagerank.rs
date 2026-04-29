use petgraph::stable_graph::{NodeIndex, StableGraph};
use petgraph::visit::EdgeRef;
use petgraph::EdgeType;
use rayon::prelude::*;

/// PageRank with parallel Rayon iteration.
///
/// Works for any petgraph `StableGraph` (both directed and undirected).
/// For undirected graphs, each undirected edge is treated as bidirectional.
pub fn pagerank_parallel<Ty: EdgeType + Sync>(
    graph: &StableGraph<u32, f64, Ty>,
    alpha: f64,
    max_iter: usize,
    tol: f64,
) -> Vec<(u32, f64)> {
    let n = graph.node_count();
    if n == 0 {
        return vec![];
    }

    // Collect all node indices in order
    let nodes: Vec<NodeIndex> = graph.node_indices().collect();
    let node_to_pos: std::collections::HashMap<usize, usize> = nodes
        .iter()
        .enumerate()
        .map(|(pos, ni)| (ni.index(), pos))
        .collect();

    // Pre-compute out-degrees (sum of outgoing edge weights)
    let out_weights: Vec<f64> = nodes
        .iter()
        .map(|&ni| graph.edges(ni).map(|e| *e.weight()).sum::<f64>())
        .collect();

    // Pre-compute weighted incoming contributions: for each node i, store (src_pos, weight/out_weight)
    let incoming: Vec<Vec<(usize, f64)>> = nodes
        .iter()
        .map(|&ni| {
            use petgraph::Direction;
            // For directed: edges pointing *to* ni. For undirected this is the same as edges(ni).
            graph
                .edges_directed(ni, Direction::Incoming)
                .filter_map(|e| {
                    let src = e.source();
                    let src_pos = *node_to_pos.get(&src.index())?;
                    let w = *e.weight();
                    let total_out = out_weights[src_pos];
                    if total_out > 0.0 {
                        Some((src_pos, w / total_out))
                    } else {
                        None
                    }
                })
                .collect()
        })
        .collect();

    let mut ranks: Vec<f64> = vec![1.0 / n as f64; n];
    let mut new_ranks: Vec<f64> = vec![0.0; n];

    for _iter in 0..max_iter {
        // Dangling nodes: nodes with zero out-weight contribute uniformly
        let dangling_sum: f64 = nodes
            .iter()
            .enumerate()
            .filter(|(pos, _)| out_weights[*pos] == 0.0)
            .map(|(pos, _)| ranks[pos])
            .sum::<f64>()
            / n as f64;

        let base = (1.0 - alpha) / n as f64 + alpha * dangling_sum;

        new_ranks.par_iter_mut().enumerate().for_each(|(i, rank)| {
            let contribution: f64 = incoming[i]
                .iter()
                .map(|&(src_pos, ratio)| alpha * ranks[src_pos] * ratio)
                .sum();
            *rank = base + contribution;
        });

        // Convergence check
        let err: f64 = ranks
            .iter()
            .zip(new_ranks.iter())
            .map(|(a, b)| (a - b).abs())
            .sum();

        std::mem::swap(&mut ranks, &mut new_ranks);

        if err < tol {
            break;
        }
    }

    nodes
        .iter()
        .enumerate()
        .map(|(pos, ni)| (ni.index() as u32, ranks[pos]))
        .collect()
}

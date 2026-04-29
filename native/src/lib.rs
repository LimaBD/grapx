use pyo3::prelude::*;

mod algorithms;
mod digraph;
mod graph;

use digraph::RustDiGraph;
use graph::RustGraph;

/// PageRank on an undirected graph.
#[pyfunction]
fn pagerank_graph(
    g: &Bound<'_, RustGraph>,
    alpha: f64,
    max_iter: usize,
    tol: f64,
) -> Vec<(u32, f64)> {
    algorithms::pagerank::pagerank_parallel(&g.borrow().inner, alpha, max_iter, tol)
}

/// PageRank on a directed graph.
#[pyfunction]
fn pagerank_digraph(
    g: &Bound<'_, RustDiGraph>,
    alpha: f64,
    max_iter: usize,
    tol: f64,
) -> Vec<(u32, f64)> {
    algorithms::pagerank::pagerank_parallel(&g.borrow().inner, alpha, max_iter, tol)
}

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RustGraph>()?;
    m.add_class::<RustDiGraph>()?;
    m.add_function(wrap_pyfunction!(pagerank_graph, m)?)?;
    m.add_function(wrap_pyfunction!(pagerank_digraph, m)?)?;
    Ok(())
}

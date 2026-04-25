"""Сборка и компиляция LangGraph workflow для AML-пайплайна."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from aml_agent.graph import nodes
from aml_agent.utils.types import AMLState


def build_workflow():
    """Создает граф этапов: ingestion -> ... -> audit -> END."""

    graph = StateGraph(AMLState)

    graph.add_node("ingestion", nodes.ingestion_node)
    graph.add_node("normalization", nodes.normalization_node)
    graph.add_node("validation", nodes.validation_node)
    graph.add_node("feature_engineering", nodes.feature_engineering_node)
    graph.add_node("clustering", nodes.clustering_node)
    graph.add_node("isolation_forest", nodes.isolation_forest_node)
    graph.add_node("sampling", nodes.sampling_node)
    graph.add_node("routing", nodes.routing_node)
    graph.add_node("low_risk_reviewer", nodes.low_risk_reviewer_node)
    graph.add_node("investigator", nodes.investigator_node)
    graph.add_node("finalizer", nodes.finalizer_node)
    graph.add_node("empty_values_validator", nodes.empty_values_validator_node)
    graph.add_node("repair_finalizer", nodes.repair_finalizer_node)
    graph.add_node("propagation", nodes.propagation_node)
    graph.add_node("post_propagation_validator", nodes.post_propagation_validator_node)
    graph.add_node("repair_propagated_rows", nodes.repair_propagated_rows_node)
    graph.add_node("suspicious_db_write", nodes.suspicious_db_write_node)
    graph.add_node("audit_log", nodes.audit_log_node)

    graph.add_edge(START, "ingestion")
    graph.add_edge("ingestion", "normalization")
    graph.add_edge("normalization", "validation")
    graph.add_edge("validation", "feature_engineering")
    graph.add_edge("feature_engineering", "clustering")
    graph.add_edge("clustering", "isolation_forest")
    graph.add_edge("isolation_forest", "sampling")
    graph.add_edge("sampling", "routing")
    graph.add_edge("routing", "low_risk_reviewer")
    graph.add_edge("low_risk_reviewer", "investigator")
    graph.add_edge("investigator", "finalizer")
    graph.add_edge("finalizer", "empty_values_validator")
    graph.add_edge("empty_values_validator", "repair_finalizer")
    graph.add_edge("repair_finalizer", "propagation")
    graph.add_edge("propagation", "post_propagation_validator")
    graph.add_edge("post_propagation_validator", "repair_propagated_rows")
    graph.add_edge("repair_propagated_rows", "suspicious_db_write")
    graph.add_edge("suspicious_db_write", "audit_log")
    graph.add_edge("audit_log", END)

    return graph.compile()

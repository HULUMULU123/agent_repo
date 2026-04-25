"""LangGraph-ноды AML-пайплайна: от ingestion до audit log."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from aml_agent.features.amount_time_features import build_amount_time_features
from aml_agent.features.clustering import cluster_purposes
from aml_agent.features.isolation_forest import apply_isolation_forest
from aml_agent.features.propagation import propagate_decisions
from aml_agent.features.purpose_embeddings import PurposeEmbedder
from aml_agent.features.sampling import representative_sampling
from aml_agent.ingestion.extractors import extract_operations
from aml_agent.ingestion.normalizer import normalize_operations
from aml_agent.ingestion.validators import validate_rows
from aml_agent.storage.database import upsert_suspicious, write_audit_rows
from aml_agent.tools import investigator_tools
from aml_agent.utils.types import AMLState


def ingestion_node(state: AMLState) -> AMLState:
    """Вход: input_path. Выход: operations (raw). Роль: загрузка документа."""

    state["operations"] = extract_operations(state["input_path"])
    state["processing_started_at"] = datetime.utcnow().isoformat()
    return state


def normalization_node(state: AMLState) -> AMLState:
    """Вход: operations raw. Выход: operations normalized."""

    state["operations"] = normalize_operations(state.get("operations", []))
    return state


def validation_node(state: AMLState) -> AMLState:
    """Вход: operations normalized. Выход: valid operations + manual_review_rows."""

    valid, manual = validate_rows(state.get("operations", []))
    state["operations"] = valid
    state["manual_review_rows"] = manual
    return state


def feature_engineering_node(state: AMLState) -> AMLState:
    """Вход: operations. Выход: operations + числовые признаки."""

    state["operations"] = build_amount_time_features(state.get("operations", []))
    return state


def clustering_node(state: AMLState) -> AMLState:
    """Вход: operations. Выход: operations + кластерные признаки purpose."""

    ops = state.get("operations", [])
    embedder = PurposeEmbedder()
    emb = embedder.fit_transform([o.get("purpose", "") for o in ops]) if ops else []
    state["operations"] = cluster_purposes(ops, emb) if len(ops) else ops
    return state


def isolation_forest_node(state: AMLState) -> AMLState:
    """Вход: operations + features. Выход: operations + iso_score/rank/anomaly."""

    state["operations"] = apply_isolation_forest(state.get("operations", []))
    return state


def sampling_node(state: AMLState) -> AMLState:
    """Вход: operations full. Выход: sampled_operations (representative set)."""

    state["sampled_operations"] = representative_sampling(state.get("operations", []))
    return state


def routing_node(state: AMLState) -> AMLState:
    """Вход: sampled_operations. Выход: low_risk_operations/high_risk_operations."""

    sampled = state.get("sampled_operations", [])
    low, high = [], []
    for op in sampled:
        (high if op.get("iso_rank", 0) > 0.8 else low).append(op)
    state["low_risk_operations"] = low
    state["high_risk_operations"] = high
    return state


def low_risk_reviewer_node(state: AMLState) -> AMLState:
    """Вход: low_risk_operations. Выход: возможно эскалированные операции в high risk."""

    escalated = []
    retained = []
    for op in state.get("low_risk_operations", []):
        if op.get("court_proximity", 0) == 1 and op.get("abs_amount", 0) > 100000:
            escalated.append(op)
        else:
            retained.append(op)
    state["low_risk_operations"] = retained
    state["high_risk_operations"] = state.get("high_risk_operations", []) + escalated
    return state


def investigator_node(state: AMLState) -> AMLState:
    """Вход: high_risk_operations. Выход: evidence_ledger на основе tools."""

    ledger = state.get("evidence_ledger", [])
    available_tools = investigator_tools.get_investigator_tools()
    state["investigator_tools_catalog"] = investigator_tools.render_tools_catalog()
    tool_map = {t.name: t for t in available_tools}
    for op in state.get("high_risk_operations", []):
        cp = op.get("counterparty", "")
        tool_calls = [
            tool_map["spark_interfax_lookup"].invoke(cp),
            tool_map["graph_relations_lookup"].invoke(cp),
            tool_map["lookup_suspicious_counterparty"].invoke(cp),
            tool_map["search_suspicious_counterparties"].invoke(cp),
            tool_map["get_historical_client_profile"].invoke(op.get("client", "")),
            tool_map["get_historical_client_counterparty_profile"].invoke(
                {"client": op.get("client", ""), "counterparty": cp}
            ),
            tool_map["search_normative_base"].invoke(op.get("purpose", "")),
        ]
        for t in tool_calls:
            ledger.append(
                {
                    "evidence_id": str(uuid4()),
                    "operation_id": op["operation_id"],
                    "source": t.get("source", "tool"),
                    "fact": str(t),
                    "confidence": 0.6,
                    "supports_risk": bool(op.get("iso_rank", 0) > 0.8),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
    state["evidence_ledger"] = ledger
    return state


def finalizer_node(state: AMLState) -> AMLState:
    """Вход: routed ops + evidence. Выход: final_decisions (строгая схема)."""

    decisions = []
    for op in state.get("sampled_operations", []):
        high = op in state.get("high_risk_operations", [])
        risk_level = "high" if high else ("medium" if op.get("iso_rank", 0) > 0.6 else "low")
        risk_score = float(op.get("iso_rank", 0))
        decisions.append(
            {
                "operation_id": op["operation_id"],
                "cluster_id": int(op.get("cluster_id", -1)),
                "risk_level": risk_level,
                "risk_score": risk_score,
                "decision": "suspicious" if risk_level in {"high", "medium"} else "clear",
                "reason": "Anomaly and contextual checks",
                "evidence_summary": f"Evidence count: {len(state.get('evidence_ledger', []))}",
                "used_tools": [x["name"] for x in state.get("investigator_tools_catalog", [])] if high else [],
                "recommended_action": "manual_investigation" if risk_level == "high" else "monitor",
                "can_propagate": risk_level != "low",
                "propagation_rules": {"within_cluster": True, "threshold": 0.75},
            }
        )
    state["final_decisions"] = decisions
    return state


def empty_values_validator_node(state: AMLState) -> AMLState:
    """Вход: final_decisions. Выход: флаг необходимости repair по пустым полям."""

    needs_repair = False
    for d in state.get("final_decisions", []):
        for key in ["operation_id", "risk_level", "decision", "reason"]:
            if d.get(key) in (None, ""):
                needs_repair = True
    state["needs_repair"] = needs_repair
    return state


def repair_finalizer_node(state: AMLState) -> AMLState:
    """Вход: final_decisions c пропусками. Выход: мягко repaired final_decisions."""

    if not state.get("needs_repair"):
        return state
    for d in state.get("final_decisions", []):
        d.setdefault("reason", "Недостаточно данных, требуется ручная проверка")
        d.setdefault("decision", "manual_review")
    return state


def propagation_node(state: AMLState) -> AMLState:
    """Вход: final_decisions + operations. Выход: propagated_decisions."""

    state["propagated_decisions"] = propagate_decisions(
        state.get("final_decisions", []),
        state.get("operations", []),
        threshold=0.75,
    )
    return state


def post_propagation_validator_node(state: AMLState) -> AMLState:
    """Вход: propagated_decisions. Выход: флаг ремонта пропагированных строк."""

    has_empty = any(d.get("operation_id") in (None, "") for d in state.get("propagated_decisions", []))
    state["needs_repair_propagated"] = has_empty
    return state


def repair_propagated_rows_node(state: AMLState) -> AMLState:
    """Вход: propagated_decisions c пропусками. Выход: repaired propagated_decisions."""

    if not state.get("needs_repair_propagated"):
        return state
    state["propagated_decisions"] = [d for d in state.get("propagated_decisions", []) if d.get("operation_id")]
    return state


def suspicious_db_write_node(state: AMLState) -> AMLState:
    """Вход: propagated_decisions. Выход: suspicious_to_write + DB upsert."""

    suspicious = [d for d in state.get("propagated_decisions", []) if d.get("decision") == "suspicious"]
    session_factory = state["session_factory"]
    with session_factory() as s:
        for d in suspicious:
            op = next((o for o in state.get("operations", []) if o["operation_id"] == d["operation_id"]), None)
            if op:
                upsert_suspicious(s, op.get("counterparty", "UNKNOWN"), d["risk_level"], d["reason"])
    state["suspicious_to_write"] = suspicious
    return state


def audit_log_node(state: AMLState) -> AMLState:
    """Вход: операции и решения. Выход: persisted audit log + finish timestamp."""

    by_decision = {d["operation_id"]: d for d in state.get("propagated_decisions", [])}
    sampled_ids = {o["operation_id"] for o in state.get("sampled_operations", [])}
    rows = []
    for op in state.get("operations", []):
        d = by_decision.get(op["operation_id"], {})
        rows.append(
            {
                "operation_id": op["operation_id"],
                "cluster_id": op.get("cluster_id"),
                "selected_for_llm": op["operation_id"] in sampled_ids,
                "iso_score": op.get("iso_score"),
                "risk_level": d.get("risk_level"),
                "propagation_confidence": d.get("propagation_confidence"),
                "used_tools": d.get("used_tools", []),
            }
        )
    with state["session_factory"]() as s:
        write_audit_rows(s, rows)
    state["audit_log_rows"] = rows
    state["processing_finished_at"] = datetime.utcnow().isoformat()
    return state

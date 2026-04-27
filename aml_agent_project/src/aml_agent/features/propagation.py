"""Propagation layer: перенос решения только на похожие операции в кластере."""

from __future__ import annotations


def _sim_bool(a: bool, b: bool) -> float:
    return 1.0 if bool(a) == bool(b) else 0.0


def _sim_num(a: float, b: float, eps: float = 1e-9) -> float:
    den = max(abs(a), abs(b), eps)
    return max(0.0, 1.0 - abs(a - b) / den)


def calculate_propagation_confidence(seed: dict, candidate: dict) -> float:
    """Считает confidence по формуле из требований."""

    purpose_similarity = _sim_num(seed.get("distance_to_center", 0), candidate.get("distance_to_center", 0))
    iso_similarity = _sim_num(seed.get("iso_score", 0), candidate.get("iso_score", 0))
    court_similarity = _sim_num(seed.get("court_proximity", 0), candidate.get("court_proximity", 0))
    amount_similarity = _sim_num(seed.get("abs_amount", 0), candidate.get("abs_amount", 0))
    counterparty_similarity = _sim_bool(seed.get("counterparty") == candidate.get("counterparty"), True)

    return (
        0.30 * purpose_similarity
        + 0.25 * iso_similarity
        + 0.20 * court_similarity
        + 0.15 * amount_similarity
        + 0.10 * counterparty_similarity
    )


def propagate_decisions(final_decisions: list[dict], all_rows: list[dict], threshold: float = 0.75) -> list[dict]:
    """Применяет propagation только при высоком сходстве, не на весь кластер."""

    by_op = {r["operation_id"]: r for r in all_rows}
    existing_ids = {d["operation_id"] for d in final_decisions}
    out = list(final_decisions)

    for seed_decision in final_decisions:
        seed_op = by_op.get(seed_decision["operation_id"])
        if not seed_op or not seed_decision.get("can_propagate", False):
            continue
        for candidate in all_rows:
            if candidate["operation_id"] in existing_ids:
                continue
            if candidate.get("cluster_id") != seed_op.get("cluster_id"):
                continue
            conf = calculate_propagation_confidence(seed_op, candidate)
            if conf >= threshold:
                d = dict(seed_decision)
                d["operation_id"] = candidate["operation_id"]
                d["propagation_confidence"] = conf
                out.append(d)
                existing_ids.add(candidate["operation_id"])
    return out

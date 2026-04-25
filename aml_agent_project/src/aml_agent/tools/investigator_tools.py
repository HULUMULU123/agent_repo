"""Инструменты investigator-агента с декоратором @tool и явными описаниями."""

from __future__ import annotations

from langchain_core.tools import BaseTool, tool


@tool
def spark_interfax_lookup(counterparty: str) -> dict:
    """Проверяет контрагента по mock-источнику Spark/Interfax: флаги, санкционные/банкротные маркеры и риск-заметки."""

    return {
        "counterparty": counterparty,
        "spark_flags": [],
        "bankruptcy_signals": [],
        "sanctions_signals": [],
        "source": "spark_interfax",
    }


@tool
def graph_relations_lookup(counterparty: str) -> dict:
    """Ищет связи контрагента в mock-графе отношений: аффилированность, бенефициары, транзакционные цепочки."""

    return {"counterparty": counterparty, "relations": [], "source": "graph_relations"}


@tool
def lookup_suspicious_counterparty(counterparty: str) -> dict:
    """Выполняет точечный lookup контрагента в mock-реестре suspicious counterparties."""

    return {"counterparty": counterparty, "is_suspicious": False, "source": "suspicious_db_lookup"}


@tool
def search_suspicious_counterparties(query: str) -> dict:
    """Выполняет полнотекстовый поиск похожих контрагентов в mock-реестре suspicious counterparties."""

    return {"query": query, "matches": [], "source": "suspicious_db_search"}


@tool
def get_historical_client_profile(client: str) -> dict:
    """Возвращает mock-исторический AML-профиль клиента: базовый риск, тренды и аномальные периоды."""

    return {"client": client, "risk_baseline": "low", "anomaly_periods": [], "source": "historical_client"}


@tool
def get_historical_client_counterparty_profile(client: str, counterparty: str) -> dict:
    """Возвращает mock-историю взаимодействия пары клиент-контрагент: частота, объемы, отклонения."""

    return {
        "client": client,
        "counterparty": counterparty,
        "history": [],
        "frequency_trend": "stable",
        "source": "historical_pair",
    }


@tool
def search_normative_base(query: str) -> dict:
    """Ищет релевантные нормы AML в mock-нормативной базе по запросу investigator-агента."""

    return {"query": query, "documents": [], "source": "normative_base"}


def get_investigator_tools() -> list[BaseTool]:
    """Возвращает полный список tools, доступных investigator-агенту."""

    return [
        spark_interfax_lookup,
        graph_relations_lookup,
        lookup_suspicious_counterparty,
        search_suspicious_counterparties,
        get_historical_client_profile,
        get_historical_client_counterparty_profile,
        search_normative_base,
    ]


def render_tools_catalog() -> list[dict[str, str]]:
    """Формирует каталог инструментов (name + description), чтобы агент "видел" их назначение."""

    return [
        {
            "name": t.name,
            "description": t.description or "No description",
        }
        for t in get_investigator_tools()
    ]

# Python-модули проекта: краткий обзор

## Корень
- `main.py` — CLI: принимает входной файл, запускает LangGraph workflow, сохраняет итоговый state и печатает summary.

## Пакет `src/aml_agent`
- `__init__.py` — маркер пакета.

### `graph/`
- `graph/__init__.py` — маркер подпакета graph.
- `graph/workflow.py` — сборка графа и последовательности нод (START → ... → END).
- `graph/nodes.py` — реализация бизнес-нод pipeline (ingestion, features, routing, investigator, finalizer, repair, propagation, db write, audit).

### `ingestion/`
- `ingestion/__init__.py` — маркер подпакета ingestion.
- `ingestion/extractors.py` — роутер парсинга по типам файлов (csv/xlsx/pdf/image).
- `ingestion/pdf_parser.py` — двухэтапный PDF-парсер (`pdfplumber` таблицы → `pymupdf` текст) с quality-check и fallback-сигналом.
- `ingestion/image_parser.py` — обработка изображений через LLM-парсер (без локального OCR в MVP).
- `ingestion/llm_parser.py` — универсальный LLM-парсер документов через GigaChat + JSON-декод.
- `ingestion/normalizer.py` — нормализация дат, сумм, строковых полей и обязательных колонок.
- `ingestion/validators.py` — базовая валидация ключевых полей и выделение `manual_review_rows`.

### `features/`
- `features/__init__.py` — маркер подпакета features.
- `features/amount_time_features.py` — вычисление amount/time/frequency/velocity/repeated/court proximity признаков.
- `features/purpose_embeddings.py` — TF-IDF векторизация `purpose`.
- `features/clustering.py` — KMeans-кластеризация по embeddings + метрики позиции в кластере.
- `features/isolation_forest.py` — аномалия-скоринг через IsolationForest (`iso_score`, `iso_rank`, `is_iso_anomaly`).
- `features/sampling.py` — representative sampling внутри кластеров по приоритетной формуле.
- `features/propagation.py` — расчет `propagation_confidence` и аккуратный перенос решений только на похожие операции.

### `llm/`
- `llm/__init__.py` — маркер подпакета llm.
- `llm/gigachat_client.py` — класс `GigaChatClient` с методами для `document parser`, `low risk reviewer`, `investigator`, `finalizer`, `repair` и `send_file`.

### `api/`
- `api/__init__.py` — маркер API-подпакета.
- `api/app.py` — FastAPI-приложение: `POST /analyze` (загрузка файла, запуск пайплайна, возврат результата) и `GET /health`.
- `api/schemas.py` — схемы ответов API (`AnalyzeResponse`).

### `prompts/`
- `prompts/__init__.py` — маркер подпакета prompts.
- `prompts/prompts.py` — русскоязычные системные промпты: parser/reviewer/investigator/finalizer/repair.

### `tools/`
- `tools/__init__.py` — экспорт investigator tools.
- `tools/investigator_tools.py` — набор investigator-инструментов c `@tool`, плюс каталог `name+description` для видимости агенту.

### `storage/`
- `storage/__init__.py` — маркер подпакета storage.
- `storage/models.py` — SQLAlchemy-модели `suspicious_counterparties` и `audit_log`.
- `storage/database.py` — фабрика сессий SQLite и CRUD/запись аудита.
- `storage/suspicious_tools.py` — re-export DB-функций как tools-обертки lookup/search/upsert.

### `utils/`
- `utils/__init__.py` — маркер подпакета utils.
- `utils/types.py` — TypedDict-типы операций, evidence, final decision и общего состояния графа.
- `utils/schemas.py` — Pydantic-схемы для final/evidence валидации.

### `pipeline/`
- `pipeline/__init__.py` — маркер сервисного слоя пайплайна.
- `pipeline/service.py` — функция `run_pipeline`, единая точка запуска workflow для CLI и API.

# AML Agent Project

Модульный Python 3.11+ проект AML-агента для анализа банковских выписок.

## Запуск

```bash
cd aml_agent_project
python -m venv .venv
source .venv/bin/activate
pip install -e .
python main.py --input data/sample_statement.csv --output data/result.json
```

## Запуск API (FastAPI)

```bash
cd aml_agent_project
uvicorn aml_agent.api.app:app --host 0.0.0.0 --port 8000
```

Пример запроса:

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@data/sample_statement.csv" \
  -F "db_url=sqlite:///aml_agent.db"
```

## Переменные окружения

Создайте `.env`:

```env
GIGACHAT_CREDENTIALS=...
GIGACHAT_SCOPE=GIGACHAT_API_PERS
```

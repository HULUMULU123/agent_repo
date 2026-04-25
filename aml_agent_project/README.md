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

## Переменные окружения

Создайте `.env`:

```env
GIGACHAT_CREDENTIALS=...
GIGACHAT_SCOPE=GIGACHAT_API_PERS
```

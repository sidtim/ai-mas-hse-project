# Мультиагентная система на основе LLM для генерации и автоматической проверки математических задач

---

Научный руководитель: Артём Беляев (tg: @karaoke_tutu)

Студент: Андрей Тимонин (tg: @sidtim)

Для запуска проекта зайдите в терминал и введите команду: `TEMPERATURE=0.7 MAX_TOKENS=2048 MODEL_ID=deepseek/deepseek-v3.2 docker-compose up --build`

Параметры окружения `TEMPERATURE`, `MAX_TOKENS`, `MODEL_ID` можете задать свои.

Чтобы проверить конфигурацию откройте новый bash-терминал и введите: `curl http://localhost:8000/config`

***Сюда еще 100% надо API-Ключ добавить, чтобы любой рандомный пользователь смог воспользоваться сервисом***

[План проекта](https://docs.google.com/document/d/11XnvAZldgIoLgLMSvpIcb7nGW0Zq7bHskZTJEk0Eeos/edit?usp=sharing)

```
ai-mas-hse-project
├─ .pre-commit-config.yaml
├─ LICENSE
├─ README.md
├─ __del_python.py
├─ ai_mas_hse_project
│  ├─ __init__.py
│  ├─ backend
│  │  ├─ Dockerfile
│  │  ├─ agents
│  │  │  ├─ __init__.py
│  │  │  ├─ generator.py
│  │  │  ├─ reviewer.py
│  │  │  └─ solver.py
│  │  ├─ config.py
│  │  ├─ graph
│  │  │  └─ workflow.py
│  │  ├─ main.py
│  │  ├─ models
│  │  │  ├─ __init__.py
│  │  │  └─ schemas.py
│  │  ├─ requirements.txt
│  │  └─ static_dataset
│  ├─ data
│  │  ├─ final_dataset
│  │  │  └─ list_dict_with_tasks.pkl
│  │  ├─ html_source
│  │  ├─ json_source
│  │  └─ llm_results
│  │     └─ tasks_result_liquidai_06_01_2025.pkl
│  ├─ docker-compose.yml
│  ├─ frontend
│  │  ├─ Dockerfile
│  │  ├─ app.py
│  │  └─ requirements.txt
│  ├─ main.py
│  ├─ notebooks
│  │  ├─ 1-create-dataset.ipynb
│  │  ├─ 2-eda.ipynb
│  │  ├─ 3-agent-tutorial.ipynb
│  │  ├─ 4-agent-baseline.ipynb
│  │  ├─ 5-russian-math-dataset.ipynb
│  │  ├─ 6-openai-test.ipynb
│  │  ├─ 7-metrics.ipynb
│  │  ├─ config.py
│  │  ├─ output_from_file.json
│  │  ├─ tasks_result_deepseek_23_02_2026.pkl
│  │  └─ test.html
│  ├─ src
│  │  └─ create_dataset.py
│  └─ static_dataset
│     └─ list_dict_with_tasks.pkl
├─ poetry.lock
├─ pyproject.toml
├─ references
│  └─ README.md
└─ tas_config.sh

```
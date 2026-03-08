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
│  │  │  ├─ mcp_solver.py
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
│  ├─ calculator_server.py
│  ├─ data
│  │  ├─ final_dataset
│  │  │  └─ list_dict_with_tasks.pkl
│  │  ├─ html_source
│  │  │  ├─ 102999.html
│  │  │  ├─ 103822.html
│  │  │  ├─ 104102.html
│  │  │  ├─ 104122.html
│  │  │  ├─ 105072.html
│  │  │  ├─ 105085.html
│  │  │  ├─ 105103.html
│  │  │  ├─ 105120.html
│  │  │  ├─ 105197.html
│  │  │  ├─ 107706.html
│  │  │  ├─ 108978.html
│  │  │  ├─ 109027.html
│  │  │  ├─ 109436.html
│  │  │  ├─ 109483.html
│  │  │  ├─ 111261.html
│  │  │  ├─ 111262.html
│  │  │  ├─ 111357.html
│  │  │  ├─ 111644.html
│  │  │  ├─ 111895.html
│  │  │  ├─ 115444.html
│  │  │  ├─ 115450.html
│  │  │  ├─ 115968.html
│  │  │  ├─ 116023.html
│  │  │  ├─ 116226.html
│  │  │  ├─ 116439.html
│  │  │  ├─ 116445.html
│  │  │  ├─ 116528.html
│  │  │  ├─ 116534.html
│  │  │  ├─ 116563.html
│  │  │  ├─ 116684.html
│  │  │  ├─ 116797.html
│  │  │  ├─ 116799.html
│  │  │  ├─ 116875.html
│  │  │  ├─ 116883.html
│  │  │  ├─ 116885.html
│  │  │  ├─ 116990.html
│  │  │  ├─ 30262.html
│  │  │  ├─ 30289.html
│  │  │  ├─ 30320.html
│  │  │  ├─ 30321.html
│  │  │  ├─ 30322.html
│  │  │  ├─ 30325.html
│  │  │  ├─ 30341.html
│  │  │  ├─ 30346.html
│  │  │  ├─ 30364.html
│  │  │  ├─ 30419.html
│  │  │  ├─ 30431.html
│  │  │  ├─ 30690.html
│  │  │  ├─ 30697.html
│  │  │  ├─ 30699.html
│  │  │  ├─ 30722.html
│  │  │  ├─ 30778.html
│  │  │  ├─ 30832.html
│  │  │  ├─ 30862.html
│  │  │  ├─ 30937.html
│  │  │  ├─ 30941.html
│  │  │  ├─ 31083.html
│  │  │  ├─ 31235.html
│  │  │  ├─ 32052.html
│  │  │  ├─ 32830.html
│  │  │  ├─ 32838.html
│  │  │  ├─ 34848.html
│  │  │  ├─ 34872.html
│  │  │  ├─ 34938.html
│  │  │  ├─ 35012.html
│  │  │  ├─ 35071.html
│  │  │  ├─ 35129.html
│  │  │  ├─ 35178.html
│  │  │  ├─ 35306.html
│  │  │  ├─ 35352.html
│  │  │  ├─ 35399.html
│  │  │  ├─ 35479.html
│  │  │  ├─ 35532.html
│  │  │  ├─ 35641.html
│  │  │  ├─ 35676.html
│  │  │  ├─ 35734.html
│  │  │  ├─ 60336.html
│  │  │  ├─ 60345.html
│  │  │  ├─ 60370.html
│  │  │  ├─ 60378.html
│  │  │  ├─ 60381.html
│  │  │  ├─ 60382.html
│  │  │  ├─ 60384.html
│  │  │  ├─ 60402.html
│  │  │  ├─ 60403.html
│  │  │  ├─ 60450.html
│  │  │  ├─ 60652.html
│  │  │  ├─ 60976.html
│  │  │  ├─ 61199.html
│  │  │  ├─ 61213.html
│  │  │  ├─ 61219.html
│  │  │  ├─ 61221.html
│  │  │  ├─ 61222.html
│  │  │  ├─ 64511.html
│  │  │  ├─ 64670.html
│  │  │  ├─ 64671.html
│  │  │  ├─ 64822.html
│  │  │  ├─ 64824.html
│  │  │  ├─ 64833.html
│  │  │  ├─ 64891.html
│  │  │  ├─ 64948.html
│  │  │  ├─ 64960.html
│  │  │  ├─ 65265.html
│  │  │  ├─ 65267.html
│  │  │  ├─ 65312.html
│  │  │  ├─ 65315.html
│  │  │  ├─ 65330.html
│  │  │  ├─ 65333.html
│  │  │  ├─ 65344.html
│  │  │  ├─ 65425.html
│  │  │  ├─ 65636.html
│  │  │  ├─ 65768.html
│  │  │  ├─ 65785.html
│  │  │  ├─ 65965.html
│  │  │  ├─ 65985.html
│  │  │  ├─ 65987.html
│  │  │  ├─ 66034.html
│  │  │  ├─ 66038.html
│  │  │  ├─ 66354.html
│  │  │  ├─ 66360.html
│  │  │  ├─ 66576.html
│  │  │  ├─ 66720.html
│  │  │  ├─ 67400.html
│  │  │  ├─ 67443.html
│  │  │  ├─ 67455.html
│  │  │  ├─ 76414.html
│  │  │  ├─ 76429.html
│  │  │  ├─ 76430.html
│  │  │  ├─ 76501.html
│  │  │  ├─ 77964.html
│  │  │  ├─ 78008.html
│  │  │  ├─ 78025.html
│  │  │  ├─ 78159.html
│  │  │  ├─ 78489.html
│  │  │  ├─ 78726.html
│  │  │  ├─ 86483.html
│  │  │  ├─ 87981.html
│  │  │  ├─ 87992.html
│  │  │  ├─ 88078.html
│  │  │  ├─ 88081.html
│  │  │  ├─ 88105.html
│  │  │  ├─ 88129.html
│  │  │  ├─ 88142.html
│  │  │  ├─ 88246.html
│  │  │  ├─ 89919.html
│  │  │  ├─ 98427.html
│  │  │  ├─ 98470.html
│  │  │  └─ test.html
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
│  │  ├─ calculator_server.py
│  │  ├─ config.py
│  │  ├─ mcp-testing.ipynb
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
import streamlit as st
import requests
import os
import random
import pickle
from pathlib import Path
import time

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ---------- Цены за 1K токенов ----------
PRICE_PER_1K_INPUT = 0.044   # рублей за 1K входных токенов
PRICE_PER_1K_OUTPUT = 0.066   # рублей за 1K выходных токенов

# ---------- UI ----------
st.set_page_config(
    page_title="Math Multi-Agent System",
    page_icon="🧮",
    layout="centered"
)

st.title("🧮 Мультиагентная система для математических задач")
st.markdown("---")

# ---------- Загрузка MCP-задач ----------
@st.cache_resource
def load_mcp_dataset():
    mcp_path = Path("/app/static_dataset/mcp_equations.pkl")
    with open(mcp_path, "rb") as f:
        return pickle.load(f)

MCP_EQUATIONS = load_mcp_dataset()

# ---------- Инициализация накопителей ----------
if "total_input_tokens" not in st.session_state:
    st.session_state.total_input_tokens = 0
    st.session_state.total_output_tokens = 0
    st.session_state.total_cost = 0.0

def add_usage_and_cost(input_tokens, output_tokens):
    """Добавляет использованные токены и пересчитывает стоимость."""
    st.session_state.total_input_tokens += input_tokens
    st.session_state.total_output_tokens += output_tokens
    cost = (input_tokens / 1000) * PRICE_PER_1K_INPUT + (output_tokens / 1000) * PRICE_PER_1K_OUTPUT
    st.session_state.total_cost += cost

# ---------- Инициализация состояний ----------
if "generated" not in st.session_state:
    st.session_state.generated = False
if "problem" not in st.session_state:
    st.session_state.problem = ""
if "ground_truth" not in st.session_state:
    st.session_state.ground_truth = ""
if "topic" not in st.session_state:
    st.session_state.topic = "алгебра"
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "средний"
if "is_mcp_equation" not in st.session_state:
    st.session_state.is_mcp_equation = False
if "gen_info" not in st.session_state:
    st.session_state.gen_info = None
if "review_info" not in st.session_state:
    st.session_state.review_info = None

# Шаг 1: Выбор темы и генерация
st.subheader("Шаг 1: Выберите тему и сгенерируйте задачу")

col1, col2 = st.columns([2, 1])

with col1:
    available_topics = [
        'алгебра и арифметика', 'комбинаторика', 'олимпиадные задачи',
        'математический анализ', 'вероятность и статистика', "уравнения"
    ]
    topic = st.selectbox(
        "Тема задачи:",
        available_topics,
        index=available_topics.index(st.session_state.topic)
        if st.session_state.topic in available_topics else 0
    )
    st.session_state.topic = topic

    is_mcp_mode = (topic == "уравнения")
    st.session_state.is_mcp_equation = is_mcp_mode

    if not is_mcp_mode:
        difficulty = st.selectbox(
            "Уровень сложности:",
            ["легкий", "средний", "сложный"],
            index=["легкий", "средний", "сложный"].index(st.session_state.difficulty)
        )
        st.session_state.difficulty = difficulty
    else:
        st.info("🧮 Режим MCP: точные математические вычисления через SymPy/NumPy/SciPy")

with col2:
    st.write("")
    st.write("")
    if is_mcp_mode:
        generate_btn_mcp = st.button("🎯 Получить уравнение", use_container_width=True)
        generate_btn_agent = False
        generate_btn_static = False
    else:
        generate_btn_agent = st.button("🎲 Сгенерировать задачу агентом", use_container_width=True)
        generate_btn_static = st.button("📚 Сгенерировать из банка задач", use_container_width=True)
        generate_btn_mcp = False

# Обработка MCP-уравнения
if generate_btn_mcp:
    start = time.time()
    with st.spinner("Выбираю уравнение..."):
        try:
            equation = random.choice(MCP_EQUATIONS)
            elapsed = time.time() - start
            st.session_state.problem = equation["problem"]
            st.session_state.ground_truth = equation["ground_truth"]
            st.session_state.mcp_hint = equation["hint"]
            st.session_state.generated = True
            st.session_state.result_shown = False
            # Для статического выбора нет токенов
            st.session_state.gen_info = {
                "time": elapsed,
                "input_tokens": 0,
                "output_tokens": 0
            }
            add_usage_and_cost(0, 0)
        except Exception as e:
            st.error(f"Ошибка: {e}")

# Обработка генерации агентом
if generate_btn_agent:
    start = time.time()
    with st.spinner("Генерирую задачу..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/generate",
                json={"topic": topic, "difficulty": st.session_state.difficulty}
            )
            elapsed = time.time() - start
            response.raise_for_status()
            data = response.json()

            st.session_state.problem = data["problem"]
            st.session_state.ground_truth = data["ground_truth"]
            st.session_state.generated = True
            st.session_state.result_shown = False

            in_tok = data.get("input_tokens", 0)
            out_tok = data.get("output_tokens", 0)
            gen_time = data.get("generation_time_seconds", elapsed)
            st.session_state.gen_info = {
                "time": gen_time,
                "input_tokens": in_tok,
                "output_tokens": out_tok
            }
            add_usage_and_cost(in_tok, out_tok)
        except Exception as e:
            st.error(f"Ошибка генерации: {e}")

# Обработка статической генерации
if generate_btn_static:
    start = time.time()
    with st.spinner("Генерирую задачу..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/generate_static",
                json={"topic": topic, "difficulty": st.session_state.difficulty}
            )
            elapsed = time.time() - start
            response.raise_for_status()
            data = response.json()

            st.session_state.problem = data["problem"]
            st.session_state.ground_truth = data["ground_truth"]
            st.session_state.generated = True
            st.session_state.result_shown = False

            st.session_state.gen_info = {
                "time": elapsed,
                "input_tokens": 0,
                "output_tokens": 0
            }
            add_usage_and_cost(0, 0)
        except Exception as e:
            st.error(f"Ошибка генерации: {e}")

# Показываем задачу и статистику генерации
if st.session_state.generated:
    st.markdown("---")
    st.subheader("📋 Задача:")
    if st.session_state.get("is_mcp_equation"):
        st.info(f"🧮 **Тип:** {st.session_state.get('mcp_hint', 'Математическое уравнение')}")
    st.info(st.session_state.problem)

    # Статистика генерации
    if st.session_state.gen_info:
        info = st.session_state.gen_info
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.caption(f"⏱️ Время генерации: {info['time']:.2f} сек")
        with col_t2:
            st.caption(f"🔢 Токены: {info['input_tokens']} вх / {info['output_tokens']} вых")

    # Шаг 2: Решение пользователя
    st.markdown("---")
    st.subheader("Шаг 2: Введите ваше решение")
    user_solution = st.text_area(
        "Ваше решение и ответ:",
        height=150,
        placeholder="Опишите ход решения и укажите ответ..."
    )

    submit_button = st.button("📤 Отправить решение", type="primary")

    if submit_button:
        if not user_solution.strip():
            st.warning("Пожалуйста, введите решение")
        else:
            start = time.time()
            if st.session_state.get("is_mcp_equation"):
                with st.spinner("🔧 MCP агент решает уравнение..."):
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/solve_with_mcp",
                            json={
                                "problem": st.session_state.problem,
                                "user_solution": user_solution,
                                "ground_truth": st.session_state.ground_truth
                            }
                        )
                        elapsed = time.time() - start
                        response.raise_for_status()
                        result = response.json()

                        # Форматируем результат для единообразия
                        st.session_state.result = {
                            "agent_analysis": {
                                "solver_answer": result.get("mcp_answer", ""),
                                "reviewer_verdict": result.get("review_verdict", "НЕИЗВЕСТНО"),
                                "is_correct": result.get("is_correct", False),
                                "answer_analysis": "",
                                "solution_analysis": f"MCP инструменты: {[tc['tool'] for tc in result.get('mcp_tool_calls', [])]}",
                                "recommendation": result.get("recommendation", "")
                            },
                            "user_solution": user_solution,
                            "mcp_details": result
                        }
                        st.session_state.result_shown = True
                        st.session_state.is_mcp_result = True

                        # Статистика
                        in_tok = result.get("input_tokens", 0)
                        out_tok = result.get("output_tokens", 0)
                        gen_time = result.get("generation_time_seconds", elapsed)
                        st.session_state.review_info = {
                            "time": gen_time,
                            "input_tokens": in_tok,
                            "output_tokens": out_tok
                        }
                        add_usage_and_cost(in_tok, out_tok)
                    except Exception as e:
                        st.error(f"Ошибка MCP решения: {e}")
            else:
                with st.spinner("Агенты проверяют ваше решение..."):
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/solve",
                            json={
                                "problem": st.session_state.problem,
                                "user_solution": user_solution,
                                "ground_truth": st.session_state.ground_truth
                            }
                        )
                        elapsed = time.time() - start
                        response.raise_for_status()
                        result = response.json()

                        st.session_state.result = result
                        st.session_state.result_shown = True
                        st.session_state.is_mcp_result = False

                        # Извлекаем статистику
                        analysis = result.get("agent_analysis", {})
                        in_tok = analysis.get("input_tokens", 0)
                        out_tok = analysis.get("output_tokens", 0)
                        gen_time = analysis.get("generation_time_seconds", elapsed)
                        st.session_state.review_info = {
                            "time": gen_time,
                            "input_tokens": in_tok,
                            "output_tokens": out_tok
                        }
                        add_usage_and_cost(in_tok, out_tok)
                    except Exception as e:
                        st.error(f"Ошибка проверки: {e}")

# Показываем результат проверки
if st.session_state.get("result_shown", False):
    st.markdown("---")
    st.subheader("📊 Результат проверки")

    result = st.session_state.result

    if "agent_analysis" in result:
        analysis = result["agent_analysis"]

        is_fully_correct = (analysis.get("is_correct", False) and
                            analysis.get("reviewer_verdict", "") == "ВЕРНО")
        is_partially_correct = (analysis.get("is_correct", False) and
                                analysis.get("reviewer_verdict", "") == "ОШИБКА В РЕШЕНИИ")

        if is_fully_correct:
            st.success("✅ **ПРАВИЛЬНО!**")
        elif is_partially_correct:
            st.warning("⚠️ **Ответ верный, но есть ошибка в решении!**")
        else:
            st.error("❌ **ОШИБКА**")

        # Статистика проверки
        if st.session_state.review_info:
            info = st.session_state.review_info
            st.caption(f"⏱️ Время проверки: {info['time']:.2f} сек · Токены: {info['input_tokens']} вх / {info['output_tokens']} вых")

        if st.session_state.get("is_mcp_result"):
            st.info("🔧 **Решение через MCP (точные вычисления)**")
            mcp_details = result.get("mcp_details", {})
            if mcp_details.get("mcp_tool_calls"):
                with st.expander("🔍 MCP инструменты"):
                    for i, tc in enumerate(mcp_details["mcp_tool_calls"], 1):
                        st.markdown(f"**Шаг {i}:** `{tc['tool']}`")
                        st.json(tc.get("arguments", {}))
                        st.markdown(f"**Результат:** `{tc.get('result', {})}`")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Ваш ответ:**")
            st.write(result.get("user_solution", "—"))
        with col2:
            st.markdown("**Правильный ответ:**")
            st.write(st.session_state.get("ground_truth", "—"))

        with st.expander("🤖 Детали проверки"):
            st.markdown(f"**Ответ агента:** {analysis.get('solver_answer', '—')}")
            st.markdown(f"**Вердикт:** {analysis.get('reviewer_verdict', '—')}")
            if analysis.get("answer_analysis"):
                st.markdown(f"**Анализ ответа:** {analysis['answer_analysis']}")
            if analysis.get("solution_analysis"):
                st.markdown(f"**Анализ решения:** {analysis['solution_analysis']}")
            if analysis.get("recommendation"):
                st.markdown(f"**💡 Рекомендация:** {analysis['recommendation']}")
    else:
        st.write("Ответ сервера:")
        st.json(result)

# Кнопка сброса задачи
if st.session_state.generated:
    st.markdown("---")
    if st.button("🔄 Начать заново"):
        st.session_state.generated = False
        st.session_state.problem = ""
        st.session_state.ground_truth = ""
        st.session_state.result_shown = False
        st.session_state.is_mcp_equation = False
        st.session_state.is_mcp_result = False
        st.session_state.gen_info = None
        st.session_state.review_info = None
        if "mcp_hint" in st.session_state:
            del st.session_state.mcp_hint
        if "mcp_details" in st.session_state:
            del st.session_state.mcp_details
        st.rerun()

# ---------- Боковая панель: общая статистика сессии ----------
with st.sidebar:
    st.header("📊 Статистика сессии")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Входные токены", st.session_state.total_input_tokens)
    with col_b:
        st.metric("Выходные токены", st.session_state.total_output_tokens)
    st.metric("Общая стоимость", f"₽{st.session_state.total_cost:.6f}")

    if st.button("🗑️ Сбросить статистику"):
        st.session_state.total_input_tokens = 0
        st.session_state.total_output_tokens = 0
        st.session_state.total_cost = 0.0
        st.rerun()
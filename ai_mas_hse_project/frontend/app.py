import streamlit as st
import requests
import os
import random
import pickle
from pathlib import Path

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

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
    
# ============ MCP УРАВНЕНИЯ ============
MCP_EQUATIONS = load_mcp_dataset()


# Инициализация состояния
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

# Шаг 1: Выбор темы и генерация
st.subheader("Шаг 1: Выберите тему и сгенерируйте задачу")

col1, col2 = st.columns([2, 1])

with col1:
    # Добавляем "уравнения" в список тем
    available_topics = ['алгебра и арифметика', 'комбинаторика', 'олимпиадные задачи',
                        'математический анализ', 'вероятность и статистика', "уравнения"]
    
    topic = st.selectbox(
        "Тема задачи:",
        available_topics,
        index=available_topics.index(st.session_state.topic) if st.session_state.topic in available_topics else 0
    )
    st.session_state.topic = topic
    
    # Флаг MCP-режима
    is_mcp_mode = (topic == "уравнения")
    st.session_state.is_mcp_equation = is_mcp_mode

    # Выбор сложности (только для не-MCP режима)
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
        # Для MCP режима только одна кнопка
        generate_btn_mcp = st.button("🎯 Получить уравнение", use_container_width=True)
        generate_btn_agent = False
        generate_btn_static = False
    else:
        # Обычные кнопки для других тем
        generate_btn_agent = st.button("🎲 Сгенерировать задачу агентом", use_container_width=True)
        generate_btn_static = st.button("📚 Сгенерировать из банка задач", use_container_width=True)
        generate_btn_mcp = False

# Обработка генерации MCP-уравнения
if generate_btn_mcp:
    with st.spinner("Выбираю уравнение..."):
        try:
            # Случайное уравнение из набора
            equation = random.choice(MCP_EQUATIONS)
            
            st.session_state.problem = equation["problem"]
            st.session_state.ground_truth = equation["ground_truth"]
            st.session_state.mcp_hint = equation["hint"]
            st.session_state.generated = True
            st.session_state.result_shown = False
            
        except Exception as e:
            st.error(f"Ошибка: {e}")

# Обработка обычной генерации (агент)
if generate_btn_agent:
    with st.spinner("Генерирую задачу..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/generate",
                json={"topic": topic, 
                      "difficulty": st.session_state.difficulty} #json={"topic": topic}
            )
            response.raise_for_status()
            data = response.json()
            
            st.session_state.problem = data["problem"]
            st.session_state.ground_truth = data["ground_truth"]
            st.session_state.generated = True
            st.session_state.result_shown = False
            
        except Exception as e:
            st.error(f"Ошибка генерации: {e}")

# Обработка статической генерации
if generate_btn_static:
    with st.spinner("Генерирую задачу..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/generate_static",
                json={"topic": topic,
                      "difficulty": st.session_state.difficulty}
            )
            response.raise_for_status()
            data = response.json()
            
            st.session_state.problem = data["problem"]
            st.session_state.ground_truth = data["ground_truth"]
            st.session_state.generated = True
            st.session_state.result_shown = False
            
        except Exception as e:
            st.error(f"Ошибка генерации: {e}")

# Показываем задачу
if st.session_state.generated:
    st.markdown("---")
    st.subheader("📋 Задача:")
    
    # Для MCP показываем подсказку
    if st.session_state.get("is_mcp_equation"):
        st.info(f"🧮 **Тип:** {st.session_state.get('mcp_hint', 'Математическое уравнение')}")
    
    st.info(st.session_state.problem)
    
    # Шаг 2: Решение пользователя
    st.markdown("---")
    st.subheader("Шаг 2: Введите ваше решение")
    
    user_solution = st.text_area(
        "Ваше решение и ответ:",
        height=150,
        placeholder="Опишите ход решения и укажите ответ..."
    )
    
    # Кнопка отправки с разной логикой для MCP
    submit_button = st.button("📤 Отправить решение", type="primary")
    
    if submit_button:
        if not user_solution.strip():
            st.warning("Пожалуйста, введите решение")
        else:
            # Выбираем endpoint в зависимости от режима
            if st.session_state.get("is_mcp_equation"):
                # MCP режим - используем новый endpoint
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
                            "mcp_details": result  # Сохраняем полные детали MCP
                        }
                        st.session_state.result_shown = True
                        st.session_state.is_mcp_result = True
                        
                    except Exception as e:
                        st.error(f"Ошибка MCP решения: {e}")
            else:
                # Обычный режим
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
                        response.raise_for_status()
                        result = response.json()
                        
                        st.session_state.result = result
                        st.session_state.result_shown = True
                        st.session_state.is_mcp_result = False
                        
                    except Exception as e:
                        st.error(f"Ошибка проверки: {e}")

# Показываем результат
if st.session_state.get("result_shown", False):
    st.markdown("---")
    st.subheader("📊 Результат проверки")
    
    result = st.session_state.result
    
    # Проверяем структуру ответа
    if "agent_analysis" in result:
        analysis = result["agent_analysis"]
        
        # Карточка результата
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
        
        # Для MCP результата показываем специальную информацию
        if st.session_state.get("is_mcp_result"):
            st.info("🔧 **Решение через MCP (точные вычисления)**")
            
            # Показываем детали MCP если есть
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
        # Если структура другая — показываем как есть
        st.write("Ответ сервера:")
        st.json(result)

# Кнопка сброса
if st.session_state.generated:
    st.markdown("---")
    if st.button("🔄 Начать заново"):
        st.session_state.generated = False
        st.session_state.problem = ""
        st.session_state.ground_truth = ""
        st.session_state.result_shown = False
        st.session_state.is_mcp_equation = False
        st.session_state.is_mcp_result = False
        if "mcp_hint" in st.session_state:
            del st.session_state.mcp_hint
        if "mcp_details" in st.session_state:
            del st.session_state.mcp_details
        st.rerun()
import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Math Multi-Agent System",
    page_icon="🧮",
    layout="centered"
)

st.title("🧮 Мультиагентная система для математических задач")
st.markdown("---")

# Инициализация состояния
if "generated" not in st.session_state:
    st.session_state.generated = False
if "problem" not in st.session_state:
    st.session_state.problem = ""
if "ground_truth" not in st.session_state:
    st.session_state.ground_truth = ""
if "topic" not in st.session_state:
    st.session_state.topic = "алгебра"

# Шаг 1: Выбор темы и генерация
st.subheader("Шаг 1: Выберите тему и сгенерируйте задачу")

col1, col2 = st.columns([2, 1])

with col1:
    topic = st.selectbox(
        "Тема задачи:",
        ["алгебра", "комбинаторика", "вероятность и статистика"],
        index=["алгебра", "комбинаторика", "вероятность и статистика"].index(st.session_state.topic)
    )
    st.session_state.topic = topic

with col2:
    st.write("")
    st.write("")
    generate_btn = st.button("🎲 Сгенерировать задачу", use_container_width=True)

if generate_btn:
    with st.spinner("Генерирую задачу..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/generate",
                json={"topic": topic}
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
    st.info(st.session_state.problem)
    
    # Шаг 2: Решение пользователя
    st.markdown("---")
    st.subheader("Шаг 2: Введите ваше решение")
    
    user_solution = st.text_area(
        "Ваше решение и ответ:",
        height=150,
        placeholder="Опишите ход решения и укажите ответ..."
    )
    
    if st.button("📤 Отправить решение", type="primary"):
        if not user_solution.strip():
            st.warning("Пожалуйста, введите решение")
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
                    response.raise_for_status()
                    result = response.json()
                    
                    st.session_state.result = result
                    st.session_state.result_shown = True
                    
                except Exception as e:
                    st.error(f"Ошибка проверки: {e}")

# Показываем результат (строки 100-120 примерно)
if st.session_state.get("result_shown", False):
    st.markdown("---")
    st.subheader("📊 Результат проверки")
    
    result = st.session_state.result
    
    # Проверяем структуру ответа
    if "agent_analysis" in result:
        analysis = result["agent_analysis"]
        
        # Карточка результата
        if analysis.get("is_correct", False):
            st.success("✅ **ПРАВИЛЬНО!**")
        else:
            st.error("❌ **ОШИБКА**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Ваш ответ:**")
            st.write(result.get("user_solution", "—"))
        
        with col2:
            st.markdown("**Правильный ответ:**")
            st.write(st.session_state.get("ground_truth", "—"))
        
        with st.expander("🤖 Что думает агент-решатель"):
            st.write(f"Агент решил так: {analysis.get('solver_answer', '—')}")
            st.write(f"Вердикт проверяющего: {analysis.get('reviewer_verdict', '—')}")
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
        st.rerun()
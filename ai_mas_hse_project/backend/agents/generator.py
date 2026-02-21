from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm

SYSTEM_PROMPT = """# Роль: генератор математических задач.

## Твоя задача — придумать одну задачу по указанной теме математики.

## Требования к задаче:
# 1. Задача должна быть реалистичной и понятной
# 2. Должна иметь однозначный числовой или формульный ответ
# 3. Сложность — уровень школьной олимпиады или ЕГЭ

## Формат ответа:
# Сначала напиши условие задачи.
# Затем, через пустую строку, напиши ответ в формате:
# START_ANSWER [правильный ответ] END_ANSWER

## Пример:
# В магазине 5 яблок и 3 груши. Сколько всего фруктов?
# 
# START_ANSWER 8 END_ANSWER"""

TOPIC_PROMPTS = {
    "алгебра": "Составь задачу по алгебре: уравнения, неравенства, функции или прогрессии.",
    "комбинаторика": "Составь задачу по комбинаторике: перестановки, сочетания, размещения или правило умножения.",
    "вероятность и статистика": "Составь задачу по теории вероятностей или статистике: классическая вероятность, среднее значение или дисперсия."
}

def extract_answer(text: str, start_marker: str = "START_ANSWER", end_marker: str = "END_ANSWER") -> str:
    start_idx = text.rfind(start_marker)
    end_idx = text.rfind(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        start_idx += len(start_marker)
        return text[start_idx:end_idx].strip()
    
    # Если маркеров нет, берем последнюю строку как ответ
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return lines[-1] if lines else "неизвестно"

class GeneratorAgent:
    def __init__(self):
        self.llm = get_llm()
    
    def generate(self, topic: str) -> dict:
        topic_hint = TOPIC_PROMPTS.get(topic, "Составь математическую задачу.")
        
        human_msg = HumanMessage(
            content=f"Тема: {topic}. {topic_hint}",
            name="Пользователь"
        )
        
        response = self.llm.invoke([SystemMessage(content=SYSTEM_PROMPT), human_msg])
        
        # Разделяем задачу и ответ
        text = response.content
        ground_truth = extract_answer(text)
        
        # Убираем ответ из текста задачи (оставляем только условие)
        problem_text = text
        if "START_ANSWER" in text:
            problem_text = text[:text.find("START_ANSWER")].strip()
        
        return {
            "full_response": text,
            "problem": problem_text,
            "ground_truth": ground_truth
        }
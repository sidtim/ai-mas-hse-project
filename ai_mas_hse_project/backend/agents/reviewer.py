from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm

SYSTEM_PROMPT = """Ты проверяющий. Сравни ответ ученика с правильным ответом.

Ответь одним словом:
ПРАВИЛЬНО — если ответы совпадают (допускаются небольшие отличия в формате)
НЕПРАВИЛЬНО — если ответы разные

Не объясняй, просто скажи ПРАВИЛЬНО или НЕПРАВИЛЬНО."""


class ReviewerAgent:
    def __init__(self):
        self.llm = get_llm()
    
    def review(self, solver_answer: str, ground_truth: str = None) -> dict:
        gt_text = ground_truth if ground_truth else "не предоставлен"
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Ответ ученика: {solver_answer}\nПравильный ответ: {gt_text}")
        ]
        
        response = self.llm.invoke(messages)
        text = response.content.strip().upper()
        
        is_correct = "ПРАВИЛЬНО" in text or "CORRECT" in text
        
        return {
            "full_response": response.content,
            "verdict": "ПРАВИЛЬНО" if is_correct else "НЕПРАВИЛЬНО",
            "is_correct": is_correct
        }
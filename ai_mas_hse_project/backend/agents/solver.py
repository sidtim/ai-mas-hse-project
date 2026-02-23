from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm

SYSTEM_PROMPT = """Ты репетитор по математике. Реши задачу пошагово.

Формат ответа (строго):
РЕШЕНИЕ: [пошаговое решение]
ОТВЕТ: [итоговый числовой ответ]

Будь кратким. ОТВЕТ — только число или формула."""


def extract_answer(text: str) -> str:
    """Извлекает ответ из решения"""
    if "ОТВЕТ:" in text:
        parts = text.split("ОТВЕТ:")
        if len(parts) >= 2:
            return parts[1].strip().split("\n")[0]
    
    if "ANSWER:" in text:
        parts = text.split("ANSWER:")
        if len(parts) >= 2:
            return parts[1].strip().split("\n")[0]
    
    # Fallback — последняя строка
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return lines[-1] if lines else text.strip()


class SolverAgent:
    def __init__(self):
        self.llm = get_llm()
    
    def solve(self, problem: str) -> dict:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Реши задачу: {problem}")
        ]
        
        response = self.llm.invoke(messages)
        text = response.content
        extracted = extract_answer(text)
        
        return {
            "full_response": text,
            "answer": extracted
        }
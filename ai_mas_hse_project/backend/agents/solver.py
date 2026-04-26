from langchain_core.messages import SystemMessage, HumanMessage
import time
from config import get_llm


# ------------------------------------------------------------
# Универсальная функция извлечения токенов (совместимость версий)
# ------------------------------------------------------------
def _get_token_usage(response):
    if hasattr(response, 'usage_metadata') and response.usage_metadata:
        inp = response.usage_metadata.get("input_tokens", 0)
        out = response.usage_metadata.get("output_tokens", 0)
        return inp, out

    if hasattr(response, 'response_metadata'):
        token_usage = response.response_metadata.get("token_usage", {})
        inp = token_usage.get("prompt_tokens", 0)
        out = token_usage.get("completion_tokens", 0)
        return inp, out

    return 0, 0


SYSTEM_PROMPT = """
Ты репетитор по математике. Реши задачу пошагово.
Старайся решать задачу кратко и лаконично, если это возможно.

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
        start = time.time()
        response = self.llm.invoke(messages)
        exec_time = time.time() - start

        text = response.content
        extracted = extract_answer(text)

        inp_tokens, out_tokens = _get_token_usage(response)
        usage = {"input_tokens": inp_tokens, "output_tokens": out_tokens}

        return {
            "solver_full": text,
            "solver_answer": extracted,
            "usage": usage,
            "execution_time": exec_time
        }
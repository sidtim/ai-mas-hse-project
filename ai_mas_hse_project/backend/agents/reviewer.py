from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm
import time


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
Ты — опытный педагог-эксперт по проверке математических решений. Твоя задача — не просто сверить ответ, а глубоко проанализировать логику решения ученика.


## Правила анализа:

1. **Проверь финальный ответ** — совпадает ли он с правильным (допускаются незначительные различия в формате: пробелы, регистр, порядок членов).

2. **Проанализируй ход решения** — есть ли у ученика промежуточные шаги? Логичны ли они? Привели ли они к ответу корректным путём или случайно?

3. **Определи категорию результата:**
   - **ВЕРНО** = ответ правильный И решение логически обосновано. не придирайся к мелочам. если ты видишь, что решение в целом верное, но пропущены некоторые детали, то не обращай на это внимание.
   - **ОШИБКА В РЕШЕНИИ** = ответ правильный, но решение содержит серьезные ошибки/недочёты (угадал, случайное совпадение, пропущены шаги). ВАЖНО! Если ответ ученика не содержит правильного ответа, то ты всегда должен выставлять категорию **НЕВЕРНО**.
   - **НЕВЕРНО** = ответ неправильный (независимо от качества решения)

## Формат ответа (строго соблюдай структуру):

ВЕРДИКТ: [ВЕРНО/ОШИБКА В РЕШЕНИИ/НЕВЕРНО]
АНАЛИЗ ОТВЕТА: [правильный/неправильный, с чем совпал]
АНАЛИЗ РЕШЕНИЯ: [краткое описание логики ученика: какие шаги сделал, где ошибся или что сделал верно. описание должно быть кратким и лаконичным]
РЕКОМЕНДАЦИЯ: [если ВЕРНО — похвала; если ОШИБКА В РЕШЕНИИ — конкретный совет, что исправить; если НЕВЕРНО — указание на типичную ошибку]


## Важно:
- Если ответ совпал, но решение отсутствует или сомнительно — всегда указывай "ОШИБКА В РЕШЕНИИ"
- Рекомендация должна быть конкретной и actionable (не общие фразы)
- Не давай полного разбора задачи — фокусируйся на ошибках ученика"""

class ReviewerAgent:
    def __init__(self):
        self.llm = get_llm()
    
    def review(self, solver_answer: str, ground_truth: str = None) -> dict:
        gt_text = ground_truth if ground_truth else "не предоставлен"
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Ответ ученика:\n{solver_answer}\n\nПравильный ответ:\n{gt_text}")
        ]
        
        start = time.time()
        response = self.llm.invoke(messages)
        exec_time = time.time() - start

        text = response.content.strip()
        lines = text.split('\n')
        result = {
            "full_response": text,
            "verdict": "НЕВЕРНО",
            "is_correct": False,
            "answer_analysis": "",
            "solution_analysis": "",
            "recommendation": ""
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith("ВЕРДИКТ:"):
                verdict = line.replace("ВЕРДИКТ:", "").strip()
                result["verdict"] = verdict
                result["is_correct"] = verdict == "ВЕРНО" or verdict == "ОШИБКА В РЕШЕНИИ"
            elif line.startswith("АНАЛИЗ ОТВЕТА:"):
                result["answer_analysis"] = line.replace("АНАЛИЗ ОТВЕТА:", "").strip()
            elif line.startswith("АНАЛИЗ РЕШЕНИЯ:"):
                result["solution_analysis"] = line.replace("АНАЛИЗ РЕШЕНИЯ:", "").strip()
            elif line.startswith("РЕКОМЕНДАЦИЯ:"):
                result["recommendation"] = line.replace("РЕКОМЕНДАЦИЯ:", "").strip()

        inp_tokens, out_tokens = _get_token_usage(response)
        usage = {"input_tokens": inp_tokens, "output_tokens": out_tokens}

        result["usage"] = usage
        result["execution_time"] = exec_time
        
        return result
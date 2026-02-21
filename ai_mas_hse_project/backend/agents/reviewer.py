from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm

SYSTEM_PROMPT = """# Роль: ассистент, проверяющий ответ другого ассистента.

## Твоя задача оценить правильность ответа АССИСТЕНТА №1 и сказать, правильно ли ассистент решил задачу или нет.

## Тебе на вход будет подаваться ответ АССИСТЕНТА №1, а также ground_truth ответ. 

## Сравни ответ АССИСТЕНТА №1 и ground_truth ответ. 

## В качестве ответа напиши "START_ANSWER ПРАВИЛЬНО END_ANSWER", если ответ АССИСТЕНТА №1 и ground_truth совпадают.

## В качестве ответа напиши "START_ANSWER ОШИБКА END_ANSWER", если ответ АССИСТЕНТА №1 и ground_truth НЕ совпадают.

## Если ground_truth отсутствует, то делай выводы на основании собственный умений и знаний. Но даже в этом случае старайся избегать длинных рассуждений. Говори четко и по делу. 

## ПИШИ В ОТВЕТЕ ТОЛЬКО "START_ANSWER ПРАВИЛЬНО END_ANSWER" или "START_ANSWER ОШИБКА END_ANSWER".

## Ты должен обходиться без длительных рассуждений. Твоя задача просто сравнить два ответа и сказать правильно ли АССИСТЕНТ №1 решил задачу или нет."""

def extract_answer(text: str, start_marker: str = "START_ANSWER", end_marker: str = "END_ANSWER") -> str:
    start_idx = text.rfind(start_marker)
    end_idx = text.rfind(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        start_idx += len(start_marker)
        return text[start_idx:end_idx].strip()
    
    return text.strip()

class ReviewerAgent:
    def __init__(self):
        self.llm = get_llm()
    
    def review(self, solver_answer: str, ground_truth: str = None) -> dict:
        gt_text = ground_truth if ground_truth else "не предоставлен"
        
        human_msg = HumanMessage(
            content=f"Ответ АССИСТЕНТА №1: {solver_answer}. ground_truth = {gt_text}",
            name="Проверяющий"
        )
        
        response = self.llm.invoke([SystemMessage(content=SYSTEM_PROMPT), human_msg])
        extracted = extract_answer(response.content).lower()
        
        is_correct = "правильно" in extracted
        
        return {
            "full_response": response.content,
            "verdict": "ПРАВИЛЬНО" if is_correct else "ОШИБКА",
            "is_correct": is_correct
        }
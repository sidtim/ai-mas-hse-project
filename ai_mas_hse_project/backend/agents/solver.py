from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm

SYSTEM_PROMPT = """# Роль: ассистент, хорошо понимающий и разбирающийся в математике.

## Твоя задача помочь пользователю "Студент" решить задачу по математике.

## Твое решение должно содержать подробное рассуждение и шаги, которые ты предпринял, чтобы решить задачу. 

## Ты должен обходиться без длительных рассуждений. Вначале напиши план того, как ты будешь решать задачу. Далее действуй согласно описанному плану. Не уходи в бесконечные рассуждения.

## Ответ к задаче необходимо давать после описания решения к задаче в следующем формате: ответ должен находиться между "START_ANSWER" и "END_ANSWER". Т.е. это должно выглядеть следующим образом:

START_ANSWER "Ответ ассистента к задаче" (идет после решения) END_ANSWER

## Важно!!! Твой ответ должен быть коротким и четким и отвечать на вопрос исходной задачи."""

def extract_answer(text: str, start_marker: str = "START_ANSWER", end_marker: str = "END_ANSWER") -> str:
    start_idx = text.rfind(start_marker)
    end_idx = text.rfind(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        start_idx += len(start_marker)
        return text[start_idx:end_idx].strip()
    
    return text.strip()

class SolverAgent:
    def __init__(self):
        self.llm = get_llm()
    
    def solve(self, problem: str) -> dict:
        human_msg = HumanMessage(
            content=f"Привет, уважаемый ассистент! Я студент. Помоги мне, пожалуйста, решить следующую задачу: {problem}",
            name="Студент"
        )
        
        response = self.llm.invoke([SystemMessage(content=SYSTEM_PROMPT), human_msg])
        extracted = extract_answer(response.content)
        
        return {
            "full_response": response.content,
            "answer": extracted
        }
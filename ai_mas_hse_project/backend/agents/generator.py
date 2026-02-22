from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm
from pathlib import Path
import pickle
import os
import pandas as pd

# Промпт на русском, без служебных токенов
SYSTEM_PROMPT = """Ты генератор математических задач. Придумай ОДНУ задачу по указанной теме.

Требования:
1. Задача должна быть реалистичной и понятной
2. Ответ — число или простая формула
3. Сложность: уровень ЕГЭ или школьной олимпиады

Формат ответа (строго соблюдай):
ЗАДАЧА: [текст задачи]
ОТВЕТ: [числовой ответ]"""

TOPIC_PROMPTS = {
    "алгебра": "Составь задачу по алгебре: уравнения, неравенства, функции или прогрессии.",
    "комбинаторика": "Составь задачу по комбинаторике: перестановки, сочетания или размещения.",
    "вероятность и статистика": "Составь задачу по теории вероятностей или статистике."
}

def extract_problem_answer(text: str) -> tuple:
    """Извлекает задачу и ответ из ответа модели"""
    # Убираем служебные токены если они есть
    text = text.replace("<|system|>", "").replace("<|user|>", "").replace("<|assistant|>", "").strip()
    
    problem = ""
    answer = ""
    
    # Ищем по-русски
    if "ЗАДАЧА:" in text and "ОТВЕТ:" in text:
        parts = text.split("ОТВЕТ:")
        if len(parts) >= 2:
            problem_part = parts[0]
            answer = parts[1].strip().split("\n")[0]
            problem = problem_part.replace("ЗАДАЧА:", "").strip()
    # Fallback на английский если модель переключилась
    elif "PROBLEM:" in text and "ANSWER:" in text:
        parts = text.split("ANSWER:")
        if len(parts) >= 2:
            problem = parts[0].replace("PROBLEM:", "").strip()
            answer = parts[1].strip().split("\n")[0]
    
    # Если не распарсилось — берём всё как задачу, последнее число как ответ
    if not problem:
        lines = [l.strip() for l in text.split("\n") if l.strip() and not l.startswith("Ты ") and not l.startswith("Требования")]
        if len(lines) >= 2:
            problem = "\n".join(lines[:-1])
            answer = lines[-1]
        else:
            problem = text
            answer = "неизвестно"
    
    return problem, answer

class GeneratorAgent:
    def __init__(self):
        self.llm = get_llm()
    
    def generate(self, topic: str) -> dict:
        topic_hint = TOPIC_PROMPTS.get(topic, "Составь математическую задачу.")
        
        # Формируем сообщения вручную в формате TinyLlama
        # TinyLlama использует: <|system|>...<|user|>...<|assistant|>...
        
        system_msg = SystemMessage(content=SYSTEM_PROMPT)
        human_msg = HumanMessage(content=f"Тема: {topic}. {topic_hint}")
        
        response = self.llm.invoke([system_msg, human_msg])
        text = response.content
        
        # # Очистка от служебных токенов
        # text = text.replace("<|system|>", "").replace("<|user|>", "").replace("<|assistant|>", "").strip()
        
        problem, answer = extract_problem_answer(text)
        
        return {
            "full_response": text,
            "problem": problem,
            "ground_truth": answer
        }
    
    def generate_static_task(self, topic: str):
        # Путь внутри контейнера
        dataset_path = Path("/app/static_dataset/list_dict_with_tasks.pkl")
        
        with open(dataset_path, "rb") as f:
            df = pickle.load(f)

        df = pd.DataFrame(df)

        random_task = df.sample(1)

        text_task = random_task['problem'].iloc[0]
        answer_task = random_task['answer'].iloc[0]

        return {
            "problem": text_task,
            "ground_truth": answer_task
        }

        
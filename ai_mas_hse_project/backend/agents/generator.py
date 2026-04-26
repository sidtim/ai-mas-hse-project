from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm
from pathlib import Path
import pickle
import os
import pandas as pd

# Промпт на русском
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

SYSTEM_PROMPT_BY_EXAMPLE = """Ты генератор математических задач. 
Получи пример задачи, её ответ и тему с уровнем сложности. 
Создай **новую** задачу, которая будет похожа по типу и сложности, 
но будет отличаться конкретными числами, контекстом или формулировкой.
Обязательно предоставь:
ЗАДАЧА: [текст новой задачи]
ОТВЕТ: [числовой ответ или краткая формула]
РЕШЕНИЕ: [подробное решение, приводящее к ответу]"""


def extract_problem_answer(text: str) -> tuple:
    """Извлекает задачу и ответ из ответа модели"""
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
        self.dataset_path = Path("/app/static_dataset/list_dict_with_tasks_update.pkl")
        self._dataset = None

    def _load_dataset(self) -> pd.DataFrame:
        if self._dataset is None:
            with open(self.dataset_path, "rb") as f:
                data = pickle.load(f)
            self._dataset = pd.DataFrame(data)
        return self._dataset
    
    def generate(self, topic: str) -> dict:
        topic_hint = TOPIC_PROMPTS.get(topic, "Составь математическую задачу.")
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Тема: {topic}. {topic_hint}")
        ]
        
        response = self.llm.invoke(messages)
        text = response.content
        
        problem, answer = extract_problem_answer(text)
        
        return {
            "full_response": text,
            "problem": problem,
            "ground_truth": answer
        }
    
    # def generate_static_task(self, topic: str):
    #     # Путь внутри контейнера
    #     dataset_path = Path("/app/static_dataset/list_dict_with_tasks_update.pkl")
        
    #     with open(dataset_path, "rb") as f:
    #         df = pickle.load(f)

    #     df = pd.DataFrame(df)

    #     random_task = df.sample(1)

    #     text_task = random_task['problem'].iloc[0]
    #     answer_task = random_task['answer'].iloc[0]

    #     return {
    #         "problem": text_task,
    #         "ground_truth": answer_task
    #     }

    def generate_static_task(self, topic: str, difficulty: str = "средний") -> dict:
        """Возвращает случайную задачу из статического банка с фильтрацией по теме и сложности."""
        example = self._get_random_example(topic, difficulty)
        return {
            "problem": example.get("problem", ""),
            "ground_truth": example.get("answer", ""),
            # "solution": example.get("solution", "")  # можно добавить, если нужно
        }
    
    def _get_random_example(self, topic: str, difficulty: str) -> dict:
        """Возвращает случайную задачу из датасета, по возможности с фильтрацией."""
        df = self._load_dataset()

        # Пытаемся фильтровать, если есть соответствующие колонки
        filtered = df
        if "topic" in df.columns:
            filtered = filtered[filtered["topic"].str.lower() == topic.lower()]
        if "complexity_level_text" in df.columns:
            filtered = filtered[filtered["complexity_level_text"].str.lower() == difficulty.lower()]

        # Если после фильтрации ничего не осталось, берём весь датасет
        if filtered.empty:
            filtered = df

        example = filtered.sample(1).iloc[0].to_dict()
        return example
    
    def generate_by_example(self, topic: str, difficulty: str) -> dict:
        example = self._get_random_example(topic, difficulty)
        example_problem = example.get("problem", "")
        example_answer = example.get("answer", "")

        prompt = (
            f"Тема: {topic}. Сложность: {difficulty}.\n"
            f"Пример задачи: {example_problem}\n"
            f"Ответ примера: {example_answer}\n\n"
            "Составь новую задачу, следуя инструкциям."
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT_BY_EXAMPLE),
            HumanMessage(content=prompt)
        ]

        response = self.llm.invoke(messages)
        text = response.content

        problem, answer, solution = self._parse_example_response(text)
        return {
            "problem": problem,
            "ground_truth": answer,
            "solution": solution        # подробное решение для внутреннего использования
        }
    
    def _parse_example_response(self, text: str) -> tuple:
        """Извлекает задачу, ответ и решение из ответа LLM."""
        problem = answer = solution = ""
        # Регулярный парсинг по ключевым словам
        if "ЗАДАЧА:" in text and "ОТВЕТ:" in text and "РЕШЕНИЕ:" in text:
            try:
                parts = text.split("ЗАДАЧА:")[1]
                problem_part, rest = parts.split("ОТВЕТ:")
                solution_part = rest.split("РЕШЕНИЕ:")[1]
                answer = rest.split("РЕШЕНИЕ:")[0].strip()
                problem = problem_part.strip()
                solution = solution_part.strip()
            except (IndexError, ValueError):
                pass   # fallback ниже

        if not problem:  # fallback на английские метки или простой разбор
            if "PROBLEM:" in text and "ANSWER:" in text and "SOLUTION:" in text:
                # аналогичный парсинг для ENG
                ...
            else:
                # берём первые три непустые строки (грубо)
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                problem = lines[0] if len(lines) > 0 else text
                answer = lines[1] if len(lines) > 1 else "неизвестно"
                solution = "\n".join(lines[2:]) if len(lines) > 2 else ""
        return problem, answer, solution
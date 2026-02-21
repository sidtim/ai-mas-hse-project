# __del_python.py

from dotenv import load_dotenv
import pickle
import os

from IPython.display import Image, display
from langchain_openai import ChatOpenAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint, HuggingFacePipeline
from langchain.tools import tool
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages

from typing_extensions import TypedDict
from typing import Annotated

load_dotenv()  # Считываем креды

torch.cuda.empty_cache()

llm = HuggingFacePipeline.from_model_id(
    model_id="LiquidAI/LFM2-2.6B-Exp",
    task="text-generation",
    device=0,
    pipeline_kwargs=dict(
        max_new_tokens=2000,
        do_sample=False,
        repetition_penalty=1,
    ),
)

tiny_lama_model = ChatHuggingFace(llm=llm)

# Определяем состояние графа
class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    ground_truth: str  # Добавляем поле для правильного ответа
    task_problem: str  # Добавляем поле для текста задачи
    solver_answer: str  # Поле для хранения ответа ассистента-решальщика
    reviewer_answer: str  # Поле для хранения ответа ассистента-проверяльщика
    review_result: int # Результат проверки решения ассистента ассесором. 1 - ответ ассистента правильный. 0 - ответ ассистента неправильный


def find_answer(ass_prompt: str,
                start_marker: str = "START_ANSWER",
                end_marker:str = "END_ANSWER"):
    # Извлекаем ответ из текста
    answer = ass_prompt
    
    start_idx = answer.rfind(start_marker)
    end_idx = answer.rfind(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        start_idx += len(start_marker)
        extracted_answer = answer[start_idx:].strip(end_marker)
    else:
        extracted_answer = answer.strip()
    
    return extracted_answer


# Узел 1: Решение задачи
def task_solver_llm(state: MessagesState):
    # Промт для решения задачи
    system_msg = SystemMessage(
"""
# Роль: ассистент, хорошо понимающий и разбирающийся в математике.

## Твоя задача помочь пользователю "Студент" решить задачу по математике.

## Твое решение должно содержать подробное рассуждение и шаги, которые ты предпринял, чтобы решить задачу. 

## Ты должен обходиться без длительных рассуждений. Вначале напиши план того, как ты будешь решать задачу. Далее действуй согласно описанному плану. Не уходи в бесконечные рассуждения.

## Ответ к задаче необходимо давать после описания решения к задаче в следующем формате: ответ должен находиться между "START_ANSWER" и "END_ANSWER". Т.е. это должно выглядеть следующим образом:

START_ANSWER "Ответ ассистента к задаче" (идет после решения) END_ANSWER

## Важно!!! Твой ответ должен быть коротким и четким и отвечать на вопрос исходной задачи.
"""
    )
    
    human_msg = HumanMessage(
        f"Привет, уважаемый ассистент! Я студент. Помоги мне, пожалуйста, решить следующую задачу: {state['task_problem']}",
        name="Студент"
    )
    
    # Вызываем модель для решения задачи
    response = tiny_lama_model.invoke([system_msg, human_msg])
    
    # Извлекаем ответ из текста
    extracted_answer = find_answer(response.content)
    
    # Обновляем состояние
    return {
        "messages": [
            # system_msg, 
            # human_msg, 
            response
            ],
        "task_problem": state["task_problem"],
        "ground_truth": state["ground_truth"],
        "solver_answer": extracted_answer,
        "reviewer_answer": state['reviewer_answer'],
        "review_result": state['review_result']
    }

# Узел 2: Проверка решения
def task_reviewer_llm(state: MessagesState):
    # Промт для проверки
    system_msg_describe = SystemMessage(
"""
# Роль: ассистент, проверяющий ответ другого ассистента.

## Твоя задача оценить правильность ответа АССИСТЕНТА №1 и сказать, правильно ли ассистент решил задачу или нет.

## Тебе на вход будет подаваться ответ АССИСТЕНТА №1, а также ground_truth ответ. 

## Сравни ответ АССИСТЕНТА №1 и ground_truth ответ. 

## В качестве ответа напиши "START_ANSWER ПРАВИЛЬНО END_ANSWER", если ответ АССИСТЕНТА №1 и ground_truth совпадают.

## В качестве ответа напиши "START_ANSWER ОШИБКА END_ANSWER", если ответ АССИСТЕНТА №1 и ground_truth НЕ совпадают.

## Если ground_truth отсутствует, то делай выводы на основании собственный умений и знаний. Но даже в этом случае старайся избегать длинных рассуждений. Говори четко и по делу. 

## ПИШИ В ОТВЕТЕ ТОЛЬКО "START_ANSWER ПРАВИЛЬНО END_ANSWER" или "START_ANSWER ОШИБКА END_ANSWER".

## Ты должен обходиться без длительных рассуждений. Твоя задача просто сравнить два ответа и сказать правильно ли АССИСТЕНТ №1 решил задачу или нет.
"""
    )
    
    human_msg = HumanMessage(
        f"Ответ АССИСТЕНТА №1: {state['reviewer_answer']}. ground_truth = {state['ground_truth']}",
        name="АССИСТЕНТ №1"
    )
    
    # Вызываем модель для проверки
    response = tiny_lama_model.invoke([system_msg_describe, human_msg])

    extracted_answer = find_answer(response.content).lower()

    review_result = 1 if "правильно" in extracted_answer else 0
    
    # Добавляем сообщение в историю
    return {"messages": [response],
            "task_problem": state["task_problem"],
            "ground_truth": state["ground_truth"],
            "solver_answer": state["solver_answer"],
            "reviewer_answer": extracted_answer,
            "review_result": review_result
    }

builder = StateGraph(MessagesState)

# Добавляем узлы
builder.add_node("task_solver", task_solver_llm)
builder.add_node("task_reviewer", task_reviewer_llm)

# Определяем связи между узлами
builder.add_edge(START, "task_solver")
builder.add_edge("task_solver", "task_reviewer")
builder.add_edge("task_reviewer", END)

# Компилируем граф
graph = builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))

# Тестирование
test_task = list_json[0]  # Ваша тестовая задача

ground_truth_problem = test_task['problem']
ground_truth_answer = test_task['answer']

test_task

# Запускаем граф
torch.cuda.empty_cache()

# Подготавливаем начальное состояние
initial_state = {
    "messages": [],
    "task_problem": ground_truth_problem,
    "ground_truth": ground_truth_answer,
    "solver_answer": "",
    "reviewer_answer": "",
    "review_result": None
}

result = graph.invoke(initial_state)

result
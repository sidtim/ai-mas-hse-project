from typing_extensions import TypedDict
from typing import Annotated, Any
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

from agents.generator import GeneratorAgent
from agents.solver import SolverAgent
from agents.reviewer import ReviewerAgent


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    topic: str
    problem: str
    ground_truth: str
    user_solution: str  # Ответ, предоставленный пользователем (для проверки)
    solver_answer: str  # Ответ, полученный от SolverAgent
    solver_full: str    # Полное решение от SolverAgent
    review_verdict: str
    is_correct: bool


class MathWorkflow:
    def __init__(self):
        self.generator = GeneratorAgent()
        self.solver = SolverAgent()
        self.reviewer = ReviewerAgent()
        
        # Строим граф
        builder = StateGraph(AgentState)
        
        builder.add_node("generate", self._generate_node)
        builder.add_node("solve", self._solve_node)
        builder.add_node("review", self._review_node)
        
        # Полный pipeline: генерация -> решение -> проверка пользовательского ответа
        builder.set_entry_point("generate")
        builder.add_edge("generate", "solve")
        builder.add_edge("solve", "review")
        builder.add_edge("review", END)
        
        self.graph = builder.compile()
    
    def _generate_node(self, state: AgentState) -> dict:
        result = self.generator.generate(state["topic"])
        return {
            "problem": result["problem"],
            "ground_truth": result["ground_truth"],
            "messages": []
        }
    
    def _solve_node(self, state: AgentState) -> dict:
        result = self.solver.solve(state["problem"])
        return {
            "solver_answer": result["solver_answer"],
            "solver_full": result["solver_full"],
            "messages": []
        }
    
    def _review_node(self, state: AgentState) -> dict:
        # Проверяем ответ ПОЛЬЗОВАТЕЛЯ (user_solution) против ground_truth
        # Если нужно проверять решение solver'а — замените state["user_solution"] на state["solver_answer"]
        result = self.reviewer.review(
            solver_answer=state["user_solution"],
            ground_truth=state["ground_truth"]
        )
        return {
            "review_verdict": result["verdict"],
            "is_correct": result["is_correct"],
            "messages": []
        }
    
    def generate_only(self, topic: str) -> dict:
        """Только генерация задачи (для первого эндпоинта)"""
        return self.generator.generate(topic)
    
    def generate_only_static(self, topic: str) -> dict:
        """Только генерация статической задачи (для первого эндпоинта)"""
        return self.generator.generate_static_task(topic)
    
    def full_pipeline(self, topic: str, problem: str, user_solution: str, ground_truth: str) -> dict:
        """Полный pipeline: решение + проверка (без генерации, задача предоставлена извне)"""
        initial_state = {
            "messages": [],
            "topic": topic,
            "problem": problem,
            "ground_truth": ground_truth,
            "user_solution": user_solution,
            "solver_answer": "",
            "solver_full": "",
            "review_verdict": "",
            "is_correct": False
        }
        
        result = self.graph.invoke(initial_state)
        return result
    
    def solve_and_review(self, problem: str, user_solution: str, ground_truth: str) -> dict:
        """Pipeline только для решения и проверки (без генерации)"""
        # Создаем временный граф без generate
        builder = StateGraph(AgentState)
        builder.add_node("solve", self._solve_node)
        builder.add_node("review", self._review_node)
        builder.set_entry_point("solve")
        builder.add_edge("solve", "review")
        builder.add_edge("review", END)
        
        graph = builder.compile()
        
        initial_state = {
            "messages": [],
            "topic": "",
            "problem": problem,
            "ground_truth": ground_truth,
            "user_solution": user_solution,
            "solver_answer": "",
            "solver_full": "",
            "review_verdict": "",
            "is_correct": False
        }
        
        return graph.invoke(initial_state)
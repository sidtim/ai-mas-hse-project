from typing_extensions import TypedDict
from typing import Annotated, Any
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

from agents.generator import GeneratorAgent
from agents.solver import SolverAgent
from agents.reviewer import ReviewerAgent
from agents.mcp_solver import MCPSolverAgent, MCPClient


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    topic: str
    problem: str
    ground_truth: str
    user_solution: str
    solver_answer: str
    solver_full: str
    review_verdict: str
    is_correct: bool
    answer_analysis: str
    solution_analysis: str
    recommendation: str
    # Дополнительные поля для статистики
    gen_usage: dict
    gen_time: float
    solver_usage: dict
    solver_time: float
    review_usage: dict
    review_time: float


class MathWorkflow:
    def __init__(self):
        self.generator = GeneratorAgent()
        self.solver = SolverAgent()
        self.reviewer = ReviewerAgent()

        builder = StateGraph(AgentState)
        builder.add_node("generate", self._generate_node)
        builder.add_node("solve", self._solve_node)
        builder.add_node("review", self._review_node)

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
            "gen_usage": result.get("usage", {}),
            "gen_time": result.get("execution_time", 0.0),
            "messages": [],
        }

    def _solve_node(self, state: AgentState) -> dict:
        result = self.solver.solve(state["problem"])
        return {
            "solver_answer": result["solver_answer"],
            "solver_full": result["solver_full"],
            "solver_usage": result.get("usage", {}),
            "solver_time": result.get("execution_time", 0.0),
            "messages": [],
        }

    def _review_node(self, state: AgentState) -> dict:
        result = self.reviewer.review(
            solver_answer=state["user_solution"],
            ground_truth=state["ground_truth"],
        )
        return {
            "review_verdict": result["verdict"],
            "is_correct": result["is_correct"],
            "answer_analysis": result.get("answer_analysis", ""),
            "solution_analysis": result.get("solution_analysis", ""),
            "recommendation": result.get("recommendation", ""),
            "review_usage": result.get("usage", {}),
            "review_time": result.get("execution_time", 0.0),
            "messages": [],
        }

    def generate_only(self, topic: str, difficulty: str = "средний") -> dict:
        return self.generator.generate_by_example(topic, difficulty)

    def generate_only_static(self, topic: str, difficulty: str = "средний") -> dict:
        return self.generator.generate_static_task(topic, difficulty)

    def full_pipeline(self, topic: str, problem: str, user_solution: str, ground_truth: str) -> dict:
        initial_state = {
            "messages": [],
            "topic": topic,
            "problem": problem,
            "ground_truth": ground_truth,
            "user_solution": user_solution,
            "solver_answer": "",
            "solver_full": "",
            "review_verdict": "",
            "is_correct": False,
            "answer_analysis": "",
            "solution_analysis": "",
            "recommendation": "",
            "gen_usage": {},
            "gen_time": 0.0,
            "solver_usage": {},
            "solver_time": 0.0,
            "review_usage": {},
            "review_time": 0.0,
        }
        return self.graph.invoke(initial_state)

    def solve_and_review(self, problem: str, user_solution: str, ground_truth: str) -> dict:
        # Временный граф без generate
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
            "is_correct": False,
            "answer_analysis": "",
            "solution_analysis": "",
            "recommendation": "",
            "gen_usage": {},
            "gen_time": 0.0,
            "solver_usage": {},
            "solver_time": 0.0,
            "review_usage": {},
            "review_time": 0.0,
        }
        result = graph.invoke(initial_state)
        # result теперь содержит все поля статистики
        return result


# ======================= MCP SOLVER ======================= #
class MCPAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    topic: str
    problem: str
    ground_truth: str
    user_solution: str
    mcp_answer: str
    mcp_full_response: str
    mcp_tool_calls: list
    review_verdict: str
    is_correct: bool
    answer_analysis: str
    solution_analysis: str
    recommendation: str
    # статистика
    mcp_usage: dict
    mcp_time: float
    review_usage: dict
    review_time: float


class MCPMathWorkflow:
    def __init__(self):
        self.mcp_solver = MCPSolverAgent()
        self.reviewer = ReviewerAgent()

        builder = StateGraph(MCPAgentState)
        builder.add_node("mcp_solve", self._mcp_solve_node)
        builder.add_node("review", self._review_node)
        builder.set_entry_point("mcp_solve")
        builder.add_edge("mcp_solve", "review")
        builder.add_edge("review", END)
        self.graph = builder.compile()

    async def _mcp_solve_node(self, state: MCPAgentState) -> dict:
        problem = state.get("problem", "")
        result = await self.mcp_solver.solve(problem)
        return {
            "mcp_answer": result["answer"],
            "mcp_full_response": result["full_response"],
            "mcp_tool_calls": result["tool_calls"],
            "mcp_usage": result.get("usage", {}),
            "mcp_time": result.get("execution_time", 0.0),
            "messages": [],
        }

    async def _review_node(self, state: MCPAgentState) -> dict:
        answer_to_check = state.get("user_solution") or state.get("mcp_answer", "")
        result = self.reviewer.review(
            solver_answer=answer_to_check,
            ground_truth=state["ground_truth"],
        )
        return {
            "review_verdict": result["verdict"],
            "is_correct": result["is_correct"],
            "answer_analysis": result.get("answer_analysis", ""),
            "solution_analysis": result.get("solution_analysis", ""),
            "recommendation": result.get("recommendation", ""),
            "review_usage": result.get("usage", {}),
            "review_time": result.get("execution_time", 0.0),
            "messages": [],
        }

    async def solve_with_mcp(self, problem: str, user_solution: str = "", ground_truth: str = "") -> dict:
        initial_state = {
            "messages": [],
            "topic": "",
            "problem": problem,
            "ground_truth": ground_truth,
            "user_solution": user_solution,
            "mcp_answer": "",
            "mcp_full_response": "",
            "mcp_tool_calls": [],
            "review_verdict": "",
            "is_correct": False,
            "answer_analysis": "",
            "solution_analysis": "",
            "recommendation": "",
            "mcp_usage": {},
            "mcp_time": 0.0,
            "review_usage": {},
            "review_time": 0.0,
        }
        result = await self.graph.ainvoke(initial_state)
        # Для совместимости с main.py собираем общее usage и время
        mcp_usage = result.get("mcp_usage", {})
        review_usage = result.get("review_usage", {})
        total_usage = {
            "input_tokens": mcp_usage.get("input_tokens", 0) + review_usage.get("input_tokens", 0),
            "output_tokens": mcp_usage.get("output_tokens", 0) + review_usage.get("output_tokens", 0),
        }
        total_time = result.get("mcp_time", 0.0) + result.get("review_time", 0.0)
        result["usage"] = total_usage
        result["execution_time"] = total_time
        return result
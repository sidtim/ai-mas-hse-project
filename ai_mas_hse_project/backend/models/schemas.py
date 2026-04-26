from pydantic import BaseModel
from typing import Optional, Literal

class GenerateRequest(BaseModel):
    topic: Literal['алгебра и арифметика', 'комбинаторика', 'олимпиадные задачи',
                   'математический анализ', 'вероятность и статистика']
    difficulty: Optional[Literal['легкий', 'средний', 'сложный']] = "средний"

class GenerateResponse(BaseModel):
    problem: str
    ground_truth: str

class SolveRequest(BaseModel):
    problem: str
    user_solution: str
    ground_truth: Optional[str] = None

class AgentResult(BaseModel):
    solver_answer: str
    reviewer_verdict: str
    is_correct: bool
    answer_analysis: Optional[str] = None
    solution_analysis: Optional[str] = None
    recommendation: Optional[str] = None
    

class SolveResponse(BaseModel):
    problem: str
    user_solution: str
    agent_analysis: AgentResult
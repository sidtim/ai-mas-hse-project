from pydantic import BaseModel
from typing import Optional, Literal

class GenerateRequest(BaseModel):
    topic: Literal["алгебра", "комбинаторика", "вероятность и статистика"]

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

class SolveResponse(BaseModel):
    problem: str
    user_solution: str
    agent_analysis: AgentResult
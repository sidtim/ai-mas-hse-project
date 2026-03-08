import logging
import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import MODEL_ID, TEMPERATURE, MAX_TOKENS

from models.schemas import (
    GenerateRequest, GenerateResponse,
    SolveRequest, SolveResponse, AgentResult
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Math Multi-Agent System", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"ГЛОБАЛЬНАЯ ОШИБКА: {str(exc)}")
    logger.error(traceback.format_exc())
    # Исправлено: возвращаем JSONResponse, а не HTTPException
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.get("/")
def root():
    return {
        "status": "ok",
        "version": "2.0.0",
        "llm_provider": "OpenAI-compatible API (vsellm.ru)"
    }

@app.post("/generate", response_model=GenerateResponse)
def generate_task(request: GenerateRequest):
    """Генерация новой задачи агентом (LLM)"""
    logger.info(f"=== НАЧАЛО ГЕНЕРАЦИИ АГЕНТОМ: {request.topic} ===")
    try:
        from graph.workflow import MathWorkflow
        wf = MathWorkflow()
        result = wf.generate_only(request.topic)
        logger.info(f"УСПЕХ: {result.get('problem', 'НЕТ')[:50]}...")
        
        return GenerateResponse(
            problem=result["problem"],
            ground_truth=result["ground_truth"]
        )
    except Exception as e:
        logger.error(f"ОШИБКА: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_static", response_model=GenerateResponse)
def generate_task_static(request: GenerateRequest):
    """Получение случайной задачи из статического банка"""
    logger.info(f"=== НАЧАЛО ГЕНЕРАЦИИ ИЗ БАНКА ЗАДАЧ: {request.topic} ===")
    try:
        from graph.workflow import MathWorkflow
        wf = MathWorkflow()
        result = wf.generate_only_static(request.topic)
        logger.info(f"УСПЕХ: {result.get('problem', 'НЕТ')[:50]}...")
        
        return GenerateResponse(
            problem=result["problem"],
            ground_truth=result["ground_truth"]
        )
    except Exception as e:
        logger.error(f"ОШИБКА: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/solve", response_model=SolveResponse)
def solve_task(request: SolveRequest):
    """
    Решение задачи и проверка пользовательского ответа.
    Использует solve + review (без генерации новой задачи).
    """
    logger.info(f"=== НАЧАЛО РЕШЕНИЯ И ПРОВЕРКИ ===")
    try:
        from graph.workflow import MathWorkflow
        wf = MathWorkflow()
        
        # Используем solve_and_review вместо full_pipeline
        # чтобы не генерировать новую задачу, а решить предоставленную
        result = wf.solve_and_review(
            problem=request.problem,
            user_solution=request.user_solution,
            ground_truth=request.ground_truth or ""
        )
        
        logger.info(f"Результат решения: solver={result.get('solver_answer', 'N/A')}")
        logger.info(f"Результат проверки: {result.get('review_verdict', 'НЕИЗВЕСТНО')}")
        
        return SolveResponse(
            problem=request.problem,
            user_solution=request.user_solution,
            agent_analysis=AgentResult(
                solver_answer=result.get("solver_answer", ""),
                reviewer_verdict=result.get("review_verdict", "НЕИЗВЕСТНО"),
                is_correct=result.get("is_correct", False),
                answer_analysis=result.get("answer_analysis", ""),
                solution_analysis=result.get("solution_analysis", ""),
                recommendation=result.get("recommendation", ""),
            )
        )
    except Exception as e:
        logger.error(f"ОШИБКА РЕШЕНИЯ/ПРОВЕРКИ: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/solve_only")
def solve_only(request: SolveRequest):
    """
    [Дополнительный] Только решение задачи без проверки.
    Возвращает полное решение и ответ.
    """
    logger.info(f"=== ТОЛЬКО РЕШЕНИЕ ===")
    try:
        from agents.solver import SolverAgent
        solver = SolverAgent()
        
        result = solver.solve(request.problem)
        
        return {
            "problem": request.problem,
            "solution": result["full_response"],
            "answer": result["answer"]
        }
    except Exception as e:
        logger.error(f"ОШИБКА РЕШЕНИЯ: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/full_pipeline")
def full_pipeline_endpoint(request: GenerateRequest):
    """
    [Дополнительный] Полный pipeline: генерация -> решение -> проверка.
    Генерирует задачу, решает её и проверяет (сравнивает solver vs ground_truth).
    Полезно для тестирования качества модели.
    """
    logger.info(f"=== ПОЛНЫЙ PIPELINE: {request.topic} ===")
    try:
        from graph.workflow import MathWorkflow
        wf = MathWorkflow()
        
        # Генерируем задачу
        gen_result = wf.generate_only(request.topic)
        
        # Решаем и проверяем (сравниваем solver_answer с ground_truth)
        result = wf.solve_and_review(
            problem=gen_result["problem"],
            user_solution="",  # Нет пользовательского ответа
            ground_truth=gen_result["ground_truth"]
        )
        
        return {
            "generated_problem": gen_result["problem"],
            "ground_truth": gen_result["ground_truth"],
            "solver_answer": result.get("solver_answer", ""),
            "solver_full": result.get("solver_full", ""),
            "review_verdict": result.get("review_verdict", "НЕИЗВЕСТНО"),
            "is_correct": result.get("is_correct", False)
        }
    except Exception as e:
        logger.error(f"ОШИБКА PIPELINE: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/solve_with_mcp")
async def solve_with_mcp(request: SolveRequest):
    """
    Решение задачи с использованием MCP инструментов.
    Более точные математические вычисления через sympy/numpy.
    """
    logger.info(f"=== MCP РЕШЕНИЕ ===")
    logger.info(f"Получена задача: {request.problem}")
    try:
        from graph.workflow import MCPMathWorkflow
        wf = MCPMathWorkflow()
        
        result = await wf.solve_with_mcp(
            problem=request.problem,
            user_solution=request.user_solution,
            ground_truth=request.ground_truth or ""
        )
        
        return {
            "problem": request.problem,
            "mcp_answer": result.get("mcp_answer", ""),
            "mcp_tool_calls": result.get("mcp_tool_calls", []),
            "review_verdict": result.get("review_verdict", ""),
            "is_correct": result.get("is_correct", False),
            "recommendation": result.get("recommendation", "")
        }
        
    except Exception as e:
        logger.error(f"ОШИБКА MCP: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/config")
def get_config():
    return {
        "model_id": MODEL_ID,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
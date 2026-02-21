import logging
import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import (
    GenerateRequest, GenerateResponse,
    SolveRequest, SolveResponse, AgentResult
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Math Multi-Agent System", version="1.0.0")

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
    return HTTPException(status_code=500, detail=str(exc))

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/generate", response_model=GenerateResponse)
def generate_task(request: GenerateRequest):
    logger.info(f"=== НАЧАЛО ГЕНЕРАЦИИ: {request.topic} ===")
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

@app.post("/solve", response_model=SolveResponse)
def solve_task(request: SolveRequest):
    logger.info(f"=== НАЧАЛО ПРОВЕРКИ ===")
    try:
        from graph.workflow import MathWorkflow
        wf = MathWorkflow()
        
        result = wf.full_pipeline(
            topic="проверка",
            problem=request.problem,
            user_solution=request.user_solution,
            ground_truth=request.ground_truth or ""
        )
        
        logger.info(f"Результат проверки: {result}")
        
        # Собираем ответ в правильном формате
        return SolveResponse(
            problem=request.problem,
            user_solution=request.user_solution,
            agent_analysis=AgentResult(
                solver_answer=result.get("solver_answer", ""),
                reviewer_verdict=result.get("review_verdict", "НЕИЗВЕСТНО"),
                is_correct=result.get("is_correct", False)
            )
        )
    except Exception as e:
        logger.error(f"ОШИБКА ПРОВЕРКИ: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
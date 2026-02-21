import logging
import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import (
    GenerateRequest, GenerateResponse,
    SolveRequest, SolveResponse, AgentResult
)

# Настройка логов ВЫВОД В КОНСОЛЬ
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Math Multi-Agent System",
    version="1.0.0"
)

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
        # Ленивая загрузка чтобы видеть где падает
        logger.info("Импорт workflow...")
        from graph.workflow import MathWorkflow
        
        logger.info("Создание workflow...")
        wf = MathWorkflow()
        
        logger.info("Вызов generate_only...")
        result = wf.generate_only(request.topic)
        
        logger.info(f"УСПЕХ: {result.get('problem', 'НЕТ ПРОБЛЕМЫ')[:50]}")
        return GenerateResponse(
            problem=result["problem"],
            ground_truth=result["ground_truth"]
        )
        
    except Exception as e:
        logger.error(f"ОШИБКА: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/solve")
def solve_task(request: SolveRequest):
    return {"status": "not implemented"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
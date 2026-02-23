import os
from dotenv import load_dotenv

load_dotenv()

# Новые переменные окружения для OpenAI-совместимого API
OPENAI_API_KEY = os.getenv("OPEN_API_KEY_VSE_LLM")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.vsellm.ru/v1")
MODEL_ID = os.getenv("MODEL_ID", "deepseek/deepseek-v3.2")
MAX_TOKENS = os.getenv("MAX_TOKENS")  # None по умолчанию (не ограничиваем)
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))

_llm = None


def get_llm():
    """Возвращает кэшированный экземпляр ChatOpenAI."""
    global _llm
    
    if _llm is None:
        from langchain_openai import ChatOpenAI
        
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPEN_API_KEY_VSE_LLM должен быть установлен в .env"
            )
        
        _llm = ChatOpenAI(
            model=MODEL_ID,
            temperature=TEMPERATURE,
            max_tokens=int(MAX_TOKENS) if MAX_TOKENS else None,
            timeout=None,
            max_retries=2,
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
        )
    
    return _llm










# ==================================================== #
# import os
# from dotenv import load_dotenv

# load_dotenv()

# MODEL_ID = os.getenv("MODEL_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
# MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "512"))
# HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# _llm = None

# def get_llm():
#     global _llm
#     if _llm is None:
#         import torch
#         from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
#         from huggingface_hub import login
        
#         # Логинимся если есть токен
#         if HUGGINGFACE_TOKEN:
#             login(token=HUGGINGFACE_TOKEN)
        
#         torch.cuda.empty_cache()
        
#         pipeline = HuggingFacePipeline.from_model_id(
#             model_id=MODEL_ID,
#             task="text-generation",
#             device=-1,
#             pipeline_kwargs=dict(
#                 max_new_tokens=MAX_NEW_TOKENS,
#                 do_sample=True,
#                 temperature=0.7,
#                 repetition_penalty=1.1,
#             ),
#         )
#         _llm = ChatHuggingFace(llm=pipeline)
    
#     return _llm
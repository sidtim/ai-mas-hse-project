import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPEN_API_KEY_VSE_LLM")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.vsellm.ru/v1")

# Читаем из переменных окружения (из .env или CLI)
MODEL_ID = os.getenv("MODEL_ID", "deepseek/deepseek-v3.2")

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        from langchain_openai import ChatOpenAI
        
        if not OPENAI_API_KEY:
            raise ValueError("OPEN_API_KEY_VSE_LLM должен быть установлен")
        
        _llm = ChatOpenAI(
            model=MODEL_ID,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
        )
    
    return _llm




# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Новые переменные окружения для OpenAI-совместимого API
# OPENAI_API_KEY = os.getenv("OPEN_API_KEY_VSE_LLM")
# OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.vsellm.ru/v1")
# MODEL_ID = os.getenv("MODEL_ID", "deepseek/deepseek-v3.2")
# MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))  # None по умолчанию (не ограничиваем)
# TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))

# _llm = None


# def get_llm():
#     """Возвращает кэшированный экземпляр ChatOpenAI."""
#     global _llm
    
#     if _llm is None:
#         from langchain_openai import ChatOpenAI
        
#         if not OPENAI_API_KEY:
#             raise ValueError(
#                 "OPEN_API_KEY_VSE_LLM должен быть установлен в .env"
#             )
        
#         _llm = ChatOpenAI(
#             model=MODEL_ID,
#             temperature=TEMPERATURE,
#             max_tokens=int(MAX_TOKENS) if MAX_TOKENS else None,
#             timeout=None,
#             max_retries=2,
#             api_key=OPENAI_API_KEY,
#             base_url=OPENAI_BASE_URL,
#         )
    
#     return _llm
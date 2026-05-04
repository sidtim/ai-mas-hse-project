import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPEN_API_KEY_VSE_LLM")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.vsellm.ru/v1")
MODEL_ID = os.getenv("MODEL_ID", "deepseek/deepseek-v3.2")
MAX_TOKENS = os.getenv("MAX_TOKENS")
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
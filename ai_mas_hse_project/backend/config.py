import os
from dotenv import load_dotenv

load_dotenv()

MODEL_ID = os.getenv("MODEL_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "512"))
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        import torch
        from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
        from huggingface_hub import login
        
        # Логинимся если есть токен
        if HUGGINGFACE_TOKEN:
            login(token=HUGGINGFACE_TOKEN)
        
        torch.cuda.empty_cache()
        
        pipeline = HuggingFacePipeline.from_model_id(
            model_id=MODEL_ID,
            task="text-generation",
            device=-1,
            pipeline_kwargs=dict(
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=True,
                temperature=0.7,
                repetition_penalty=1.1,
            ),
        )
        _llm = ChatHuggingFace(llm=pipeline)
    
    return _llm
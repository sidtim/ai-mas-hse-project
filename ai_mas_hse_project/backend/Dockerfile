FROM python:3.10-slim

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip
RUN pip install --no-cache-dir --upgrade pip

# Устанавливаем СНАЧАЛА numpy и torch (совместимые версии)
RUN pip install --no-cache-dir numpy==1.24.3
RUN pip install --no-cache-dir torch==2.0.1 --index-url https://download.pytorch.org/whl/cpu

# Устанавливаем pandas
RUN pip install --no-cache-dir pandas

# Устанавливаем langchain-зависимости (совместимые версии)
RUN pip install --no-cache-dir \
    langchain-core==0.1.52 \
    langgraph==0.0.48 \
    langchain-huggingface==0.0.3 \
    langchain-openai>=0.1.0

# Остальные зависимости
RUN pip install --no-cache-dir \
    fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    pydantic==2.5.3 \
    python-dotenv==1.0.0 \
    transformers==4.37.2 \
    accelerate==0.26.1

# Копируем код
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
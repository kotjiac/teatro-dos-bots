# Imagem base
FROM python:3.11-slim

# Evita prompts interativos e reduz camadas
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Adiciona /app ao PYTHONPATH
ENV PYTHONPATH=/app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    libsndfile1 \
    python3-distutils \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do projeto
COPY requirements.txt .
RUN  pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia arquivos do projeto
COPY . .

# Expõe a porta do FastAPI
EXPOSE 8000

# Comando padrão
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]


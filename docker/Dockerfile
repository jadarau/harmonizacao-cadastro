# Dockerfile para a aplicação Harmonização
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências Python
COPY requirements.txt .

# Instala pymongo e motor primeiro para evitar conflitos
RUN pip install --no-cache-dir pymongo motor

# Instala o restante das dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Cria usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expõe a porta da aplicação
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/v1/healthz || exit 1

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema se necessário
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .
# Copiar o .env para dentro da imagem (cuidado: evita incluir segredos)
COPY .env ./

# Expor a porta
EXPOSE 8000

# Comando para executar a aplicação
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]

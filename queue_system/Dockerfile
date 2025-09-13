FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema se necessário
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências (se existir)
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Comando para executar a aplicação
CMD ["python", "run.py"]

# Usa imagem oficial do Python
FROM python:3.13-slim

# Define diretório de trabalho dentro do container
WORKDIR /app

# Evita criar arquivos temporários de cache como root
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Atualiza pip e instala dependências essenciais do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .

# Instala dependências Python
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copia o restante do projeto
COPY . .

# Porta (opcional, não obrigatória para bots)
EXPOSE 8080

# Comando para rodar o bot
CMD ["python", "bot.py"]

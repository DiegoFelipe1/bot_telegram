# Use a imagem oficial do Python 3.13 slim (mais leve)
FROM python:3.12-slim

# Variáveis de ambiente para não criar buffers e deixar logs no stdout
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

# Atualiza e instala dependências do sistema necessárias para psycopg2 e outras libs
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Cria diretório do app
WORKDIR /app

# Copia requirements.txt e instala as dependências
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copia todo o código
COPY . .

# Comando para rodar o bot
CMD ["python", "bot.py"]

# Escolhe a imagem oficial do Python
FROM python:3.13-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Atualiza pip e instala dependências
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Expõe a porta (não é obrigatória para bots, mas boa prática)
EXPOSE 8080

# Comando para rodar seu bot
CMD ["python", "bot.py"]

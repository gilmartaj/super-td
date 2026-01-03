# Usa uma imagem leve do Python
FROM python:3.10-slim

# Evita que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências de sistema necessárias para curl-cffi e outras libs
RUN apt-get update && apt-get install -y \
    build-essential \
    libcurl4-openssl-dev \
    ssl-cert \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o conteúdo do projeto (incluindo seus módulos locais)
COPY . .

ENV TZ="America/Bahia"

# Comando para rodar o script
CMD ["python", "main.py"]
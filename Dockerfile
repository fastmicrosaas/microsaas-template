# Imagen base ligera de Python
FROM python:3.11-alpine

# Evitar archivos .pyc y habilitar logs inmediatos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apk update && apk add --no-cache gcc musl-dev libpq postgresql-dev

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto
EXPOSE 8000

# Comando para aplicar migraciones y levantar servidor
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

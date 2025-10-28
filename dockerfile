# Usa tu imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Configurar la zona horaria (Buena práctica, se mantiene)
RUN apt-get update && apt-get install -y tzdata \
    && rm -rf /var/lib/apt/lists/*
ENV TZ=America/Argentina/Buenos_Aires
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copiar el contenido del proyecto al contenedor
COPY . /app

# Instalar dependencias (asumiendo que 'gunicorn' está en requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# El watchdog no es necesario en producción, se omite.

# Exponer el puerto (es solo informativo en Cloud Run, pero se mantiene)
EXPOSE 8080

# Comando de inicio: Usar el formato de lista (exec form)
# 1. Se elimina 'sh -c'
# 2. Se elimina '--reload' y 'watchdog'
# 3. Se usa $PORT para que Gunicorn escuche en el puerto que Cloud Run asigne.
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "main:app"]
# NOTA: Reemplaza "main:app" si tu objeto Flask no está en main.py o se llama diferente.
# Ejemplo: Si la app está en 'app/main.py' y se llama 'app', usa: "app.main:app"
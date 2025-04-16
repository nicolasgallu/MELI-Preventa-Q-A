FROM python:3.9-slim

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Configurar la zona horaria
RUN apt-get update && apt-get install -y tzdata
ENV TZ=America/Argentina/Buenos_Aires
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copiar el contenido del proyecto al contenedor
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Instalar watchdog para monitoreo
RUN pip install watchdog

# Exponer el puerto
EXPOSE 5000

# Comando de inicio con timeout ajustado
CMD ["gunicorn", "-w", "4", "-k", "gthread", "--threads", "4", "--timeout", "600", "-b", "0.0.0.0:5000", "main:app"]

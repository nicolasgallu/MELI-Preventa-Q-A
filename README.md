# Webhook de MercadoLibre - Servidor Flask

Este proyecto tiene como objetivo crear un servidor que escuche notificaciones enviadas por el webhook de MercadoLibre, habilitando exclusivamente las notificaciones de preguntas y que las mismas sean respondidas por un modelo LLM.
El modelo LLM primero clasifica la pregunta en un tipo de categoria, luego otro modelo responde la pregunta y un tercero audita la respuesta en busca de incongruencias, en caso de que la respuesta caiga en un FALLBACK se deriva la pregunta al dueño de la cuenta caso contrario se publcia la respuesta del modelo LLM, tambien hacemos uso de un modelo SWITCH, en caso de que el modelo A falle se utiliza el B (deepseek de preferencia por temas de coste economico, caso contrario pasamos a GPT 4)

## Tecnologías Utilizadas
- **Flask**: Framework de Python para levantar el servidor.
- **BigQuery (GBQ)**: Para almacenar y gestionar la información relacionada con las preguntas y respuestas.
- **APIs de LLMs (DeepSeek y OpenAI)**: Para generar respuestas automatizadas basadas en IA.
- **Gmail SMTP**: Para enviar notificaciones por correo electrónico.

---

## Configuración del Proyecto

Para que el proyecto funcione correctamente, es necesario realizar algunos pasos de configuración.

### 1. Crear el archivo `.env`
En el directorio principal del proyecto, crea un archivo llamado `.env` y agrega las siguientes variables de entorno:

```ini
# LLMs
DEEPSEEK_API_KEY="XXX"
OPENAI_API_KEY="XXX"

# MercadoLibre
CLIENT_ID="de la cuenta de meli"
CLIENT_SECRET="de la cuenta de meli"

# BigQuery (GBQ)
DATASET_ID="ID del dataset del proyecto"

## --> Tabla de Credenciales
TABLE_CREDENTIALS="tabla de GBQ donde se encuentra el token de acceso para responder preguntas en la API de Meli"

## --> Tabla de Inventario
TABLE_INVENTORY="tabla de GBQ donde existe la metadata del item por el cual se pregunta"

## --> Tabla de Preguntas Procesadas
TABLE_QA_INIT="tabla de GBQ donde se registran las preguntas ya procesadas para no volver a procesar"

## --> Tabla de Registro de Preguntas y Respuestas con LLM
TABLE_QA_LLM="tabla de GBQ donde se registra el consumo de recursos económicos del LLM"

## --> Tabla de Prompts
TABLE_PROMPTS="tabla de GBQ donde se alojan los prompts a utilizar"

# Correo para Notificaciones al Cliente
SENDER_EMAIL="email que envía el mensaje al dueño"
SENDER_PASSWORD="código de app del email que envía el mensaje (se obtiene desde Gmail)"
RECIPIENT_EMAIL="email del cliente para notificarle sobre preguntas no respondidas"

# Logger
LOG_LEVEL=DEBUG
```

### 2. Agregar credenciales de BigQuery
En la carpeta `config/`, debes incluir el archivo JSON con las credenciales de la cuenta de servicio de BigQuery. Este archivo es necesario para tener permisos de lectura y escritura en el proyecto de GBQ.

**Nombre del archivo:** `bigquery-service-account.json`

---

## Instalación y Ejecución

### 1. Clonar el repositorio
```sh
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
```

### 2. Crear un entorno virtual y activarlo
```sh
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate    # Windows
```

### 3. Instalar dependencias
```sh
pip install -r requirements.txt
```

### 4. Ejecutar el servidor
```sh
python app.py
```

---

## Contribuciones
Si deseas contribuir, por favor abre un issue o un pull request con mejoras o correcciones.

---





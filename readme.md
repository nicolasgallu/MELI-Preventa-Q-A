
---

# 🚀 Webhook de MercadoLibre – Servidor Flask

Este proyecto crea un **servidor Flask** que escucha notificaciones enviadas por el **webhook de MercadoLibre**, manejando **exclusivamente las notificaciones de preguntas** para procesarlas y responderlas automáticamente.

---

## 🛠️ Tecnologías Utilizadas

* 🐍 **Flask** → Framework de Python para levantar el servidor.
* 📊 **BigQuery (GBQ)** → Almacenamiento y gestión de datos de preguntas y respuestas.
* 🤖 **APIs de LLMs (DeepSeek y OpenAI)** → Generación de respuestas automáticas con IA.
* 📧 **Gmail SMTP** → Envío de notificaciones por correo electrónico.

---

## ⚙️ Configuración del Proyecto

Para que todo funcione correctamente, seguí estos pasos:

### 1️⃣ Crear el archivo `.env`

En el directorio raíz, crea un archivo `.env` con las siguientes variables:

```ini
# 🔑 LLMs
DEEPSEEK_API_KEY="XXX"
OPENAI_API_KEY="XXX"

# 🛒 MercadoLibre
CLIENT_ID="de la cuenta de meli"
CLIENT_SECRET="de la cuenta de meli"

# 🗄️ BigQuery (GBQ)
DATASET_ID="ID del dataset del proyecto"

## Tablas
TABLE_CREDENTIALS="tabla GBQ con token de acceso"
TABLE_INVENTORY="tabla GBQ con metadata del item"
TABLE_QA_INIT="tabla GBQ de preguntas procesadas"
TABLE_QA_LLM="tabla GBQ con registro de uso del LLM"
TABLE_PROMPTS="tabla GBQ con prompts"

# 📬 Correo de Notificaciones
SENDER_EMAIL="email remitente"
SENDER_PASSWORD="código de app de Gmail"
RECIPIENT_EMAIL="email del cliente"

# 📜 Logger
LOG_LEVEL=DEBUG
```

---

### 2️⃣ Agregar credenciales de BigQuery

En la carpeta `config/` incluir el archivo JSON con las credenciales de la cuenta de servicio de BigQuery:

📄 **Nombre:** `bigquery-service-account.json`
💡 Necesario para lectura/escritura en GBQ.

---

## ▶️ Instalación y Ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate    # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar el servidor

```bash
python app.py
```

---

## 🤝 Contribuciones

Si querés mejorar el proyecto, abrí un **issue** o enviá un **pull request** con tus cambios.

---

## 📄 Licencia

Este proyecto está bajo licencia **MIT**. Más detalles en el archivo `LICENSE`.

---


# 🚀 E-commerce AI Support Bot

Motor de respuestas automáticas para centralizar y automatizar la atención al cliente en **MercadoLibre** y **WhatsApp (Whapi)**. Utiliza **Flask** y modelos de IA (**DeepSeek** y **OpenAI**) para generar respuestas humanas y precisas.

### 🛠️ Stack Tecnológico

* **Framework:** Flask (Python)
* **IA:** DeepSeek API & OpenAI API (GPT-4o/o1)
* **DB:** Cloud SQL (MySQL) con SQLAlchemy
* **Mensajería:** Whapi.cloud
* **Cloud:** Google Cloud Secret Manager

### 🗄️ Base de Datos

El sistema utiliza las siguientes tablas principales:

* `questions`: Registro de preguntas entrantes.
* `items`: Metadata de productos.
* `ai_responses`: Log de razonamiento y respuestas de la IA.
* `product_catalog_sync`: Stock y nombres sincronizados.
* `prompts`: Instrucciones dinámicas para los agentes de IA.

### ⚙️ Configuración (.env)

Crea un archivo `.env` con las siguientes variables:

```ini
# IA
OPENAI_API_KEY="xxx"
DEEPSEEK_API_KEY="xxx"

# WHAPI
TOKEN_WHAPI="xxx"
PHONE="xxx"

# DATABASE (Cloud SQL)
INSTANCE_DB="xxx"
USER_DB="xxx"
PASSWORD_DB="xxx"
NAME_DB="xxx"

# GOOGLE & MELI
PROJECT_ID="xxx"
SECRET_ID="xxx"
USER_ID="xxx"

```

> **Nota:** En caso de error, el bot responde por defecto: *"Consultar con humano"*.
# 🗳️ SentiVote-WebApp – Análisis de Sentimiento de Opiniones Electorales

SentiVote es una aplicación web que permite analizar el sentimiento de opiniones sobre candidatos electorales, usando datos de redes sociales. Utiliza un modelo de NLP entrenado en español (BETO) para clasificar los tweets como positivos, negativos o neutrales.

---

## 📁 Estructura del Proyecto

    SentiVote-WebApp/
    │
    ├── backend/                  # Servidor Flask y modelo de análisis de sentimiento
    │   ├── app.py
    │   └── ../data/              # Tweets en formato JSON
    │       └── corpus_completo.json
    │
    ├── frontend/                 # Aplicación React
    │   ├── src/
    │   │   ├── components/
    |   |   ├──types
    │   │   └── App.jsx
    │   └── package.json
    │
    └── README.md                 # Este archivo

---

## 🚀 Instalación y Ejecución

### 🖥️ Frontend (React)

    cd sentivote
    npm install
    npm run dev

La app se ejecutará por defecto en: http://localhost:5173

---

### ⚙️ Backend (Flask)

#### Crear y activar entorno virtual

    cd backend
    py -3 -m venv .venv
    .venv\Scripts\activate

#### Instalar dependencias

    pip install -r requirements.txt

#### Configura las variables de entorno

    touch .env

#### Ejecutar el servidor

    python main.py

El backend estará activo en: http://localhost:5000

---

> ✅ Asegúrate de que el archivo `corpus_data.json` esté ubicado en la carpeta `data/` al mismo nivel del backend.

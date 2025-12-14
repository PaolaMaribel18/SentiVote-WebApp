# 🗳️ SentiVote-WebApp – Análisis de Sentimiento de Opiniones Electorales

SentiVote es una aplicación web que permite analizar el sentimiento de opiniones sobre candidatos electorales, usando datos de redes sociales. Utiliza un modelo de lenguaje BERT preentrenado en español (pysentimiento/robertuito) ajustado (fine-tuned) con un corpus político específico, y lo combina con un sistema de refuerzo basado en diccionarios temáticos (Manejo de Negación) para ofrecer mayor precisión en el dominio electoral.

---

## 📁 Estructura del Proyecto

SentiVote-WebApp/
│
├── backend/                          # API Flask, Lógica Híbrida (Diccionario + ML)
│   ├── data/
│   │   └── corpus.json               # Corpus consolidado de publicaciones y comentarios
│   └── main.py                       # Servidor Flask y Lógica de Análisis
│
├── fineTuning/                       # Scripts y modelo para el Fine-Tuning
│   ├── modelo_final/                 # Modelo fine-tuned guardado (Robertuito/BETO)
│   └── finetuning.ipynb              # Notebook de entrenamiento
│
├── frontend/                         # Aplicación Web (React/TypeScript)
│   ├── src/
│   │   ├── components/               # Componentes React (Formularios, Tweets, Gráficos)
│   │   └── App.tsx                   # Componente Principal
│   └── package.json
│
├── webScraping/                      # Scripts de recolección y pre-procesamiento
│   └── ...                           # Scripts de Python
│
└── README.md
---

## 🚀 Instalación y Ejecución

### 🖥️ Frontend (React)

#### Navega a la carpeta del frontend:

    cd frontend

#### Instala las dependencias:

    npm install

#### Ejecuta la aplicación:

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

✅ IMPORTANTE:

Asegúrate de que el modelo fine-tuned esté ubicado en backend/fineTuning/modelo_final.

Asegúrate de que el archivo corpus.json esté en backend/data/.
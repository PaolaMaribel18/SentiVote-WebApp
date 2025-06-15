# SentiVote-WebApp
# 🗳️ SentiVote – Análisis de Sentimiento de Opiniones Electorales

SentiVote es una aplicación web que permite analizar el sentimiento de opiniones sobre candidatos electorales, usando datos de redes sociales. Utiliza un modelo de NLP entrenado en español (BETO) para clasificar los tweets como positivos, negativos o neutrales.

---

## 📁 Estructura del Proyecto

SentiVote-WebApp/
│
├── backend/ # Servidor Flask y modelo de análisis de sentimiento
│ ├── app.py
│ └── ../data/ # Tweets simulados en formato JSON
│ └── tweets_simulados.json
│
├── frontend/ # Aplicación React
│ ├── src/
│ │ ├── components/
│ │ └── App.jsx
│ └── package.json
│
└── README.md # Este archivo


## Frontend (React)
cd sentivote
npm install
npm run dev

## Backend (Flask)
Crear ambiente
> cd backend
> py -3 -m venv .venv

Activar ambiente
>.venv\Scripts\activate


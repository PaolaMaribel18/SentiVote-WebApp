import { useState, useEffect } from "react";
import Busqueda from "./components/Busqueda";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser, faCity, faPersonBooth } from "@fortawesome/free-solid-svg-icons";
import axios from "axios";

function App() {
  const [tweets, setTweets] = useState([]);
  const [resultados, setResultados] = useState([]);

useEffect(() => {
  axios
    .get("http://localhost:5000/api/tweets")
    .then((res) => setTweets(res.data))
    .catch((err) => console.error("Error al obtener tweets:", err));
}, []);

const filtrarTweets = async ({ ciudad, nombre }) => {
  const filtrados = tweets.filter(
    (t) =>
      t.ciudad.toLowerCase() === ciudad.toLowerCase() &&
      t.nombre.toLowerCase() === nombre.toLowerCase()
  );

  console.log("Filtrados:", filtrados); // <--- Agregado para verificar

  setResultados([]);

  if (filtrados.length === 0) return;

  try {
    const response = await axios.post("http://localhost:5000/analizar", {
      textos: filtrados.map((t) => t.texto),
    });

    console.log("Respuesta backend:", response.data); // <--- Agregado

    const analizados = filtrados.map((t, i) => ({
      ...t,
      sentimiento: response.data[i].sentimiento,
      confianza: response.data[i].confianza,
    }));

    setResultados(analizados);
  } catch (error) {
    console.error("Error al conectar con el backend:", error);
  }
};


  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 to-white p-6">
      <h1 className="text-4xl font-extrabold text-indigo-800 text-center mb-8">
        <FontAwesomeIcon icon={faPersonBooth} className="mr-2 text-indigo-600" />
        SentiVote <span className="text-base text-gray-500">(v1 Prototipo)</span>
      </h1>

      <div className="max-w-2xl mx-auto">
        <Busqueda onFiltrar={filtrarTweets} />

        <div className="mt-10">
          {resultados.length > 0 ? (
            <div className="space-y-4">
              {resultados.map((t, i) => (
                <div key={i} className="bg-white rounded-xl p-4 shadow hover:shadow-lg transition">
                  <div className="flex items-center gap-3 mb-2">
                    <FontAwesomeIcon icon={faUser} className="text-indigo-500" />
                    <span className="font-semibold text-gray-800">@{t.usuario}</span>
                  </div>
                  <p className="text-gray-700">{t.texto}</p>
                  <div className="mt-2 text-sm text-gray-500 flex items-center gap-1">
                    <FontAwesomeIcon icon={faCity} />
                    <span>{t.ciudad}</span>
                  </div>
                  {t.sentimiento && (
                    <div className="mt-2 text-sm">
                      <span className="font-semibold text-indigo-600">Sentimiento:</span>{" "}
                      {t.sentimiento} ({(t.confianza * 100).toFixed(1)}%)
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 italic">No hay resultados para la búsqueda.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

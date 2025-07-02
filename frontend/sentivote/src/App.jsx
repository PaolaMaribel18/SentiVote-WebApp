import { useState, useEffect } from "react";
import Busqueda from "./components/Busqueda";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser, faPersonBooth, faComments } from "@fortawesome/free-solid-svg-icons";
import axios from "axios";

function App() {
  const [tweets, setTweets] = useState([]);
  const [resultados, setResultados] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [tiempo, setTiempo] = useState(null);



  useEffect(() => {
    axios
      .get("http://localhost:5000/api/tweets")
      .then((res) => setTweets(res.data))
      .catch((err) => console.error("Error al obtener tweets:", err));
  }, []);

  const filtrarTweets = async ({ nombre }) => {
    const nombreBuscado = nombre.toLowerCase();

    const inicio = performance.now(); // 🕒 inicio
    setCargando(true);
    setResultados([]);
    setTiempo(null);
    console.log("Nombre buscado:", nombreBuscado); // 

    // Filtrar por coincidencia en campo "candidato"
    const filtrados = tweets.filter((t) =>
      t.candidato.toLowerCase().includes(nombreBuscado)
    );

    setResultados([]);

    if (filtrados.length === 0) return;

    try {
      const response = await axios.post("http://localhost:5000/analizar", {
        textos: filtrados.map((t) => t.texto_comentario_limpio),
      });

      console.log("Respuesta backend:", response.data); // <--- Agregado


      const analizados = filtrados.map((t, i) => ({
        ...t,
        sentimiento: response.data[i]?.sentimiento || "NEU",
        confianza: response.data[i]?.confianza ?? 0,
      }));

      setResultados(analizados);
    } catch (error) {
      console.error("Error al conectar con el backend:", error);
    } finally {
      const fin = performance.now();
      setTiempo(((fin - inicio) / 1000).toFixed(2)); // segundos con 2 decimales
      setCargando(false);
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
          <div className="flex justify-between items-center text-sm text-gray-600 mb-4">
            {cargando ? (
              <p className="italic animate-pulse">⏳ Procesando análisis...</p>
            ) : (
              tiempo && <p className="italic">✅ Tiempo de consulta: {tiempo} segundos</p>
            )}
          </div>

          {resultados.length > 0 ? (
            <div className="space-y-4">
              {resultados.map((t, i) => (
                <div key={i} className="bg-white rounded-xl p-4 shadow hover:shadow-lg transition">
                  <div className="flex items-center gap-3 mb-2">
                    <FontAwesomeIcon icon={faUser} className="text-indigo-500" />
                    <span className="font-semibold text-gray-800">{t.usuario}</span>
                  </div>
                  <p className="text-gray-700 italic mb-1">
                    <span className="font-semibold text-indigo-600">Tweet:</span> "{t.texto}"
                  </p>
                  <span className="font-semibold text-indigo-400"><FontAwesomeIcon icon={faComments} /> Comentario:</span> "{t.texto_comentario}"
                  {t.sentimiento && (
                    <div className="mt-2 text-sm">
                      <span className="font-semibold text-indigo-600">Sentimiento:</span>{" "}
                      {t.sentimiento} ({(t.confianza * 100).toFixed(1)}%)
                    </div>
                  )}
                </div>
              ))}

            </div>
          ) : !cargando ? (
            <p className="text-center text-gray-500 italic">No hay resultados para la búsqueda.</p>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export default App;

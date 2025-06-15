import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser, faSearch } from "@fortawesome/free-solid-svg-icons";

export default function Busqueda({ onFiltrar }) {
  const [nombre, setNombre] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Buscando candidato:", nombre); // 
    onFiltrar({nombre });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-6 bg-white p-6 rounded-2xl shadow-md border border-gray-200"
    >

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          <FontAwesomeIcon icon={faUser} className="text-indigo-500 mr-2" />
          Nombre del candidato
        </label>
        <input
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
          type="text"
          placeholder="Ej: CandidatoX"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
        />
      </div>

      <button
        className="w-full flex items-center justify-center gap-2 bg-indigo-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-indigo-700 transition"
        type="submit"
      >
        <FontAwesomeIcon icon={faSearch} />
        Buscar Opiniones
      </button>
    </form>
  );
}

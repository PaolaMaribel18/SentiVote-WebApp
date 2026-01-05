// frontend/src/components/CompareView.tsx
import React, { useState } from 'react';
import { Users, BarChart2, ArrowRight, Activity, MessageSquare } from 'lucide-react';
import { SentimentChart } from './SentimentChart';
import { BackendResponse, SentimentAnalysis } from '../types';

// Lista de candidatos basada en los archivos del corpus
const CANDIDATES = [
  "Andrea Gonzalez Nader",
  "Carlos Rabascall",
  "Daniel Noboa",
  "Enrique Gomez",
  "Francesco Tabacchi",
  "Henry Cucalon",
  "Henry Kronfle",
  "Ivan Saquicela",
  "Jimmy Jairala",
  "Jorge Escala",
  "Juan Ivan Cueva",
  "Leonidas Iza",
  "Luisa Gonzalez",
  "Pedro Granja",
  "Victor Araus",
  "Wilson Gomez Vascones"
];

const API_BASE_URL = 'http://localhost:5000';

export function CompareView() {
  const [candidateA, setCandidateA] = useState<string>('');
  const [candidateB, setCandidateB] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<{
    a: SentimentAnalysis | null;
    b: SentimentAnalysis | null;
  }>({ a: null, b: null });
  const [error, setError] = useState<string | null>(null);

  // Reutilizamos la lógica de conversión para mantener consistencia con App.tsx
  const convertToAnalysis = (data: BackendResponse, query: string): SentimentAnalysis => {
    const totalPosts = data.publicaciones.length;
    const allComments = data.publicaciones.flatMap(p => p.comentarios);

    const countSentiment = (list: any[], key: string, val: 'POS' | 'NEG' | 'NEU') =>
      list.filter(x => String(x[key]) === val).length;

    const pos = countSentiment(data.publicaciones, 'sentimiento_publicacion', 'POS') +
                countSentiment(allComments, 'sentimiento_comentario', 'POS');
    const neg = countSentiment(data.publicaciones, 'sentimiento_publicacion', 'NEG') +
                countSentiment(allComments, 'sentimiento_comentario', 'NEG');
    const neu = countSentiment(data.publicaciones, 'sentimiento_publicacion', 'NEU') +
                countSentiment(allComments, 'sentimiento_comentario', 'NEU');

    return {
      id: Date.now().toString(),
      query,
      createdAt: new Date().toISOString(),
      tweets: [], // No necesitamos los tweets individuales para la vista resumen
      summary: {
        total: totalPosts + allComments.length,
        positive: pos,
        negative: neg,
        neutral: neu,
        uniqueUsers: { positive: 0, negative: 0, neutral: 0 } // Simplificado
      },
      wordClouds: { positive: [], negative: [], neutral: [] }
    };
  };

  const handleCompare = async () => {
    if (!candidateA || !candidateB) return;
    setLoading(true);
    setError(null);

    try {
      const [resA, resB] = await Promise.all([
        fetch(`${API_BASE_URL}/analizar`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: candidateA, platforms: [] })
        }),
        fetch(`${API_BASE_URL}/analizar`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: candidateB, platforms: [] })
        })
      ]);

      const dataA: BackendResponse = await resA.json();
      const dataB: BackendResponse = await resB.json();

      setResults({
        a: convertToAnalysis(dataA, candidateA),
        b: convertToAnalysis(dataB, candidateB)
      });

    } catch (err) {
      setError("Error al obtener datos de comparación. Verifique la conexión.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  interface StatCardProps {
    label: string;
    valA: number;
    valB: number;
    icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
    colorClass?: string;
  }

  const StatCard: React.FC<StatCardProps> = ({ label, valA, valB, icon: Icon, colorClass = 'text-gray-600' }) => {
    const diff = valA - valB;
    const winner = diff > 0 ? 'A' : diff < 0 ? 'B' : 'Tie';
    const total = valA + valB;
    const percentA = total > 0 ? Math.round((valA / total) * 100) : 50;
    const percentB = total > 0 ? Math.round((valB / total) * 100) : 50;

    return (
      <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${colorClass} bg-opacity-10`}>
              <Icon className={`w-5 h-5 ${colorClass}`} />
            </div>
            <span className="text-gray-600 font-medium">{label}</span>
          </div>
          <div className="text-sm text-gray-400">{winner === 'Tie' ? 'Empate' : `Ganador: ${winner}`}</div>
        </div>

        <div className="flex items-center gap-4 justify-between">
          <div className={`text-lg font-bold ${winner === 'A' ? 'text-blue-600' : 'text-gray-400'}`}>
            {valA.toLocaleString()} <span className="text-xs text-gray-400 ml-2">({percentA}%)</span>
          </div>
          <div className="flex-1 mx-3">
            <div className="h-2 bg-gray-100 rounded overflow-hidden">
              <div
                className="h-2 rounded"
                style={{
                  width: `${percentA}%`,
                  background: 'linear-gradient(90deg, #3b82f6, #8b5cf6)'
                }}
                aria-hidden
              />
            </div>
            <div className="h-2 mt-1" style={{ display: 'none' }} /> {/* espacio visual si se desea más separación */}
          </div>
          <div className={`text-lg font-bold ${winner === 'B' ? 'text-purple-600' : 'text-gray-400'}`}>
            {valB.toLocaleString()} <span className="text-xs text-gray-400 ml-2">({percentB}%)</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header y Controles */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
          <Users className="w-6 h-6 text-blue-600" />
          Comparativa de Candidatos
        </h2>

        <div className="flex flex-col md:flex-row gap-4 items-end">
          <div className="flex-1 w-full">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Candidato A</label>
            <select
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-blue-50"
              value={candidateA}
              onChange={(e) => setCandidateA(e.target.value)}
            >
              <option value="">Seleccionar...</option>
              {CANDIDATES.filter(c => c !== candidateB).map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          <div className="flex items-center justify-center pb-3">
            <div className="bg-gray-100 p-2 rounded-full">
              <span className="font-bold text-gray-500">VS</span>
            </div>
          </div>

          <div className="flex-1 w-full">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Candidato B</label>
            <select
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 bg-purple-50"
              value={candidateB}
              onChange={(e) => setCandidateB(e.target.value)}
            >
              <option value="">Seleccionar...</option>
              {CANDIDATES.filter(c => c !== candidateA).map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          <button
            onClick={handleCompare}
            disabled={loading || !candidateA || !candidateB}
            className="w-full md:w-auto px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-bold hover:shadow-lg disabled:opacity-50 transition-all flex items-center justify-center gap-2"
          >
            {loading ? <Activity className="animate-spin" /> : <ArrowRight />}
            Comparar
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">
          {error}
        </div>
      )}

      {/* Resultados */}
      {results.a && results.b && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

          {/* Métricas Clave */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <StatCard
              label="Total Interacciones"
              valA={results.a.summary.total}
              valB={results.b.summary.total}
              icon={MessageSquare}
              colorClass="text-indigo-600"
            />
            <StatCard
              label="Menciones Positivas"
              valA={results.a.summary.positive}
              valB={results.b.summary.positive}
              icon={Activity}
              colorClass="text-green-600"
            />
            <StatCard
              label="Menciones Negativas"
              valA={results.a.summary.negative}
              valB={results.b.summary.negative}
              icon={Activity}
              colorClass="text-red-600"
            />
            <StatCard
              label="Sentimiento Neto (Pos - Neg)"
              valA={results.a.summary.positive - results.a.summary.negative}
              valB={results.b.summary.positive - results.b.summary.negative}
              icon={BarChart2}
              colorClass="text-orange-600"
            />
          </div>

          {/* Gráficos Lado a Lado */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-xl border border-blue-100 shadow-sm relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-blue-500"></div>
              <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">{candidateA}</h3>
              <SentimentChart data={results.a.summary} />
            </div>

            <div className="bg-white p-6 rounded-xl border border-purple-100 shadow-sm relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-purple-500"></div>
              <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">{candidateB}</h3>
              <SentimentChart data={results.b.summary} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
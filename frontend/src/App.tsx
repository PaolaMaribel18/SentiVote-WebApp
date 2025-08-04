import React, { useState } from 'react';
import { BarChart3, Brain, Globe, Users } from 'lucide-react';
import { SearchForm } from './components/SearchForm';
import { SentimentCard } from './components/SentimentCard';
import { TweetCard } from './components/TweetCard';
import { SentimentChart } from './components/SentimentChart';
import { ReportGenerator } from './components/ReportGenerator';
import { SearchFilters, SentimentAnalysis } from './types';

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPersonBooth } from "@fortawesome/free-solid-svg-icons";

// Configuración de la API
const API_BASE_URL = 'http://localhost:5000';

// Interfaces para los datos del backend
interface BackendComment {
  id_comentario: string;
  texto_comentario: string;
  sentimiento_comentario: 'POS' | 'NEG' | 'NEU';
  confianza_comentario: number;
}

interface BackendPost {
  id_post: string;
  candidato: string;
  texto: string;
  sentimiento_publicacion: 'POS' | 'NEG' | 'NEU';
  confianza_publicacion: number;
  comentarios: BackendComment[];
  sentimiento_comentarios: 'POS' | 'NEG' | 'NEU';
  confianza_comentarios: number;
  sentimiento_final: 'POS' | 'NEG' | 'NEU';
  confianza_final: number;
}

interface BackendResponse {
  publicaciones: BackendPost[];
  wordcloud: {
    general: string;
    por_sentimiento: {
      POS: { imagen: string; palabras: Record<string, number> } | null;
      NEG: { imagen: string; palabras: Record<string, number> } | null;
      NEU: { imagen: string; palabras: Record<string, number> } | null;
    };

  }; total_textos_analizados: number;
}

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState<SentimentAnalysis | null>(null);
  const [backendPosts, setBackendPosts] = useState<BackendPost[]>([]);
  const [wordcloudImage, setWordcloudImage] = useState<BackendResponse['wordcloud'] | null>(null);
  const [conclusion, setConclusion] = useState<string | null>(null);

  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (filters: SearchFilters) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/analizar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: filters.query,
          dateFrom: filters.dateFrom,
          dateTo: filters.dateTo,
          platforms: filters.platforms,
          minEngagement: filters.minEngagement
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error HTTP: ${response.status}`);
      }

      const backendData: BackendResponse = await response.json();

      // Guardar los datos del backend
      setBackendPosts(backendData.publicaciones);

      // Generar la conclusión usando el backend
      const palabrasFrecuentes = {
        POS: backendData.wordcloud.por_sentimiento.POS?.palabras ?? {},
        NEG: backendData.wordcloud.por_sentimiento.NEG?.palabras ?? {},
        NEU: backendData.wordcloud.por_sentimiento.NEU?.palabras ?? {}
      };

      console.log("Enviando a /conclusiones:", {
        query: filters.query,
        wordclouds: palabrasFrecuentes
      });

      try {
        const conclusionResponse = await fetch(`${API_BASE_URL}/conclusiones`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: filters.query,
            wordclouds: palabrasFrecuentes
          })
        });

        const conclusionData = await conclusionResponse.json();
        console.log("Respuesta del endpoint /conclusiones:", conclusionData);

        const conclusionText = conclusionData.conclusion ?? null;
        setConclusion(conclusionText);

        // ✅ Aquí generamos el análisis final con la conclusión real
        const convertedAnalysis = convertBackendDataToFrontend(
          backendData.publicaciones,
          filters.query,
          conclusionText
        );
        setCurrentAnalysis(convertedAnalysis);

      } catch (error) {
        console.warn("No se pudo generar la conclusión automáticamente.", error);

        // Aún generamos el análisis sin conclusión
        const convertedAnalysis = convertBackendDataToFrontend(
          backendData.publicaciones,
          filters.query,
          null
        );
        setCurrentAnalysis(convertedAnalysis);
      }

      // Guardar la imagen de la wordcloud
      setWordcloudImage({
        general: backendData.wordcloud.general,
        por_sentimiento: backendData.wordcloud.por_sentimiento
      });

    } catch (error) {
      console.error('Error al realizar la búsqueda:', error);
      setError(error instanceof Error ? error.message : 'Error desconocido');
    } finally {
      setIsLoading(false);
    }
  };

  const convertBackendDataToFrontend = (backendData: BackendPost[], query: string, conclusion?: string | null
  ): SentimentAnalysis => {
    // Contar todos los comentarios para el análisis general
    const allComments = backendData.flatMap(post => post.comentarios);

    // Calcular estadísticas basadas en publicaciones Y comentarios
    const totalPosts = backendData.length;
    const totalComments = allComments.length;
    const totalItems = totalPosts + totalComments;

    // Contar sentimientos de publicaciones
    const postSentiments = {
      positive: backendData.filter(post => post.sentimiento_publicacion === 'POS').length,
      negative: backendData.filter(post => post.sentimiento_publicacion === 'NEG').length,
      neutral: backendData.filter(post => post.sentimiento_publicacion === 'NEU').length
    };

    // Contar sentimientos de comentarios
    const commentSentiments = {
      positive: allComments.filter(comment => comment.sentimiento_comentario === 'POS').length,
      negative: allComments.filter(comment => comment.sentimiento_comentario === 'NEG').length,
      neutral: allComments.filter(comment => comment.sentimiento_comentario === 'NEU').length
    };

    // Combinar sentimientos
    const totalSentiments = {
      positive: postSentiments.positive + commentSentiments.positive,
      negative: postSentiments.negative + commentSentiments.negative,
      neutral: postSentiments.neutral + commentSentiments.neutral
    };

    // Crear tweets ficticios solo para mantener compatibilidad con el frontend existente
    const dummyTweets = backendData.map(post => ({
      id: post.id_post,
      text: post.texto,
      user: {
        name: post.candidato,
        username: post.candidato.toLowerCase().replace(/\s+/g, '_'),
        avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(post.candidato)}&background=random`
      },
      platform: 'twitter' as const,
      sentiment: mapSentiment(post.sentimiento_final),
      confidence: post.confianza_final,
      engagement: {
        likes: Math.floor(Math.random() * 1000) + 10,
        retweets: Math.floor(Math.random() * 500) + 5,
        replies: post.comentarios.length
      },
      createdAt: new Date().toISOString()
    }));

    // Calcular el resumen
    const summary = {
      total: totalItems,
      positive: totalSentiments.positive,
      negative: totalSentiments.negative,
      neutral: totalSentiments.neutral,
      uniqueUsers: {
        positive: Math.floor(totalSentiments.positive * 0.8),
        negative: Math.floor(totalSentiments.negative * 0.9),
        neutral: Math.floor(totalSentiments.neutral * 0.85)
      }
    };

    // Ya no necesitamos generar wordClouds aquí, usamos el del backend
    const analysis: SentimentAnalysis = {
      id: Date.now().toString(),
      query: query,
      createdAt: new Date().toISOString(),
      tweets: dummyTweets, // Solo para compatibilidad
      summary: summary,
      wordClouds: {
        positive: [],
        negative: [],
        neutral: []
      }, // Vacío porque usamos la imagen del backend
      comments: [],
      conclusion: typeof conclusion === 'string' ? conclusion : String(conclusion)
    };

    return analysis;
  };

  const mapSentiment = (backendSentiment: string): 'positive' | 'negative' | 'neutral' => {
    switch (backendSentiment) {
      case 'POS':
        return 'positive';
      case 'NEG':
        return 'negative';
      case 'NEU':
      default:
        return 'neutral';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">

            <h1 className="text-4xl font-bold text-gray-900">

              <FontAwesomeIcon icon={faPersonBooth} className="mr-2 text-indigo-600" />
              SentiVote-Análisis de Sentimientos
            </h1>
          </div>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Plataforma de análisis socio-político del Ecuador mediante minería de datos en redes sociales
          </p>
        </header>

        {/* Search Form */}
        <SearchForm onSearch={handleSearch} isLoading={isLoading} />

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-8">
            <div className="flex items-center">
              <div className="text-red-600 mr-3">⚠️</div>
              <div>
                <h3 className="text-red-800 font-semibold">Error de conexión</h3>
                <p className="text-red-700 text-sm mt-1">
                  {error}. Asegúrate de que el servidor backend esté ejecutándose en http://localhost:5000
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {currentAnalysis && backendPosts.length > 0 && (
          <div className="space-y-8">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <SentimentCard
                type="positive"
                count={currentAnalysis.summary.positive}
                percentage={(currentAnalysis.summary.positive / currentAnalysis.summary.total) * 100}
                uniqueUsers={currentAnalysis.summary.uniqueUsers.positive}
              />
              <SentimentCard
                type="negative"
                count={currentAnalysis.summary.negative}
                percentage={(currentAnalysis.summary.negative / currentAnalysis.summary.total) * 100}
                uniqueUsers={currentAnalysis.summary.uniqueUsers.negative}
              />
              <SentimentCard
                type="neutral"
                count={currentAnalysis.summary.neutral}
                percentage={(currentAnalysis.summary.neutral / currentAnalysis.summary.total) * 100}
                uniqueUsers={currentAnalysis.summary.uniqueUsers.neutral}
              />
            </div>

            {/* Charts and Analytics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <SentimentChart data={currentAnalysis.summary} />

              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Métricas Generales
                </h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-gray-600 flex items-center">
                      <Globe className="w-4 h-4 mr-2" />
                      Total de Publicaciones:
                    </span>
                    <span className="font-semibold text-gray-900">{backendPosts.length}</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-gray-600 flex items-center">
                      <Globe className="w-4 h-4 mr-2" />
                      Total de Comentarios:
                    </span>
                    <span className="font-semibold text-gray-900">
                      {backendPosts.reduce((total, post) => total + post.comentarios.length, 0)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-gray-600 flex items-center">
                      <Users className="w-4 h-4 mr-2" />
                      Total de Análisis:
                    </span>
                    <span className="font-semibold text-gray-900">
                      {currentAnalysis.summary.total}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-gray-600">Consulta Analizada:</span>
                    <span className="font-semibold text-blue-600">"{currentAnalysis.query}"</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Wordcloud General del Backend */}
            {wordcloudImage && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-6 text-center">
                  Nube de Palabras General
                </h3>
                <div className="flex justify-center">
                  <img
                    src={`data:image/png;base64,${wordcloudImage?.general ?? ''}`}
                    alt="Nube de palabras general"
                    className="max-w-full h-auto rounded-lg shadow-md"
                    style={{ maxHeight: '500px' }}
                  />
                </div>
                <p className="text-sm text-gray-600 text-center mt-4">
                  Visualización de las palabras más frecuentes en todas las publicaciones y comentarios analizados
                </p>
              </div>
            )}
            {/* Wordclouds por Sentimiento */}
            {wordcloudImage?.por_sentimiento && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                {wordcloudImage.por_sentimiento.POS && (
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                    <h4 className="text-lg font-semibold text-green-600 text-center mb-2">Palabras Positivas</h4>
                    <img
                      src={`data:image/png;base64,${wordcloudImage.por_sentimiento.POS?.imagen ?? ''}`}
                      alt="Nube de palabras positivas"
                      className="max-w-full h-auto mx-auto rounded-md shadow"
                    />
                  </div>
                )}
                {wordcloudImage.por_sentimiento.NEG && (
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                    <h4 className="text-lg font-semibold text-red-600 text-center mb-2">Palabras Negativas</h4>
                    <img
                      src={`data:image/png;base64,${wordcloudImage.por_sentimiento.NEG?.imagen ?? ''}`}
                      alt="Nube de palabras positivas"
                      className="max-w-full h-auto mx-auto rounded-md shadow"
                    />
                  </div>
                )}
                {wordcloudImage.por_sentimiento.NEU && (
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                    <h4 className="text-lg font-semibold text-gray-600 text-center mb-2">Palabras Neutrales</h4>
                    <img
                      src={`data:image/png;base64,${wordcloudImage.por_sentimiento.NEU?.imagen ?? ''}`}
                      alt="Nube de palabras neutrales"
                      className="max-w-full h-auto mx-auto rounded-md shadow"
                    />
                  </div>
                )}
              </div>
            )}
            {/* Conclusión del Análisis */}
            {conclusion && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mt-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-4 text-center">
                  Conclusión del Análisis
                </h3>
                <p className="text-gray-700 text-lg text-center leading-relaxed whitespace-pre-line">
                  {conclusion}
                </p>
                <p className="text-xs text-gray-500 italic mt-2">
                  * Esta conclusión fue generada automáticamente por un modelo de lenguaje (Gemini Flash 2.0).
                </p>
              </div>
            )}



            {/* Posts List with Expandable Comments */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
              {/* Columna izquierda - Lista de publicaciones */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-[611.25px] flex flex-col">
                <h3 className="text-xl font-semibold text-gray-800 mb-4 flex-shrink-0">
                  Publicaciones Analizadas ({backendPosts.length})
                </h3>
                <div className="flex-1 overflow-y-auto space-y-4 pr-2">
                  {backendPosts.map(post => (
                    <TweetCard key={post.id_post} post={post} />
                  ))}
                </div>
              </div>

              {/* Columna derecha - Generador de reportes */}
              <div className="h-[600px]">
                <ReportGenerator analysis={currentAnalysis} backendPosts={backendPosts} />
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!currentAnalysis && !isLoading && !error && (
          <div className="text-center py-16">
            <Brain className="w-24 h-24 text-gray-300 mx-auto mb-6" />
            <h3 className="text-2xl font-semibold text-gray-700 mb-4">
              Comienza tu Análisis
            </h3>
            <p className="text-gray-500 max-w-md mx-auto">
              Ingresa el nombre de un candidato o palabra clave para iniciar el análisis de sentimientos
              en redes sociales sobre temas políticos del Ecuador.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
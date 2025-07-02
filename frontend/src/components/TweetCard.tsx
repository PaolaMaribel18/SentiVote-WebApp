import React, { useState } from 'react';
import { Heart, MessageCircle, Repeat2, Calendar, Gauge, ChevronDown, ChevronUp, User } from 'lucide-react';

interface Comment {
  id_comentario: string;
  texto_comentario: string;
  sentimiento_comentario: 'POS' | 'NEG' | 'NEU';
  confianza_comentario: number;
}

interface Post {
  id_post: string;
  candidato: string;
  texto: string;
  sentimiento_publicacion: 'POS' | 'NEG' | 'NEU';
  confianza_publicacion: number;
  comentarios: Comment[];
  sentimiento_comentarios: 'POS' | 'NEG' | 'NEU';
  confianza_comentarios: number;
  sentimiento_final: 'POS' | 'NEG' | 'NEU';
  confianza_final: number;
  fecha?: string; // Agregamos la fecha como opcional
}

interface TweetCardProps {
  post: Post;
}

export const TweetCard: React.FC<TweetCardProps> = ({ post }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const sentimentConfig = {
    POS: { color: 'text-green-600', bg: 'bg-green-100', label: 'Positivo' },
    NEG: { color: 'text-red-600', bg: 'bg-red-100', label: 'Negativo' },
    NEU: { color: 'text-gray-600', bg: 'bg-gray-100', label: 'Neutral' }
  };

  const getSentimentConfig = (sentiment: 'POS' | 'NEG' | 'NEU') => sentimentConfig[sentiment];

  const postSentiment = getSentimentConfig(post.sentimiento_publicacion);
  const finalSentiment = getSentimentConfig(post.sentimiento_final);

  // Función para formatear la fecha
  const formatDate = (fechaStr?: string): string => {
    if (!fechaStr) {
      // Si no hay fecha, usar la fecha actual como fallback
      return new Date().toLocaleDateString('es-EC');
    }

    try {
      // Intentar parsear la fecha que viene del backend
      const fecha = new Date(fechaStr);
      
      // Verificar si la fecha es válida
      if (isNaN(fecha.getTime())) {
        // Si no es una fecha válida, intentar otros formatos comunes
        // Formato DD/MM/YYYY o similar
        const partes = fechaStr.split(/[\/\-\.]/);
        if (partes.length === 3) {
          // Asumir formato DD/MM/YYYY
          const [dia, mes, año] = partes;
          const fechaParsed = new Date(parseInt(año), parseInt(mes) - 1, parseInt(dia));
          if (!isNaN(fechaParsed.getTime())) {
            return fechaParsed.toLocaleDateString('es-EC');
          }
        }
        
        // Si no se puede parsear, devolver la fecha original
        return fechaStr;
      }
      
      // Formatear la fecha válida
      return fecha.toLocaleDateString('es-EC', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (error) {
      console.warn('Error al formatear fecha:', fechaStr, error);
      // En caso de error, devolver la fecha original o fecha actual
      return fechaStr || new Date().toLocaleDateString('es-EC');
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all duration-200 w-full">
      {/* Publicación Principal */}
      <div className="p-4">
        <div className="flex items-start space-x-3">
          <img
            src={`https://ui-avatars.com/api/?name=${encodeURIComponent(post.candidato)}&background=random&size=48`}
            alt={post.candidato}
            className="w-10 h-10 rounded-full object-cover flex-shrink-0"
          />
          
          <div className="flex-1 min-w-0">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2 gap-2">
              <div className="flex items-center space-x-2 min-w-0">
                <h4 className="font-semibold text-gray-900 truncate text-sm">
                  {post.candidato}
                </h4>
                <span className="text-gray-500 text-xs truncate">
                  @{post.candidato.toLowerCase().replace(/\s+/g, '_')}
                </span>
                <div className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full whitespace-nowrap">
                  Post
                </div>
              </div>
              
              <div className="flex items-center space-x-1 flex-shrink-0">
                <div className={`${postSentiment.bg} ${postSentiment.color} px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap`}>
                  {postSentiment.label}
                </div>
                <div className={`${finalSentiment.bg} ${finalSentiment.color} px-2 py-1 rounded-full text-xs font-medium border whitespace-nowrap`}>
                  F: {finalSentiment.label}
                </div>
              </div>
            </div>
            
            <p className="text-gray-800 mb-3 leading-relaxed text-sm break-words">
              {post.texto}
            </p>
            
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between text-xs text-gray-500 gap-2">
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-1">
                  <MessageCircle className="w-3 h-3" />
                  <span>{post.comentarios.length}</span>
                </div>
              </div>
              
              <div className="flex items-center space-x-2 flex-wrap">
                <div className="flex items-center space-x-1">
                  <Calendar className="w-3 h-3" />
                  <span>{formatDate(post.fecha)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Botón para expandir comentarios */}
        {post.comentarios.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center justify-between w-full text-left px-3 py-2 text-sm font-medium text-gray-700 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
            >
              <div className="flex items-center space-x-2 min-w-0">
                <MessageCircle className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">
                  {post.comentarios.length} comentario{post.comentarios.length !== 1 ? 's' : ''}
                </span>
                <div className={`${getSentimentConfig(post.sentimiento_comentarios).bg} ${getSentimentConfig(post.sentimiento_comentarios).color} px-2 py-1 rounded-full text-xs whitespace-nowrap`}>
                  {getSentimentConfig(post.sentimiento_comentarios).label}
                </div>
              </div>
              {isExpanded ? (
                <ChevronUp className="w-4 h-4 flex-shrink-0" />
              ) : (
                <ChevronDown className="w-4 h-4 flex-shrink-0" />
              )}
            </button>
          </div>
        )}
      </div>

      {/* Comentarios expandibles */}
      {isExpanded && post.comentarios.length > 0 && (
        <div className="border-t border-gray-100 bg-gray-50">
          <div className="p-4">
            <h5 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <MessageCircle className="w-4 h-4 mr-2" />
              Comentarios ({post.comentarios.length})
            </h5>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {post.comentarios.map((comentario, index) => {
                const commentSentiment = getSentimentConfig(comentario.sentimiento_comentario);
                return (
                  <div key={comentario.id_comentario} className="bg-white rounded-lg p-3 border border-gray-200">
                    <div className="flex items-start space-x-3">
                      <img
                        src={`https://ui-avatars.com/api/?name=Usuario${index + 1}&background=random&size=32`}
                        alt={`Usuario ${index + 1}`}
                        className="w-8 h-8 rounded-full object-cover flex-shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-1 gap-1">
                          <div className="flex items-center space-x-2 min-w-0">
                            <span className="text-sm font-medium text-gray-800 truncate">
                              Usuario {index + 1}
                            </span>
                            <div className="bg-gray-500 text-white text-xs px-2 py-1 rounded-full whitespace-nowrap">
                              Comentario
                            </div>
                          </div>
                          <div className="flex items-center space-x-1 flex-shrink-0">
                            <div className={`${commentSentiment.bg} ${commentSentiment.color} px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap`}>
                              {commentSentiment.label}
                            </div>
                            <span className="text-xs text-gray-500 whitespace-nowrap">
                              {Math.round(comentario.confianza_comentario * 100)}%
                            </span>
                          </div>
                        </div>
                        <p className="text-sm text-gray-700 leading-relaxed break-words">
                          {comentario.texto_comentario}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* Resumen de comentarios */}
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between text-xs text-gray-600 gap-1">
                <span>Sentimiento promedio de comentarios:</span>
                <div className="flex items-center space-x-2">
                  <div className={`${getSentimentConfig(post.sentimiento_comentarios).bg} ${getSentimentConfig(post.sentimiento_comentarios).color} px-2 py-1 rounded-full font-medium whitespace-nowrap`}>
                    {getSentimentConfig(post.sentimiento_comentarios).label}
                  </div>
                  <span className="whitespace-nowrap">({Math.round(post.confianza_comentarios * 100)}% confianza)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
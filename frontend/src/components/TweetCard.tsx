import React, { useState } from 'react';
import { MessageCircle, Calendar, ChevronDown, ChevronUp } from 'lucide-react';

interface Comment {
  id_comentario: string;
  texto_comentario: string;
  sentimiento_comentario: string;
  confianza_comentario: number;
}

interface Post {
  id_post: string;
  candidato: string;
  usuario: string; // <--- AGREGADO: Necesario para mostrar al autor real
  texto: string;
  sentimiento_publicacion: string;
  confianza_publicacion: number;
  comentarios: Comment[];
  sentimiento_comentarios: string;
  confianza_comentarios: number;
  sentimiento_final: string;
  confianza_final: number;
  fecha?: string;
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

  const getSentimentConfig = (sentiment: string) => {
    const config = sentimentConfig[sentiment as keyof typeof sentimentConfig];
    return config || sentimentConfig['NEU'];
  };

  const postSentiment = getSentimentConfig(post.sentimiento_publicacion);
  const finalSentiment = getSentimentConfig(post.sentimiento_final);

  // Parseo seguro de fecha
  const formatDate = (fechaStr?: string): string => {
    if (!fechaStr) return new Date().toLocaleDateString('es-EC');
    try {
        const fecha = new Date(fechaStr);
        return isNaN(fecha.getTime()) ? fechaStr : fecha.toLocaleDateString('es-EC');
    } catch { return fechaStr; }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all duration-200 w-full mb-4">
      <div className="p-4">
        <div className="flex items-start space-x-3">
          {/* Avatar del USUARIO (no del candidato) */}
          <img
            src={`https://ui-avatars.com/api/?name=${encodeURIComponent(post.usuario || 'Anónimo')}&background=random&size=48`}
            alt={post.usuario}
            className="w-10 h-10 rounded-full object-cover flex-shrink-0"
          />
          
          <div className="flex-1 min-w-0">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2 gap-2">
              <div className="flex items-center space-x-2 min-w-0">
                {/* Nombre del USUARIO real */}
                <h4 className="font-semibold text-gray-900 truncate text-sm">
                  {post.usuario}
                </h4>
                {/* Etiqueta del Candidato sobre el que se habla */}
                <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded-full truncate">
                   Sobre: {post.candidato}
                </span>
              </div>
              
              {/* Badges de Sentimiento */}
              <div className="flex items-center space-x-1 flex-shrink-0">
                <div className={`${postSentiment.bg} ${postSentiment.color} px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap`}>
                  Post: {postSentiment.label}
                </div>
                <div className={`${finalSentiment.bg} ${finalSentiment.color} px-2 py-1 rounded-full text-xs font-medium border whitespace-nowrap`}>
                  Global: {finalSentiment.label}
                </div>
              </div>
            </div>
            
            {/* Texto del Post (Ahora sí debería aparecer) */}
            <p className="text-gray-800 mb-3 leading-relaxed text-sm break-words whitespace-pre-wrap">
              {post.texto}
            </p>
            
            <div className="flex items-center text-xs text-gray-500 gap-4">
               <div className="flex items-center space-x-1">
                  <MessageCircle className="w-3 h-3" />
                  <span>{post.comentarios.length}</span>
               </div>
               <div className="flex items-center space-x-1">
                  <Calendar className="w-3 h-3" />
                  <span>{formatDate(post.fecha)}</span>
               </div>
            </div>
          </div>
        </div>

        {/* Botón de comentarios (Misma lógica anterior) */}
        {post.comentarios.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center justify-between w-full text-left px-3 py-2 text-sm font-medium text-gray-700 bg-gray-50 rounded-lg hover:bg-gray-100"
            >
              <span>Ver {post.comentarios.length} comentarios</span>
              {isExpanded ? <ChevronUp className="w-4 h-4"/> : <ChevronDown className="w-4 h-4"/>}
            </button>
          </div>
        )}
      </div>

      {/* Lista de comentarios */}
      {isExpanded && (
        <div className="border-t border-gray-100 bg-gray-50 p-4 space-y-3">
            {post.comentarios.map((com, idx) => {
                const sentiment = getSentimentConfig(com.sentimiento_comentario);
                return (
                    <div key={com.id_comentario || idx} className="bg-white p-3 rounded-lg border border-gray-200">
                        <div className="flex justify-between items-start">
                             <p className="text-sm text-gray-800">{com.texto_comentario}</p>
                             <span className={`${sentiment.bg} ${sentiment.color} text-xs px-2 py-0.5 rounded-full`}>
                                {sentiment.label}
                             </span>
                        </div>
                    </div>
                );
            })}
        </div>
      )}
    </div>
  );
};
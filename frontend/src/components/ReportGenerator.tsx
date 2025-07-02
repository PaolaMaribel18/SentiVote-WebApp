import React, { useState } from 'react';
import { Download, FileText, MessageSquare, Plus } from 'lucide-react';
import { SentimentAnalysis } from '../types';

interface ReportGeneratorProps {
  analysis: SentimentAnalysis | null;
  backendPosts?: any[]; // Agregar los posts del backend como prop opcional
}

export const ReportGenerator: React.FC<ReportGeneratorProps> = ({ analysis, backendPosts = [] }) => {
  const [comments, setComments] = useState<string[]>(analysis?.comments || []);
  const [newComment, setNewComment] = useState('');

  const addComment = () => {
    if (newComment.trim()) {
      setComments([...comments, newComment.trim()]);
      setNewComment('');
    }
  };

  const generateReport = () => {
    if (!analysis) return;

    // Calcular estadísticas más precisas
    const totalPosts = backendPosts.length;
    const totalComments = backendPosts.reduce((total, post) => total + (post.comentarios?.length || 0), 0);
    const totalAnalysisItems = analysis.summary.total; // Publicaciones + comentarios analizados
    
    // Obtener candidatos únicos
    const uniqueCandidates = [...new Set(backendPosts.map(post => post.candidato))];

    const reportData = {
      // Información de la consulta
      query: analysis.query,
      createdAt: analysis.createdAt,
      
      // Estadísticas detalladas
      statistics: {
        totalPosts: totalPosts,
        totalComments: totalComments,
        totalAnalysisItems: totalAnalysisItems,
        uniqueCandidates: uniqueCandidates.length,
        candidatesList: uniqueCandidates
      },
      
      // Resumen de sentimientos
      sentimentSummary: {
        positive: {
          count: analysis.summary.positive,
          percentage: Math.round((analysis.summary.positive / analysis.summary.total) * 100)
        },
        negative: {
          count: analysis.summary.negative,
          percentage: Math.round((analysis.summary.negative / analysis.summary.total) * 100)
        },
        neutral: {
          count: analysis.summary.neutral,
          percentage: Math.round((analysis.summary.neutral / analysis.summary.total) * 100)
        }
      },
      
      // Análisis por candidato (si hay datos del backend)
      candidateAnalysis: backendPosts.length > 0 ? generateCandidateAnalysis(backendPosts) : null,
      
      // Palabras clave
      wordClouds: analysis.wordClouds,
      
      // Comentarios del analista
      analystComments: comments,
      
      // Metadata
      reportMetadata: {
        generatedAt: new Date().toISOString(),
        reportVersion: '1.0',
        totalDataPoints: totalAnalysisItems
      }
    };

    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analisis-sentimientos-${analysis.query.replace(/\s+/g, '-')}-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Función helper para generar análisis por candidato
  const generateCandidateAnalysis = (posts: any[]) => {
    const candidateStats: { [key: string]: any } = {};
    
    posts.forEach(post => {
      const candidato = post.candidato || 'Sin candidato';
      
      if (!candidateStats[candidato]) {
        candidateStats[candidato] = {
          totalPosts: 0,
          totalComments: 0,
          sentiments: {
            posts: { POS: 0, NEG: 0, NEU: 0 },
            comments: { POS: 0, NEG: 0, NEU: 0 },
            final: { POS: 0, NEG: 0, NEU: 0 }
          },
          avgConfidence: {
            posts: 0,
            comments: 0,
            final: 0
          }
        };
      }
      
      const stats = candidateStats[candidato];
      stats.totalPosts++;
      stats.totalComments += post.comentarios?.length || 0;
      
      // Contar sentimientos de posts
      stats.sentiments.posts[post.sentimiento_publicacion] = 
        (stats.sentiments.posts[post.sentimiento_publicacion] || 0) + 1;
      
      // Contar sentimientos finales
      stats.sentiments.final[post.sentimiento_final] = 
        (stats.sentiments.final[post.sentimiento_final] || 0) + 1;
      
      // Contar sentimientos de comentarios
      post.comentarios?.forEach((comment: any) => {
        stats.sentiments.comments[comment.sentimiento_comentario] = 
          (stats.sentiments.comments[comment.sentimiento_comentario] || 0) + 1;
      });
    });
    
    return candidateStats;
  };

  if (!analysis) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="text-center text-gray-500">
          <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>Realiza un análisis para generar reportes</p>
        </div>
      </div>
    );
  }

  // Calcular estadísticas corregidas para mostrar
  const totalPosts = backendPosts.length;
  const totalComments = backendPosts.reduce((total, post) => total + (post.comentarios?.length || 0), 0);
  const uniqueCandidates = [...new Set(backendPosts.map(post => post.candidato))].length;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-6 flex items-center">
        <FileText className="w-5 h-5 mr-2" />
        Generar Reporte
      </h3>

      {/* Comentarios */}
      <div className="mb-6">
        <h4 className="text-md font-medium text-gray-700 mb-3 flex items-center">
          <MessageSquare className="w-4 h-4 mr-2" />
          Comentarios y Observaciones
        </h4>
        
        <div className="space-y-3 mb-4">
          {comments.map((comment, index) => (
            <div key={index} className="bg-gray-50 p-3 rounded-lg">
              <p className="text-gray-700">{comment}</p>
            </div>
          ))}
        </div>

        <div className="flex space-x-2">
          <input
            type="text"
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Agregar comentario o observación..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            onKeyPress={(e) => e.key === 'Enter' && addComment()}
          />
          <button
            onClick={addComment}
            disabled={!newComment.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Resumen del reporte CORREGIDO */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h4 className="font-medium text-gray-700 mb-2">Resumen del Reporte:</h4>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Consulta: "{analysis.query}"</li>
          <li>• Publicaciones analizadas: <strong>{totalPosts}</strong></li>
          <li>• Comentarios analizados: <strong>{totalComments}</strong></li>
          <li>• Total de elementos analizados: <strong>{analysis.summary.total}</strong></li>
          <li>• Candidatos únicos: <strong>{uniqueCandidates}</strong></li>
          <li>• Observaciones incluidas: <strong>{comments.length}</strong></li>
          <li>• Fecha de análisis: <strong>{new Date(analysis.createdAt).toLocaleDateString('es-EC')}</strong></li>
        </ul>
        
        {/* Resumen de sentimientos */}
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-sm font-medium text-gray-700 mb-2">Distribución de Sentimientos:</p>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="bg-green-100 text-green-800 p-2 rounded text-center">
              <div className="font-semibold">Positivos</div>
              <div>{analysis.summary.positive} ({Math.round((analysis.summary.positive / analysis.summary.total) * 100)}%)</div>
            </div>
            <div className="bg-red-100 text-red-800 p-2 rounded text-center">
              <div className="font-semibold">Negativos</div>
              <div>{analysis.summary.negative} ({Math.round((analysis.summary.negative / analysis.summary.total) * 100)}%)</div>
            </div>
            <div className="bg-gray-100 text-gray-800 p-2 rounded text-center">
              <div className="font-semibold">Neutrales</div>
              <div>{analysis.summary.neutral} ({Math.round((analysis.summary.neutral / analysis.summary.total) * 100)}%)</div>
            </div>
          </div>
        </div>
      </div>

      <button
        onClick={generateReport}
        className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-3 px-6 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 focus:ring-4 focus:ring-green-300 transition-all duration-200 flex items-center justify-center"
      >
        <Download className="w-5 h-5 mr-2" />
        Descargar Reporte Completo
      </button>
    </div>
  );
};
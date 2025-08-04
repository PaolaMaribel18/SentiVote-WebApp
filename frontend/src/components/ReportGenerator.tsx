import React, { useState } from 'react';
import { Download, FileText, MessageSquare, Plus } from 'lucide-react';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { SentimentAnalysis } from '../types';
import logo from '../assets/logo.png';

interface ReportGeneratorProps {
  analysis: SentimentAnalysis | null;
  backendPosts?: any[];
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

    const doc = new jsPDF();
    const img = new Image();
    img.src = logo;

    img.onload = () => {
      const pageWidth = doc.internal.pageSize.getWidth();

      const logoWidth = 20;
      const logoHeight = 20;
      const logoX = pageWidth - logoWidth - 20;
      const logoY = 20;

      doc.addImage(img, 'PNG', logoX, logoY, logoWidth, logoHeight);

      doc.setFontSize(16);
      doc.setTextColor(33, 33, 33);
      doc.text("SentiVoteEc - Reporte de Análisis Sociopolítico", 20, 28);

      doc.setFontSize(10);
      doc.setTextColor(100);
      doc.text("Plataforma de análisis de sentimiento político en redes sociales", 20, 35);

      doc.setDrawColor(200);
      doc.line(20, 42, pageWidth - 20, 42);

      let y = 52;
      doc.setTextColor(0);
      doc.setFontSize(12);
      doc.text(`Consulta: ${analysis.query}`, 14, y);
      y += 8;
      doc.text(`Fecha de generación: ${new Date().toLocaleString()}`, 14, y);
      y += 8;

      doc.text("Estadísticas Generales:", 14, y);
      y += 4;

      autoTable(doc, {
        startY: y,
        head: [["Indicador", "Valor"]],
        body: [
          ["Publicaciones Analizadas", backendPosts.length],
          ["Comentarios Analizados", backendPosts.reduce((total, post) => total + (post.comentarios?.length || 0), 0)],
          ["Elementos Totales Analizados", analysis.summary.total],
          ["Candidatos Únicos", [...new Set(backendPosts.map(post => post.candidato))].length]
        ]
      });

      const yStartSent = doc.lastAutoTable.finalY + 10;
      doc.text("Distribución de Sentimientos:", 14, yStartSent);
      autoTable(doc, {
        startY: yStartSent + 4,
        head: [["Sentimiento", "Cantidad", "%"]],
        body: [
          ["Positivo", analysis.summary.positive, Math.round((analysis.summary.positive / analysis.summary.total) * 100) + "%"],
          ["Negativo", analysis.summary.negative, Math.round((analysis.summary.negative / analysis.summary.total) * 100) + "%"],
          ["Neutral", analysis.summary.neutral, Math.round((analysis.summary.neutral / analysis.summary.total) * 100) + "%"]
        ]
      });

      const yStartConclusion = doc.lastAutoTable.finalY + 10;
      if (analysis.conclusion) {
        doc.setFontSize(12);
        doc.text("Conclusión del Sistema:", 14, yStartConclusion);
        doc.setFontSize(11);
        const splitText = doc.splitTextToSize(analysis.conclusion, 180);
        doc.text(splitText, 14, yStartConclusion + 8);
        doc.setFontSize(9);
        doc.setTextColor(100);
        doc.text("* Esta conclusión fue generada automáticamente por un modelo de lenguaje (Gemini Flash 2.0).", 14, yStartConclusion + 8 + splitText.length * 6 + 4);
        doc.setTextColor(0);
      }

      const canvas = document.createElement('canvas');
      canvas.width = 400;
      canvas.height = 200;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        const barColors = ['#34D399', '#F87171', '#A3A3A3'];
        const values = [analysis.summary.positive, analysis.summary.negative, analysis.summary.neutral];
        const total = values.reduce((a, b) => a + b, 0);

        ctx.fillStyle = '#000';
        ctx.font = '12px sans-serif';
        const labels = ['Positivos', 'Negativos', 'Neutrales'];

        values.forEach((val, i) => {
          const barWidth = (val / total) * 300;
          ctx.fillStyle = barColors[i];
          ctx.fillRect(100, 30 + i * 30, barWidth, 20);
          ctx.fillStyle = '#000';
          ctx.fillText(labels[i], 10, 45 + i * 30);
          ctx.fillText(`${val} (${Math.round((val / total) * 100)}%)`, 100 + barWidth + 5, 45 + i * 30);
        });

        const image = canvas.toDataURL('image/png');
        doc.addPage();
        doc.setFontSize(14);
        doc.text("Gráfico de Sentimientos", 14, 20);
        doc.addImage(image, 'PNG', 15, 30, 180, 90);
      }

      if (comments.length > 0) {
        doc.addPage();
        doc.setFontSize(14);
        doc.text("Comentarios del Analista", 14, 20);
        comments.forEach((comment, i) => {
          doc.setFontSize(11);
          doc.text(`• ${comment}`, 14, 30 + i * 8);
        });
      }

      const pageHeight = doc.internal.pageSize.getHeight();
      const pageWidth2 = doc.internal.pageSize.getWidth();
      doc.setFontSize(9);
      doc.setTextColor(120);
      doc.text(`Reporte generado automáticamente el ${new Date().toLocaleString('es-EC')}`, pageWidth2 / 2, pageHeight - 10, { align: 'center' });

      doc.save(`reporte_${analysis.query.replace(/\s+/g, '_')}.pdf`);
    };
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

  const totalPosts = backendPosts.length;
  const totalComments = backendPosts.reduce((total, post) => total + (post.comentarios?.length || 0), 0);
  const uniqueCandidates = [...new Set(backendPosts.map(post => post.candidato))].length;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-6 flex items-center">
        <FileText className="w-5 h-5 mr-2" />
        Generar Reporte
      </h3>

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
        Descargar Reporte Completo (PDF)
      </button>
    </div>
  );
};

import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface SentimentCardProps {
  type: 'positive' | 'negative' | 'neutral';
  count: number;
  percentage: number;
  uniqueUsers: number;
}

export const SentimentCard: React.FC<SentimentCardProps> = ({ 
  type, 
  count, 
  percentage, 
  uniqueUsers 
}) => {
  const config = {
    positive: {
      icon: TrendingUp,
      color: 'text-green-600',
      bg: 'bg-green-50',
      border: 'border-green-200',
      label: 'Positivo'
    },
    negative: {
      icon: TrendingDown,
      color: 'text-red-600',
      bg: 'bg-red-50',
      border: 'border-red-200',
      label: 'Negativo'
    },
    neutral: {
      icon: Minus,
      color: 'text-gray-600',
      bg: 'bg-gray-50',
      border: 'border-gray-200',
      label: 'Neutral'
    }
  };

  const { icon: Icon, color, bg, border, label } = config[type];

  return (
    <div className={`${bg} ${border} border rounded-xl p-6 hover:shadow-md transition-shadow duration-200`}>
      <div className="flex items-center justify-between mb-4">
        <div className={`${color} flex items-center`}>
          <Icon className="w-6 h-6 mr-2" />
          <h3 className="text-lg font-semibold">{label}</h3>
        </div>
        <div className={`${color} text-2xl font-bold`}>
          {percentage.toFixed(1)}%
        </div>
      </div>
      
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Publicaciones:</span>
          <span className="font-semibold text-gray-900">{count}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Usuarios únicos:</span>
          <span className="font-semibold text-gray-900">{uniqueUsers}</span>
        </div>
      </div>
    </div>
  );
};
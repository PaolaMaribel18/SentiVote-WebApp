import React from 'react';

interface SentimentChartProps {
  data: {
    positive: number;
    negative: number;
    neutral: number;
  };
}

export const SentimentChart: React.FC<SentimentChartProps> = ({ data }) => {
  const total = data.positive + data.negative + data.neutral;
  
  const percentages = {
    positive: (data.positive / total) * 100,
    negative: (data.negative / total) * 100,
    neutral: (data.neutral / total) * 100
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-6">Distribución de Sentimientos</h3>
      
      {/* Gráfico de barras */}
      <div className="space-y-4 mb-6">
        <div className="flex items-center">
          <div className="w-20 text-sm font-medium text-gray-600">Positivo</div>
          <div className="flex-1 bg-gray-200 rounded-full h-4 mx-3">
            <div
              className="bg-green-500 h-4 rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${percentages.positive}%` }}
            ></div>
          </div>
          <div className="w-16 text-sm font-semibold text-green-600">
            {percentages.positive.toFixed(1)}%
          </div>
        </div>
        
        <div className="flex items-center">
          <div className="w-20 text-sm font-medium text-gray-600">Negativo</div>
          <div className="flex-1 bg-gray-200 rounded-full h-4 mx-3">
            <div
              className="bg-red-500 h-4 rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${percentages.negative}%` }}
            ></div>
          </div>
          <div className="w-16 text-sm font-semibold text-red-600">
            {percentages.negative.toFixed(1)}%
          </div>
        </div>
        
        <div className="flex items-center">
          <div className="w-20 text-sm font-medium text-gray-600">Neutral</div>
          <div className="flex-1 bg-gray-200 rounded-full h-4 mx-3">
            <div
              className="bg-gray-500 h-4 rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${percentages.neutral}%` }}
            ></div>
          </div>
          <div className="w-16 text-sm font-semibold text-gray-600">
            {percentages.neutral.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Gráfico circular */}
      <div className="flex justify-center">
        <div className="relative w-48 h-48">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="8"
            />
            
            {/* Positivo */}
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="#10b981"
              strokeWidth="8"
              strokeDasharray={`${percentages.positive * 2.51} 251.2`}
              strokeDashoffset="0"
              className="transition-all duration-1000 ease-out"
            />
            
            {/* Negativo */}
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="#ef4444"
              strokeWidth="8"
              strokeDasharray={`${percentages.negative * 2.51} 251.2`}
              strokeDashoffset={`-${percentages.positive * 2.51}`}
              className="transition-all duration-1000 ease-out"
            />
            
            {/* Neutral */}
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="#6b7280"
              strokeWidth="8"
              strokeDasharray={`${percentages.neutral * 2.51} 251.2`}
              strokeDashoffset={`-${(percentages.positive + percentages.negative) * 2.51}`}
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-800">{total}</div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
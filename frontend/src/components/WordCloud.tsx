import React from 'react';
import { WordCloudItem } from '../types';

interface WordCloudProps {
  words: WordCloudItem[];
  title: string;
  sentiment: 'positive' | 'negative' | 'neutral';
}

export const WordCloud: React.FC<WordCloudProps> = ({ words, title, sentiment }) => {
  const sentimentColors = {
    positive: ['text-green-600', 'text-green-500', 'text-green-700'],
    negative: ['text-red-600', 'text-red-500', 'text-red-700'],
    neutral: ['text-gray-600', 'text-gray-500', 'text-gray-700']
  };

  const getWordSize = (frequency: number, maxFreq: number) => {
    const normalizedSize = (frequency / maxFreq) * 3 + 1;
    return `${normalizedSize}rem`;
  };

  const maxFrequency = Math.max(...words.map(w => w.frequency));
  const colors = sentimentColors[sentiment];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
      <div className="flex flex-wrap gap-2 items-center justify-center min-h-[200px] p-4">
        {words.map((word, index) => (
          <span
            key={word.word}
            className={`font-bold cursor-pointer hover:opacity-75 transition-opacity duration-200 ${
              colors[index % colors.length]
            }`}
            style={{
              fontSize: getWordSize(word.frequency, maxFrequency),
              transform: `rotate(${Math.random() * 20 - 10}deg)`
            }}
            title={`${word.word}: ${word.frequency} menciones`}
          >
            {word.word}
          </span>
        ))}
      </div>
    </div>
  );
};
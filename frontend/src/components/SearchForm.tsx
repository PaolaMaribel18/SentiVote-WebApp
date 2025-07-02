import React, { useState } from 'react';
import { Search, Calendar, Filter, Loader2 } from 'lucide-react';
import { SearchFilters } from '../types';

interface SearchFormProps {
  onSearch: (filters: SearchFilters) => void;
  isLoading: boolean;
}

export const SearchForm: React.FC<SearchFormProps> = ({ onSearch, isLoading }) => {
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    platforms: ['twitter', 'facebook', 'instagram'],
    dateFrom: '',
    dateTo: '',
    minEngagement: 0
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (filters.query.trim()) {
      onSearch(filters);
    }
  };

  const handlePlatformToggle = (platform: 'twitter' | 'facebook' | 'instagram') => {
    setFilters(prev => ({
      ...prev,
      platforms: prev.platforms.includes(platform)
        ? prev.platforms.filter(p => p !== platform)
        : [...prev.platforms, platform]
    }));
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="query" className="block text-sm font-semibold text-gray-700 mb-2">
            Consulta o Palabra Clave
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              id="query"
              value={filters.query}
              onChange={(e) => setFilters(prev => ({ ...prev, query: e.target.value }))}
              placeholder="Ej: Guillermo Lasso, correísmo, reforma tributaria..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <Calendar className="inline w-4 h-4 mr-1" />
              Fecha Desde
            </label>
            <input
              type="date"
              value={filters.dateFrom}
              onChange={(e) => setFilters(prev => ({ ...prev, dateFrom: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <Calendar className="inline w-4 h-4 mr-1" />
              Fecha Hasta
            </label>
            <input
              type="date"
              value={filters.dateTo}
              onChange={(e) => setFilters(prev => ({ ...prev, dateTo: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <Filter className="inline w-4 h-4 mr-1" />
              Engagement Mínimo
            </label>
            <input
              type="number"
              value={filters.minEngagement}
              onChange={(e) => setFilters(prev => ({ ...prev, minEngagement: parseInt(e.target.value) || 0 }))}
              min="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-3">Redes Sociales</label>
          <div className="flex flex-wrap gap-3">
            {[
              { key: 'twitter' as const, label: 'Twitter', color: 'bg-blue-100 text-blue-800' },
              { key: 'facebook' as const, label: 'Facebook', color: 'bg-indigo-100 text-indigo-800' },
              { key: 'instagram' as const, label: 'Instagram', color: 'bg-pink-100 text-pink-800' }
            ].map(({ key, label, color }) => (
              <button
                key={key}
                type="button"
                onClick={() => handlePlatformToggle(key)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                  filters.platforms.includes(key)
                    ? color
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading || !filters.query.trim()}
          className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 focus:ring-4 focus:ring-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center"
        >
          {isLoading ? (
            <>
              <Loader2 className="animate-spin w-5 h-5 mr-2" />
              Analizando...
            </>
          ) : (
            <>
              <Search className="w-5 h-5 mr-2" />
              Iniciar Análisis
            </>
          )}
        </button>
      </form>
    </div>
  );
};
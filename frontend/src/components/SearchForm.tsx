import React, { useState } from 'react';
import { Search, Calendar, Loader2, ArrowRight } from 'lucide-react';
import { SearchFilters } from '../types';
import { CorpusDateRange } from '../App';

interface SearchFormProps {
  onSearch: (filters: SearchFilters) => void;
  isLoading: boolean;
  dateRange: CorpusDateRange;
}

export const SearchForm: React.FC<SearchFormProps> = ({ onSearch, isLoading, dateRange }) => {
  // Inicializamos con valores vacíos, pero respetando la interfaz
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    dateFrom: '',
    dateTo: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (filters.query.trim()) {
      onSearch(filters);
    }
  };

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 mb-10 transform transition-all hover:shadow-2xl">
      <form onSubmit={handleSubmit} className="space-y-6">
        
        {/* --- Campo de Búsqueda Principal --- */}
        <div>
          <label htmlFor="query" className="block text-sm font-bold text-gray-700 mb-2 ml-1">
            ¿Qué deseas analizar?
          </label>
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
            </div>
            <input
              type="text"
              id="query"
              value={filters.query}
              onChange={(e) => setFilters(prev => ({ ...prev, query: e.target.value }))}
              placeholder="Ej: Daniel Noboa, Seguridad, Elecciones..."
              className="block w-full pl-11 pr-4 py-4 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 focus:bg-white transition-all duration-200 text-lg shadow-sm"
              required
            />
          </div>
        </div>

        {/* --- Filtros de Fecha (Grid ajustado) --- */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Fecha Desde */}
          <div className="relative group">
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 ml-1">
              Fecha Inicio
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Calendar className="h-5 w-5 text-gray-400 group-focus-within:text-purple-500 transition-colors" />
              </div>
              <input
                type="date"
                value={filters.dateFrom || ''}
                onChange={(e) => setFilters(prev => ({ ...prev, dateFrom: e.target.value }))}
                min={dateRange.minString}
                max={dateRange.maxString}
                className="block w-full pl-10 pr-3 py-3 bg-gray-50 border border-gray-200 rounded-lg text-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 focus:bg-white transition-all duration-200 sm:text-sm shadow-sm"
              />
            </div>
          </div>

          {/* Fecha Hasta */}
          <div className="relative group">
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 ml-1">
              Fecha Fin
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Calendar className="h-5 w-5 text-gray-400 group-focus-within:text-purple-500 transition-colors" />
              </div>
              <input
                type="date"
                value={filters.dateTo || ''}
                onChange={(e) => setFilters(prev => ({ ...prev, dateTo: e.target.value }))}
                min={dateRange.minString}
                max={dateRange.maxString}
                className="block w-full pl-10 pr-3 py-3 bg-gray-50 border border-gray-200 rounded-lg text-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 focus:bg-white transition-all duration-200 sm:text-sm shadow-sm"
              />
            </div>
          </div>
        </div>

        {/* --- Botón de Acción --- */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={isLoading || !filters.query.trim()}
            className={`
              w-full flex items-center justify-center py-4 px-6 rounded-xl text-white font-bold text-lg shadow-lg transform transition-all duration-200
              ${isLoading || !filters.query.trim() 
                ? 'bg-gray-300 cursor-not-allowed opacity-70' 
                : 'bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:scale-[1.01] hover:shadow-xl active:scale-[0.99]'}
            `}
          >
            {isLoading ? (
              <>
                <Loader2 className="animate-spin w-6 h-6 mr-2" />
                <span className="tracking-wide">Analizando datos...</span>
              </>
            ) : (
              <>
                <Search className="w-5 h-5 mr-2" />
                <span>Iniciar Análisis</span>
                <ArrowRight className="w-5 h-5 ml-2 opacity-70" />
              </>
            )}
          </button>
        </div>

      </form>
    </div>
  );
};
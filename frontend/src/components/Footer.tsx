import React from 'react';
import { BarChart3, Github, Twitter, Mail, Heart } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Marca / Logo */}
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold text-gray-900">SentimientoElectoral</span>
            </div>
            <p className="text-gray-500 text-sm leading-relaxed max-w-xs">
              Plataforma de análisis de sentimientos políticos en tiempo real para el Ecuador, impulsada por IA y minería de datos.
            </p>
          </div>

          {/* Enlaces Rápidos */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              Navegación
            </h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-gray-500 hover:text-indigo-600 transition-colors text-sm">
                  Metodología
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-500 hover:text-indigo-600 transition-colors text-sm">
                  Sobre el Proyecto
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-500 hover:text-indigo-600 transition-colors text-sm">
                  Términos de Uso
                </a>
              </li>
            </ul>
          </div>

          {/* Contacto y Redes */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              Conecta con nosotros
            </h3>
            <div className="flex gap-4">
               <a href="#" className="p-2 bg-gray-50 rounded-full text-gray-400 hover:text-blue-500 hover:bg-blue-50 transition-all">
                 <Twitter className="w-5 h-5" />
               </a>
               <a href="#" className="p-2 bg-gray-50 rounded-full text-gray-400 hover:text-gray-900 hover:bg-gray-100 transition-all">
                 <Github className="w-5 h-5" />
               </a>
               <a href="#" className="p-2 bg-gray-50 rounded-full text-gray-400 hover:text-red-500 hover:bg-red-50 transition-all">
                 <Mail className="w-5 h-5" />
               </a>
            </div>
          </div>
        </div>
        
        {/* Copyright */}
        <div className="border-t border-gray-100 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-gray-500">
            © {new Date().getFullYear()} SentimientoElectoral. Todos los derechos reservados.
          </p>
          <div className="flex items-center text-sm text-gray-500 gap-1">
            <span>Hecho con</span>
            <Heart className="w-4 h-4 text-red-500 fill-current" />
            <span>en Ecuador</span>
          </div>
        </div>
      </div>
    </footer>
  );
}